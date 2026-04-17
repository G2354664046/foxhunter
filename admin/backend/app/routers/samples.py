from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_admin
from app.models.admin_user import AdminUser
from app.models.sample import Sample
from app.schemas.common import Message
from app.schemas.sample import SampleCreate, SampleOut, SampleUpdate

router = APIRouter(prefix="/samples", tags=["samples"])


@router.get("", response_model=dict)
def list_samples(
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None, description="文件名或哈希"),
    user_id: int | None = None,
    status: str | None = None,
):
    q = db.query(Sample)
    if user_id is not None:
        q = q.filter(Sample.user_id == user_id)
    if status:
        q = q.filter(Sample.status == status)
    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.filter(or_(Sample.filename.like(kw), Sample.hash.like(kw)))
    total = q.count()
    items = (
        q.order_by(Sample.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "items": [SampleOut.model_validate(s) for s in items]}


@router.get("/{sample_id}", response_model=SampleOut)
def get_sample(
    sample_id: int,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    s = db.query(Sample).filter(Sample.id == sample_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="样本不存在")
    return s


@router.post("", response_model=SampleOut)
def create_sample(
    payload: SampleCreate,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    s = Sample(**payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.put("/{sample_id}", response_model=SampleOut)
def update_sample(
    sample_id: int,
    payload: SampleUpdate,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    s = db.query(Sample).filter(Sample.id == sample_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="样本不存在")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{sample_id}", response_model=Message)
def delete_sample(
    sample_id: int,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    s = db.query(Sample).filter(Sample.id == sample_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="样本不存在")
    db.delete(s)
    db.commit()
    return Message(message="已删除")
