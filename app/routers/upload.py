from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import hashlib, os, time

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models.sample import Sample
from app.models.user import User
from app.tasks import process_sample

router = APIRouter()

# ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)

@router.post("/upload")
async def upload_sample(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 读取文件内容
    content = await file.read()

    # 计算文件哈希
    file_hash = hashlib.sha256(content).hexdigest()

    # 如果样本已经存在，直接返回已有记录ID
    existing = (
        db.query(Sample)
        .filter(Sample.user_id == user.id, Sample.hash == file_hash)
        .order_by(Sample.id.desc())
        .first()
    )
    if existing:
        return {
            "task_id": None,
            "message": "Sample already exists",
            "sample_id": existing.id
        }

    # 创建数据库记录
    new_sample = Sample(
        user_id=user.id,
        filename=file.filename,
        hash=file_hash,
        status="pending",
    )
    db.add(new_sample)
    db.commit()
    db.refresh(new_sample)

    # 保存文件到磁盘供worker读取（使用 sample_id 做前缀，避免重名）
    safe_name = os.path.basename(file.filename)
    filename = f"{new_sample.id}_{int(time.time())}_{safe_name}"
    file_path = os.path.join(settings.upload_dir, filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # 异步调度处理
    async_result = process_sample.delay(new_sample.id, file_path)
    new_sample.task_id = async_result.id
    db.commit()


    return {
        "task_id": async_result.id,
        "sample_id": new_sample.id,
        "message": "File uploaded successfully"
    }