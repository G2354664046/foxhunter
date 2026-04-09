from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json

from app.auth import get_current_user
from app.database import get_db
from app.models.cnn_detection_result import CnnDetectionResult
from app.models.sample import Sample
from app.models.user import User

router = APIRouter()

@router.get("/result/{sample_id}")
async def get_result(
    sample_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Validate ID
    try:
        sample_id = int(sample_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sample ID")

    sample = db.query(Sample).filter(Sample.id == sample_id, Sample.user_id == user.id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    cnn_row = (
        db.query(CnnDetectionResult)
        .filter(CnnDetectionResult.sample_id == sample.id)
        .order_by(CnnDetectionResult.id.desc())
        .first()
    )

    parsed_result = sample.result_json
    if parsed_result is None and sample.result:
        try:
            parsed_result = json.loads(sample.result)
        except Exception:
            parsed_result = sample.result

    return {
        "id": sample.id,
        "filename": sample.filename,
        "status": sample.status,
        "result": parsed_result,
        "cnn_csv_row": (
            {
                "image_name": cnn_row.image_name,
                "predicted": cnn_row.predicted_index,
                "predicted_label": cnn_row.predicted_label,
                "prob": cnn_row.probability,
                "is_malware": cnn_row.is_malware,
                "weights_path": cnn_row.weights_path,
            }
            if cnn_row
            else None
        ),
        "created_at": sample.created_at,
        "updated_at": sample.updated_at,
    }