from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_admin
from app.models.admin_user import AdminUser
from app.models.cnn_result import CnnDetectionResult
from app.schemas.common import Message
from app.schemas.cnn_result import CnnResultCreate, CnnResultOut, CnnResultUpdate

router = APIRouter(prefix="/cnn-results", tags=["cnn-results"])


@router.get("", response_model=dict)
def list_results(
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sample_id: int | None = None,
    keyword: str | None = Query(None, description="图片名或标签"),
):
    q = db.query(CnnDetectionResult)
    if sample_id is not None:
        q = q.filter(CnnDetectionResult.sample_id == sample_id)
    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.filter(
            or_(
                CnnDetectionResult.image_name.like(kw),
                CnnDetectionResult.predicted_label.like(kw),
            )
        )
    total = q.count()
    items = (
        q.order_by(CnnDetectionResult.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "items": [CnnResultOut.model_validate(r) for r in items]}


@router.get("/{result_id}", response_model=CnnResultOut)
def get_result(
    result_id: int,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    r = db.query(CnnDetectionResult).filter(CnnDetectionResult.id == result_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="记录不存在")
    return r


@router.post("", response_model=CnnResultOut)
def create_result(
    payload: CnnResultCreate,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    r = CnnDetectionResult(**payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.put("/{result_id}", response_model=CnnResultOut)
def update_result(
    result_id: int,
    payload: CnnResultUpdate,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    r = db.query(CnnDetectionResult).filter(CnnDetectionResult.id == result_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="记录不存在")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{result_id}", response_model=Message)
def delete_result(
    result_id: int,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    r = db.query(CnnDetectionResult).filter(CnnDetectionResult.id == result_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(r)
    db.commit()
    return Message(message="已删除")
