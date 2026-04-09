def build_file_detection_result(
    cnn_confidence: float,
    virustotal_summary: dict,
    cnn_detail: dict | None = None,
    gray_image_path: str | None = None,
) -> dict:
    """
    合并 cxn_cnn 家族分类结果与 VirusTotal 多引擎摘要。
    若 VT 报恶意引擎数 > 0，综合判定为恶意并提高置信度。
    """
    base = ensemble_prediction(cnn_confidence)
    out: dict = {
        **base,
        "cxn_models_note": "cxn_cnn 用于恶意家族多分类；恶意二分类优先参考 VirusTotal 多引擎结果。",
        "virustotal": virustotal_summary,
        "cnn_detail": cnn_detail or {},
        "gray_image_path": gray_image_path,
        "family_confidence": float(cnn_confidence),
    }
    vt = virustotal_summary or {}
    if not vt.get("configured") or vt.get("status") != "ok":
        return out
    stats = vt.get("stats") or {}
    mal = int(stats.get("malicious_votes", 0))
    total = max(int(stats.get("total_engines", 0)), 1)
    vt_positive = mal > 0
    out["is_malware"] = bool(base["is_malware"]) or vt_positive
    if vt_positive:
        out["confidence"] = max(float(base["confidence"]), min(1.0, mal / total))
    return out


def ensemble_prediction(cnn_confidence: float) -> dict:
    """
    Baseline prediction using CNN family confidence only.
    恶意二分类由 VT 覆盖，故默认基线为安全并保留家族置信度。
    """
    return {
        "is_malware": False,
        "confidence": max(0.0, min(float(cnn_confidence), 1.0)),
        "cnn_score": cnn_confidence,
    }
