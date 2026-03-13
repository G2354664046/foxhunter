import requests
from fastapi import APIRouter, HTTPException

from app.config import settings


router = APIRouter()


@router.get("/url/scan")
def scan_url(url: str):
  """
  使用 URLhaus 公共 API 对 URL 进行安全检测。

  URLhaus API 文档: https://urlhaus.abuse.ch/api/
  需要在 .env 中配置 URLHAUS_API_KEY。
  """
  if not url:
      raise HTTPException(status_code=400, detail="URL is required")

  if not settings.urlhaus_api_key:
      raise HTTPException(status_code=503, detail="URLhaus API key not configured")

  headers = {"Auth-Key": settings.urlhaus_api_key}

  try:
      # URLhaus 使用 POST /v1/url/ 接口，表单参数为 url=...
      resp = requests.post(
          "https://urlhaus-api.abuse.ch/v1/url/",
          data={"url": url},
          headers=headers,
          timeout=15,
      )
  except requests.RequestException as exc:
      raise HTTPException(
          status_code=503,
          detail=f"URL scanner service unavailable: {exc}",
      )

  if resp.status_code != 200:
      raise HTTPException(
          status_code=resp.status_code,
          detail=f"URL scanner returned {resp.status_code}",
      )

  try:
      data = resp.json()
  except ValueError:
      raise HTTPException(status_code=502, detail="Invalid JSON from scanner service")

  return {"url": url, "provider": "URLhaus", "raw_result": data}

