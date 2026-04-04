from celery_app import celery_app
from app.database import SessionLocal
from app.models.sample import Sample
from app.services import (
    build_file_detection_result,
    extract_pe_features,
    predict_cnn,
    predict_random_forest,
    scan_file_for_detection,
)
import os
import json


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

        try:
            features = extract_pe_features(file_path)
        except Exception:
            features = {}

        rf_score = predict_random_forest(features)
        cnn_score = predict_cnn(file_path)

        result = build_file_detection_result(rf_score, cnn_score, vt_summary)

        sample.status = "completed"
        sample.result = json.dumps(result, ensure_ascii=False)
        db.commit()

        os.remove(file_path)

    except Exception as e:
        if sample is not None:
            sample.status = "failed"
            sample.result = str(e)
            db.commit()
    finally:
        db.close()
