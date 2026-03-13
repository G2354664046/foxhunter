from celery_app import celery_app
from app.database import SessionLocal
from app.models.sample import Sample
from app.services.feature_extraction import extract_pe_features
from app.services.model_inference import (
    ensemble_prediction,
    predict_cnn,
    predict_random_forest,
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

        # Extract features
        features = extract_pe_features(file_path)

        # Predict with models
        rf_score = predict_random_forest(features)
        cnn_score = predict_cnn(file_path)

        # Ensemble
        result = ensemble_prediction(rf_score, cnn_score)

        # Update sample
        sample.status = "completed"
        sample.result = json.dumps(result, ensure_ascii=False)
        db.commit()

        # Clean up file
        os.remove(file_path)

    except Exception as e:
        if sample is not None:
            sample.status = "failed"
            sample.result = str(e)
            db.commit()
    finally:
        db.close()