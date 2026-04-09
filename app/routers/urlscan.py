import requests
from fastapi import APIRouter, HTTPException
from app.config import settings

router = APIRouter()


@router.get("/url/scan")
def scan_url(url: str):
    """
    使用 URLhaus API 对 URL 进行检测。
    需在 foxhunter/.env 配置 URLHAUS_API_KEY（https://auth.abuse.ch/ 申请 Auth-Key）。
    """
    if not url:
        raise HTTPException(status_code=400, detail="请提供要检测的 URL")

    if not settings.urlhaus_api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "未配置有效的 URLHAUS_API_KEY。请在 https://auth.abuse.ch/ 申请 Auth-Key，"
                "写入 foxhunter/.env 后重启 uvicorn。"
            ),
        )

    headers = {"Auth-Key": settings.urlhaus_api_key}

    try:
        resp = requests.post(
            "https://urlhaus-api.abuse.ch/v1/url/",
            data={"url": url},
            headers=headers,
            timeout=15,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail=f"无法连接 URLhaus：{exc}",
        )

    if resp.status_code != 200:
        detail = f"URLhaus 返回 HTTP {resp.status_code}"
        try:
            err = resp.json()
            if isinstance(err, dict) and err.get("query_status"):
                detail = f"URLhaus：{err.get('query_status')} — {err}"
        except ValueError:
            pass
        raise HTTPException(status_code=502, detail=detail)

    try:
        data = resp.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="URLhaus 返回非 JSON 数据")

    return {"url": url, "provider": "URLhaus", "raw_result": data}
