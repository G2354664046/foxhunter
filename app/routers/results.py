from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
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

    return {
        "id": sample.id,
        "filename": sample.filename,
        "status": sample.status,
        "result": sample.result,
        "created_at": sample.created_at,
        "updated_at": sample.updated_at,
    }