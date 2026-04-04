def build_file_detection_result(
    rf_confidence: float,
    cnn_confidence: float,
    virustotal_summary: dict,
) -> dict:
    """
    合并 cxn_random_forest / cxn_cnn 占位分数与 VirusTotal 多引擎摘要。
    若 VT 报恶意引擎数 > 0，综合判定为恶意并提高置信度。
    """
    base = ensemble_prediction(rf_confidence, cnn_confidence)
    out: dict = {
        **base,
        "cxn_models_note": "cxn_random_forest 与 cxn_cnn 当前为占位分数，待接入训练权重。",
        "virustotal": virustotal_summary,
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


def ensemble_prediction(rf_confidence: float, cnn_confidence: float) -> dict:
    """
    Ensemble prediction using weighted voting (RF + CNN).
    """
    weight_rf = 0.6
    weight_cnn = 0.4
    final_score = weight_rf * rf_confidence + weight_cnn * cnn_confidence

    is_malware = final_score > 0.5
    confidence = final_score if is_malware else 1 - final_score

    return {
        "is_malware": is_malware,
        "confidence": confidence,
        "rf_score": rf_confidence,
        "cnn_score": cnn_confidence,
    }
