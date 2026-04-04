"""VirusTotal 相关服务（哈希/文件情报等）。"""

from .client import fetch_file_report, scan_file_for_detection

__all__ = ["fetch_file_report", "scan_file_for_detection"]
