from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Final


SUPPORTED_UPLOAD_EXTENSIONS: Final[set[str]] = {".exe", ".dll", ".bin"}


def is_supported_upload(filename: str) -> bool:
    """检查上传文件扩展名是否在允许列表中。"""
    return Path(filename).suffix.lower() in SUPPORTED_UPLOAD_EXTENSIONS


def save_as_binary_file(
    content: bytes,
    original_filename: str,
    output_dir: str,
    prefix: str | None = None,
) -> dict[str, str | int]:
    """
    将 exe/dll/bin 内容统一保存为二进制文件（.bin）。

    返回信息：
    - output_path: 落盘后的绝对路径
    - output_name: 落盘后的文件名
    - sha256: 文件 sha256
    - size: 字节大小
    """
    if not original_filename:
        raise ValueError("original_filename is required")
    if not is_supported_upload(original_filename):
        raise ValueError("unsupported file type; only .exe/.dll/.bin are allowed")
    if not isinstance(content, (bytes, bytearray)):
        raise ValueError("content must be bytes")

    os.makedirs(output_dir, exist_ok=True)

    source_name = Path(original_filename).stem
    safe_stem = "".join(ch for ch in source_name if ch.isalnum() or ch in {"_", "-", "."}) or "sample"
    if prefix:
        safe_stem = f"{prefix}_{safe_stem}"

    output_name = f"{safe_stem}.bin"
    output_path = os.path.abspath(os.path.join(output_dir, output_name))

    with open(output_path, "wb") as f:
        f.write(content)

    return {
        "output_path": output_path,
        "output_name": output_name,
        "sha256": hashlib.sha256(content).hexdigest(),
        "size": len(content),
    }
