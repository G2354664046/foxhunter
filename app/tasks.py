from celery_app import celery_app
from app.config import settings
from app.database import SessionLocal
from app.models.cnn_detection_result import CnnDetectionResult
from app.models.sample import Sample
from app.services import (
    binary_file_to_gray_image,
    build_file_detection_result,
    predict_cnn,
    scan_file_for_detection,
)
import json
import os


@celery_app.task
def process_sample(sample_id: int, file_path: str):
    db = SessionLocal()
    sample = None
    try:
        sample = db.query(Sample).filter(Sample.id == sample_id).first()
        if not sample:
            return

        sample.status = "processing"
        db.commit()

        vt_summary = scan_file_for_detection(file_path, sample.hash)

        gray_name = f"sample_{sample.id}.png"
        gray_path = binary_file_to_gray_image(
            file_path=file_path,
            out_data_dir=settings.out_data_dir,
            image_name=gray_name,
        )

        cnn_pred = None
        cnn_score = 0.5
        try:
            cnn_pred = predict_cnn(gray_path)
            cnn_score = float(cnn_pred["probability"])
            cnn_pred["status"] = "ok"
        except Exception as cnn_exc:
            # CNN 失败时不中断整条检测链路，保留 VT 结果。
            cnn_pred = {
                "status": "error",
                "task_type": "family_classification",
                "error": str(cnn_exc),
                "is_malware": True,
                "weights_path": "",
            }

        result = build_file_detection_result(
            cnn_score,
            vt_summary,
            cnn_detail=cnn_pred,
            gray_image_path=gray_path,
        )

        if "predicted_index" in cnn_pred and "probability" in cnn_pred:
            db.add(
                CnnDetectionResult(
                    sample_id=sample.id,
                    image_name=os.path.basename(gray_path),
                    image_path=gray_path,
                    predicted_index=int(cnn_pred["predicted_index"]),
                    predicted_label=str(cnn_pred["predicted_label"]),
                    probability=float(cnn_pred["probability"]),
                    is_malware=bool(cnn_pred["is_malware"]),
                    weights_path=str(cnn_pred.get("weights_path") or ""),
                )
            )

        sample.status = "completed"
        sample.result = json.dumps(result, ensure_ascii=False)
        sample.result_json = result
        db.commit()

        os.remove(file_path)

    except Exception as e:
        if sample is not None:
            sample.status = "failed"
            sample.result = str(e)
            sample.result_json = {"error": str(e)}
            db.commit()
    finally:
        db.close()
