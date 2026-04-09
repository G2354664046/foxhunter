from datetime import datetime, timezone
import hashlib
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.auth import get_current_user, get_current_user_optional
from app.config import settings
from app.database import get_db
from app.models.sample import Sample
from app.models.user import User
from app.schemas import SampleResponse


router = APIRouter()


class UrlRecordCreate(BaseModel):
    url: str
    result: dict


class HashRecordCreate(BaseModel):
    file_hash: str
    result: dict


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


@router.get("/samples/stats")
def sample_stats(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    """
    实时统计：
    - 已登录：统计当前用户
    - 未登录：统计全站
    """
    query = db.query(Sample)
    if user is not None:
        query = query.filter(Sample.user_id == user.id)

    total_scans = query.count()

    today = datetime.now().date()
    today_scans = (
        query.filter(func.date(Sample.created_at) == today)
        .count()
    )

    pending_scans = (
        query.filter(Sample.status.in_(["pending", "processing"]))
        .count()
    )

    # 通过 result JSON 中顶层 is_malware 统计“发现恶意”
    # 仅在 completed 样本中统计，避免把处理中误判入内。
    completed_rows = query.filter(Sample.status == "completed").all()
    malware_found = 0
    for row in completed_rows:
        payload = row.result_json
        if payload is None and not row.result:
            continue
        try:
            if payload is None:
                payload = json.loads(row.result)
            if bool(payload.get("is_malware")):
                malware_found += 1
        except Exception:
            continue

    # 检测引擎口径：本地模型 2（RF + CNN）+ 外部引擎源（VT / URLhaus）是否可用
    engines = 2
    if settings.virustotal_api_key:
        engines += 1
    if settings.urlhaus_api_key:
        engines += 1

    return {
        "scope": "user" if user is not None else "global",
        "today_scans": today_scans,
        "malware_found": malware_found,
        "pending_scans": pending_scans,
        "total_scans": total_scans,
        "engines": engines,
    }


@router.post("/samples/url-record")
def create_url_record(
    payload: UrlRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    url = (payload.url or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="url is required")

    digest = hashlib.sha256(f"url:{url}:{datetime.now(timezone.utc).timestamp()}".encode("utf-8")).hexdigest()

    sample = Sample(
        user_id=user.id,
        filename=url,
        sample_type="url",
        hash=digest,
        status="completed",
        result=json.dumps(payload.result, ensure_ascii=False),
        result_json=payload.result,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return {"sample_id": sample.id}


@router.post("/samples/hash-record")
def create_hash_record(
    payload: HashRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    file_hash = (payload.file_hash or "").strip().lower()
    if not file_hash:
        raise HTTPException(status_code=400, detail="file_hash is required")

    digest = file_hash if len(file_hash) == 64 else hashlib.sha256(
        f"hash:{file_hash}:{datetime.now(timezone.utc).timestamp()}".encode("utf-8")
    ).hexdigest()

    sample = Sample(
        user_id=user.id,
        filename=file_hash,
        sample_type="hash",
        hash=digest,
        status="completed",
        result=json.dumps(payload.result, ensure_ascii=False),
        result_json=payload.result,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return {"sample_id": sample.id}


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

