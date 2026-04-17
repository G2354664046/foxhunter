from __future__ import annotations

import json
import math
import os
import io
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

from app.config import settings

TARGET_SIZE = (256, 256)
_CNN_MODEL = None
_CLASS_INDEX: dict[str, int] | None = None


def _build_cnn(num_classes: int):
    try:
        from tensorflow.keras.layers import Conv2D, Dense, Dropout, Flatten, Input, MaxPooling2D
        from tensorflow.keras.models import Sequential
    except Exception as exc:
        raise RuntimeError(
            "未检测到 tensorflow，请先安装项目依赖后再执行 CNN 检测。"
        ) from exc

    # 与 训练模型malware-classification-CNN-main/scripts/test.py 保持一致
    model = Sequential()
    model.add(Input(shape=(*TARGET_SIZE, 3)))
    model.add(Conv2D(32, kernel_size=(3, 3), activation="relu", padding="same"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(64, kernel_size=(3, 3), activation="relu", padding="same"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(128, kernel_size=(3, 3), activation="relu", padding="same"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(256, kernel_size=(3, 3), activation="relu", padding="same"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(512, kernel_size=(3, 3), activation="relu", padding="same"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(256, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation="softmax"))
    return model


def _resolve_asset_path(p: str) -> str:
    path = Path(p)
    if path.is_absolute():
        return str(path)
    base = Path(__file__).resolve().parents[3]  # foxhunter/
    return str((base / path).resolve())


def _load_class_index() -> dict[str, int]:
    global _CLASS_INDEX
    if _CLASS_INDEX is not None:
        return _CLASS_INDEX
    class_index_path = _resolve_asset_path(settings.cnn_class_index_path)
    if not os.path.isfile(class_index_path):
        raise FileNotFoundError(f"CNN class_index 文件不存在: {class_index_path}")
    with open(class_index_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    _CLASS_INDEX = {str(k): int(v) for k, v in raw.items()}
    return _CLASS_INDEX


def _weights_fallback_keras_path(weights_path: str) -> str | None:
    """
    由 xxx.weights.h5 推断同目录下可能存在的 Keras 全模型文件。
    训练仓库默认会保存 modellozzo_ckpt.keras。
    """
    p = Path(weights_path)
    if p.name.endswith(".weights.h5"):
        candidate = p.with_name("modellozzo_ckpt.keras")
        if candidate.is_file():
            return str(candidate)
    return None


def _export_weights_from_keras(keras_path: str, weights_path: str) -> tuple[bool, str]:
    """
    仅存在 .keras 全模型时，导出为 .weights.h5，便于后续统一按权重加载。
    返回 (成功标记, 失败原因)。
    """
    try:
        from tensorflow.keras.models import load_model

        model = load_model(keras_path)
        Path(weights_path).parent.mkdir(parents=True, exist_ok=True)
        model.save_weights(weights_path)
        return True, ""
    except Exception as exc:
        return False, str(exc)


def _load_weights_from_h5_by_layer_vars(model, h5_file_path: str) -> tuple[bool, str]:
    """
    兼容 Keras 新式 H5 结构（root/layers/<layer_name>/vars/<idx>）。
    按层名手动把 vars 映射给当前 model 的同名层。
    """
    try:
        import h5py
    except Exception as exc:
        return False, f"缺少 h5py 依赖: {exc}"

    loaded_layers = 0
    weighted_layers = 0
    missing = []
    mismatch = []

    try:
        with h5py.File(h5_file_path, "r") as f:
            if "layers" not in f:
                return False, "H5 根节点不含 layers"
            layer_groups = f["layers"]
            for layer in model.layers:
                current = layer.get_weights()
                if not current:
                    continue
                weighted_layers += 1
                lname = layer.name
                if lname not in layer_groups:
                    missing.append(lname)
                    continue
                g = layer_groups[lname]
                if "vars" not in g:
                    missing.append(f"{lname}/vars")
                    continue
                vars_group = g["vars"]
                keys = sorted(vars_group.keys(), key=lambda x: int(x) if str(x).isdigit() else str(x))
                vals = [np.array(vars_group[k]) for k in keys]
                if len(vals) < len(current):
                    mismatch.append(f"{lname}: expect {len(current)}, got {len(vals)}")
                    continue
                try:
                    layer.set_weights(vals[: len(current)])
                    loaded_layers += 1
                except Exception as exc:
                    mismatch.append(f"{lname}: set_weights失败({exc})")
    except Exception as exc:
        return False, f"读取 H5 失败: {exc}"

    if weighted_layers == 0:
        return False, "当前模型无可赋权层"
    if loaded_layers == 0:
        return False, f"未成功加载任何层; missing={missing[:5]}, mismatch={mismatch[:5]}"
    if loaded_layers < weighted_layers:
        return False, f"部分层加载成功 {loaded_layers}/{weighted_layers}; missing={missing[:5]}, mismatch={mismatch[:5]}"
    return True, f"成功加载 {loaded_layers}/{weighted_layers} 层"


def _load_weights_from_keras_archive(model, keras_path: str) -> tuple[bool, str]:
    """
    从 .keras 压缩包中读取 model.weights.h5，并按层名+vars 手动赋权。
    """
    try:
        import h5py
    except Exception as exc:
        return False, f"缺少 h5py 依赖: {exc}"

    try:
        with zipfile.ZipFile(keras_path, "r") as zf:
            if "model.weights.h5" not in zf.namelist():
                return False, ".keras 包内缺少 model.weights.h5"
            raw = zf.read("model.weights.h5")
    except Exception as exc:
        return False, f"读取 .keras 压缩包失败: {exc}"

    loaded_layers = 0
    weighted_layers = 0
    missing = []
    mismatch = []
    try:
        with h5py.File(io.BytesIO(raw), "r") as f:
            if "layers" not in f:
                return False, "model.weights.h5 不含 layers 节点"
            layer_groups = f["layers"]
            for layer in model.layers:
                current = layer.get_weights()
                if not current:
                    continue
                weighted_layers += 1
                lname = layer.name
                if lname not in layer_groups:
                    missing.append(lname)
                    continue
                g = layer_groups[lname]
                if "vars" not in g:
                    missing.append(f"{lname}/vars")
                    continue
                vars_group = g["vars"]
                keys = sorted(vars_group.keys(), key=lambda x: int(x) if str(x).isdigit() else str(x))
                vals = [np.array(vars_group[k]) for k in keys]
                if len(vals) < len(current):
                    mismatch.append(f"{lname}: expect {len(current)}, got {len(vals)}")
                    continue
                try:
                    layer.set_weights(vals[: len(current)])
                    loaded_layers += 1
                except Exception as exc:
                    mismatch.append(f"{lname}: set_weights失败({exc})")
    except Exception as exc:
        return False, f"读取归档内 H5 失败: {exc}"

    if weighted_layers == 0:
        return False, "当前模型无可赋权层"
    if loaded_layers == 0:
        return False, f"未成功加载任何层; missing={missing[:5]}, mismatch={mismatch[:5]}"
    if loaded_layers < weighted_layers:
        return False, f"部分层加载成功 {loaded_layers}/{weighted_layers}; missing={missing[:5]}, mismatch={mismatch[:5]}"
    return True, f"成功加载 {loaded_layers}/{weighted_layers} 层"


def _get_model():
    global _CNN_MODEL
    if _CNN_MODEL is not None:
        return _CNN_MODEL
    class_index = _load_class_index()
    num_classes = len(class_index)
    model = _build_cnn(num_classes=num_classes)
    weights_path = _resolve_asset_path(settings.cnn_weights_path)
    alt_keras = _weights_fallback_keras_path(weights_path)
    export_err = ""
    if not os.path.isfile(weights_path):
        if alt_keras:
            ok, export_err = _export_weights_from_keras(alt_keras, weights_path)
            if not ok:
                # 导出失败时，按“你的模型键值”手动从 .keras 归档赋权
                ok_arch, msg_arch = _load_weights_from_keras_archive(model, alt_keras)
                if ok_arch:
                    _CNN_MODEL = model
                    return _CNN_MODEL
                try:
                    from tensorflow.keras.models import load_model

                    model = load_model(alt_keras)
                    _CNN_MODEL = model
                    return _CNN_MODEL
                except Exception as exc:
                    raise RuntimeError(
                        "CNN 权重文件不存在且 .keras 直接加载失败。"
                        f" weights={weights_path}, keras={alt_keras}, "
                        f"export_error={export_err}, archive_map_error={msg_arch}, keras_load_error={exc}"
                    ) from exc
        else:
            raise FileNotFoundError(
                f"CNN 权重文件不存在: {weights_path}。"
                f"可用 .keras 路径: {alt_keras or '未找到'}"
            )
    # 优先加载同目录完整模型（.keras），可规避部分 .weights.h5 版本兼容问题
    keras_exc: Exception | None = None
    if alt_keras:
        try:
            from tensorflow.keras.models import load_model

            model = load_model(alt_keras)
            _CNN_MODEL = model
            return _CNN_MODEL
        except Exception as exc:
            keras_exc = exc

    try:
        model.load_weights(weights_path)
    except Exception as exc_weights:
        ok_h5, msg_h5 = _load_weights_from_h5_by_layer_vars(model, weights_path)
        if ok_h5:
            _CNN_MODEL = model
            return _CNN_MODEL
        try:
            import tensorflow as tf

            tf_ver = tf.__version__
        except Exception:
            tf_ver = "unknown"
        extra = ""
        if alt_keras:
            if keras_exc is None:
                extra = f"；并且尝试加载 .keras 失败（路径={alt_keras}）"
            else:
                extra = f"；并且加载 .keras 失败: {keras_exc}（路径={alt_keras}）"
        raise RuntimeError(
            "CNN 权重加载失败，请检查训练/推理环境与模型结构是否一致。"
            f" weights={weights_path}, num_classes={num_classes}, tf={tf_ver}. 原始错误: {exc_weights}；"
            f"H5手动映射结果: {msg_h5}{extra}"
        ) from exc_weights
    _CNN_MODEL = model
    return _CNN_MODEL


def _center_crop_or_pad_to_target(image: np.ndarray, target_h: int = 256, target_w: int = 256) -> np.ndarray:
    if image.ndim == 2:
        image = np.expand_dims(image, axis=-1)
    h, w = image.shape[0], image.shape[1]
    c = image.shape[2]

    if h > target_h:
        y0 = (h - target_h) // 2
        image = image[y0 : y0 + target_h, :, :]
        h = target_h
    if w > target_w:
        x0 = (w - target_w) // 2
        image = image[:, x0 : x0 + target_w, :]
        w = target_w

    if h < target_h or w < target_w:
        out = np.zeros((target_h, target_w, c), dtype=image.dtype)
        y0 = (target_h - h) // 2
        x0 = (target_w - w) // 2
        out[y0 : y0 + h, x0 : x0 + w, :] = image
        image = out

    return image


def binary_file_to_gray_image(file_path: str, out_data_dir: str, image_name: str) -> str:
    with open(file_path, "rb") as f:
        raw = np.frombuffer(f.read(), dtype=np.uint8)
    if raw.size == 0:
        raise ValueError("输入文件为空，无法转换灰度图")

    side = int(math.ceil(math.sqrt(raw.size)))
    padded = np.pad(raw, (0, side * side - raw.size), mode="constant", constant_values=0)
    gray = padded.reshape((side, side))
    gray_3ch = np.stack([gray] * 3, axis=-1)
    prepared = _center_crop_or_pad_to_target(gray_3ch, target_h=TARGET_SIZE[0], target_w=TARGET_SIZE[1])
    img = Image.fromarray(prepared.astype(np.uint8), mode="RGB")

    os.makedirs(out_data_dir, exist_ok=True)
    out_path = os.path.abspath(os.path.join(out_data_dir, image_name))
    img.save(out_path)
    return out_path


def predict_cnn(gray_image_path: str) -> dict:
    model = _get_model()
    class_index = _load_class_index()
    index_to_class = {v: k for k, v in class_index.items()}

    img = Image.open(gray_image_path).convert("RGB")
    x = np.asarray(img, dtype=np.uint8)
    x = _center_crop_or_pad_to_target(x, target_h=TARGET_SIZE[0], target_w=TARGET_SIZE[1]).astype(np.float32) / 255.0
    x = np.expand_dims(x, axis=0)

    proba = model.predict(x, verbose=0)[0]
    predicted_index = int(np.argmax(proba))
    probability = float(proba[predicted_index])
    predicted_label = str(index_to_class.get(predicted_index, predicted_index))
    class_probabilities = {
        str(index_to_class.get(i, i)): float(p)
        for i, p in enumerate(proba)
    }
    # 该模型任务是恶意家族分类（1..9），非良恶二分类。
    is_malware = True

    return {
        "predicted_index": predicted_index,
        "predicted_label": predicted_label,
        "probability": probability,
        "class_probabilities": class_probabilities,
        "task_type": "family_classification",
        "is_malware": is_malware,
        "weights_path": _resolve_asset_path(settings.cnn_weights_path),
    }
