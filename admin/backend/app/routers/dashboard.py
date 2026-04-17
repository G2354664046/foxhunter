from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
import httpx

from app.config import settings
from app.database import get_db
from app.deps import get_current_admin
from app.models.admin_user import AdminUser
from app.models.cnn_result import CnnDetectionResult
from app.models.sample import Sample
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(_: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    user_count = db.query(func.count(User.id)).scalar() or 0
    sample_count = db.query(func.count(Sample.id)).scalar() or 0
    cnn_count = db.query(func.count(CnnDetectionResult.id)).scalar() or 0
    pending = db.query(func.count(Sample.id)).filter(Sample.status == "pending").scalar() or 0
    processing = db.query(func.count(Sample.id)).filter(Sample.status == "processing").scalar() or 0
    completed = db.query(func.count(Sample.id)).filter(Sample.status == "completed").scalar() or 0
    failed = db.query(func.count(Sample.id)).filter(Sample.status == "failed").scalar() or 0
    return {
        "users": user_count,
        "samples": sample_count,
        "cnn_results": cnn_count,
        "samples_by_status": {
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "failed": failed,
        },
    }


@router.get("/foxhunter")
def foxhunter_status(_: AdminUser = Depends(get_current_admin)):
    base = settings.foxhunter_api_base.rstrip("/")
    url = f"{base}/api/v1/health"
    try:
        with httpx.Client(timeout=3.0) as client:
            r = client.get(url)
            ok = r.status_code == 200
            body = None
            try:
                body = r.json()
            except Exception:
                body = {"raw": r.text[:500]}
            return {
                "reachable": ok,
                "url": url,
                "status_code": r.status_code,
                "response": body,
            }
    except Exception as e:
        return {
            "reachable": False,
            "url": url,
            "error": str(e),
        }
