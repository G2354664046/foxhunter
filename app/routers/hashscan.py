import requests
from fastapi import APIRouter, HTTPException

from app.config import settings


router = APIRouter()


@router.get("/hash/scan")
def scan_hash(file_hash: str):
    """
    使用 VirusTotal v3 API 根据哈希查询文件检测信息。

    参考文档: https://docs.virustotal.com/reference/file-info
    需要在 .env 中配置 VIRUSTOTAL_API_KEY。
    """
    if not file_hash:
        raise HTTPException(status_code=400, detail="file_hash is required")

    if not settings.virustotal_api_key:
        raise HTTPException(status_code=503, detail="VirusTotal API key not configured")

    headers = {"x-apikey": settings.virustotal_api_key}
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"

    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail=f"VirusTotal service unavailable: {exc}",
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"VirusTotal returned {resp.status_code}",
        )

    try:
        data = resp.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Invalid JSON from VirusTotal")

    return {"hash": file_hash, "provider": "VirusTotal", "raw_result": data}

