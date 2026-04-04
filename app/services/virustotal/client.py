"""
VirusTotal v3 API：按哈希查询、可选上传后轮询分析。

文档: https://docs.virustotal.com/reference/overview
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

from app.config import settings

logger = logging.getLogger(__name__)

VT_API_BASE = "https://www.virustotal.com/api/v3"

# 免费版等常见限制：单文件约 32MB；此处略保守
MAX_UPLOAD_BYTES = 32 * 1024 * 1024


def _headers() -> dict[str, str]:
    key = settings.virustotal_api_key
    if not key:
        raise RuntimeError("VIRUSTOTAL_API_KEY not configured")
    return {"x-apikey": key}


def fetch_file_report(file_hash: str) -> dict[str, Any] | None:
    """
    ``GET /files/{id}``。若文件未收录返回 ``None``（HTTP 404）。
    其他错误抛出 ``requests.HTTPError``。
    """
    url = f"{VT_API_BASE}/files/{file_hash}"
    resp = requests.get(url, headers=_headers(), timeout=30)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def _sum_analysis_stats(stats: dict[str, Any] | None) -> tuple[dict[str, int], int]:
    """返回各类计数及引擎总数（各统计项之和）。"""
    if not stats:
        return {}, 0
    out: dict[str, int] = {}
    for k, v in stats.items():
        try:
            out[str(k)] = int(v)
        except (TypeError, ValueError):
            continue
    total = sum(out.values())
    return out, total


def normalize_file_report(api_json: dict[str, Any], file_hash: str) -> dict[str, Any]:
    """将 VT ``GET /files/{id}`` 的 JSON 转为前端/任务使用的摘要结构。"""
    data = api_json.get("data") or {}
    attr = data.get("attributes") or {}
    stats_raw = attr.get("last_analysis_stats") or {}
    stats_dict, total_engines = _sum_analysis_stats(stats_raw)
    malicious = stats_dict.get("malicious", 0) + stats_dict.get("suspicious", 0)
    permalink = f"https://www.virustotal.com/gui/file/{file_hash}/detection"
    return {
        "configured": True,
        "status": "ok",
        "file_hash": file_hash,
        "stats": {
            **stats_dict,
            "malicious_votes": malicious,
            "total_engines": total_engines,
        },
        "permalink": permalink,
        "last_analysis_date": attr.get("last_analysis_date"),
        "meaningful_name": attr.get("meaningful_name"),
    }


def upload_file_and_get_analysis_id(file_path: str) -> str:
    """
    ``POST /files``，返回 ``analysis`` 的 id，用于轮询 ``GET /analyses/{id}``。
    """
    size = os.path.getsize(file_path)
    if size > MAX_UPLOAD_BYTES:
        raise ValueError(f"文件超过 VirusTotal 上传大小限制（>{MAX_UPLOAD_BYTES} 字节）")

    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        resp = requests.post(
            f"{VT_API_BASE}/files",
            headers=_headers(),
            files=files,
            timeout=300,
        )
    resp.raise_for_status()
    body = resp.json()
    aid = (body.get("data") or {}).get("id")
    if not aid:
        raise RuntimeError(f"VirusTotal 上传响应缺少 analysis id: {body!r}")
    return str(aid)


def poll_analysis_until_complete(analysis_id: str, timeout_sec: int = 120, interval: float = 2.0) -> dict[str, Any]:
    """轮询 ``GET /analyses/{id}`` 直到 completed 或超时。"""
    url = f"{VT_API_BASE}/analyses/{analysis_id}"
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        resp = requests.get(url, headers=_headers(), timeout=30)
        resp.raise_for_status()
        body = resp.json()
        status = ((body.get("data") or {}).get("attributes") or {}).get("status")
        if status == "completed":
            return body
        if status == "failed":
            raise RuntimeError("VirusTotal 分析失败")
        time.sleep(interval)
    raise TimeoutError("VirusTotal 分析超时")


def scan_file_for_detection(file_path: str, sha256_hex: str) -> dict[str, Any]:
    """
    文件检测主入口：先按 SHA256 查库；若无记录则上传并轮询，再拉取文件报告。

    未配置 API Key 时返回 ``configured: False``，不抛错。
    """
    if not settings.virustotal_api_key:
        return {
            "configured": False,
            "status": "not_configured",
            "message": "未配置 VIRUSTOTAL_API_KEY，已跳过 VirusTotal。",
        }

    sha256_hex = sha256_hex.lower().strip()
    try:
        report = fetch_file_report(sha256_hex)
        if report is not None:
            return normalize_file_report(report, sha256_hex)

        logger.info("VirusTotal 库中无此哈希，尝试上传: %s", sha256_hex[:16])
        analysis_id = upload_file_and_get_analysis_id(file_path)
        poll_analysis_until_complete(analysis_id)
        report2 = None
        for _ in range(10):
            report2 = fetch_file_report(sha256_hex)
            if report2 is not None:
                break
            time.sleep(2)
        if report2 is None:
            return {
                "configured": True,
                "status": "error",
                "error": "上传并分析后仍无法获取文件报告",
                "file_hash": sha256_hex,
            }
        return normalize_file_report(report2, sha256_hex)
    except requests.RequestException as e:
        logger.exception("VirusTotal HTTP 错误")
        err_body = ""
        if isinstance(e, requests.HTTPError) and e.response is not None:
            err_body = e.response.text or ""
        return {
            "configured": True,
            "status": "error",
            "error": err_body or str(e),
            "file_hash": sha256_hex,
        }
    except Exception as e:
        logger.exception("VirusTotal 扫描失败")
        return {
            "configured": True,
            "status": "error",
            "error": str(e),
            "file_hash": sha256_hex,
        }


