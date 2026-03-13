from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_user_optional
from app.database import get_db
from app.models.sample import Sample
from app.models.user import User
from app.schemas import SampleResponse


router = APIRouter()


@router.get("/samples", response_model=List[SampleResponse])
def list_samples(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[Sample]:
    """列出当前登录用户的样本记录，按创建时间倒序。"""
    samples = (
        db.query(Sample)
        .filter(Sample.user_id == user.id)
        .order_by(Sample.created_at.desc())
        .all()
    )
    return samples


@router.get("/samples/recent")
def recent_samples(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    """最近检测动态：

    - 未登录：返回全站最近 5 条样本，用户名做部分脱敏
    - 已登录：返回当前用户最近 5 条样本
    """

    def mask_username(raw: str) -> str:
        if not raw:
            return ""
        if len(raw) <= 2:
            return raw[0] + "*" * (len(raw) - 1)
        return raw[0] + "*" * (len(raw) - 2) + raw[-1]

    query = db.query(Sample)

    # 已登录：只看自己的样本
    if user is not None:
        query = query.filter(Sample.user_id == user.id)

    samples = (
        query.order_by(Sample.created_at.desc())
        .limit(5)
        .all()
    )

    items = []
    for s in samples:
        username = s.user.username if s.user else ""
        if user is None:
            username = mask_username(username)
        # 已登录可以看到自己的完整用户名

        items.append(
            {
                "id": s.id,
                "filename": s.filename,
                "status": s.status,
                "created_at": s.created_at,
                "username": username,
            }
        )

    return {"items": items}


@router.delete("/samples/{sample_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sample(
    sample_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    """删除当前用户的一条样本记录。"""
    try:
        sample_id = int(sample_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sample ID")

    sample = (
        db.query(Sample)
        .filter(Sample.id == sample_id, Sample.user_id == user.id)
        .first()
    )
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    db.delete(sample)
    db.commit()

