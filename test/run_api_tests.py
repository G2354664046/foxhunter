from __future__ import annotations
import argparse
import json
import os
import random
import string
import time
from datetime import datetime
from typing import Any
import requests


def _rand_suffix(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

def _now_str() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def _safe_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return None

def _case_result(
    case_id: str,
    name: str,
    forward: dict[str, Any],
    reverse: dict[str, Any] | list[dict[str, Any]],
) -> dict[str, Any]:
    rev_list: list[dict[str, Any]] = reverse if isinstance(reverse, list) else [reverse]
    fwd_ok = bool(forward.get("passed"))
    rev_ok = all(bool(x.get("passed")) for x in rev_list)
    skipped_rev = any(x.get("skipped") for x in rev_list)
    # 若反向全部跳过，总结果仅看正向
    if skipped_rev and all(x.get("skipped") for x in rev_list):
        overall = fwd_ok
    elif any(x.get("skipped") for x in rev_list):
        overall = fwd_ok and rev_ok
    else:
        overall = fwd_ok and rev_ok

    return {
        "case_id": case_id,
        "name": name,
        "passed": overall,
        "forward": forward,
        "reverse": rev_list if len(rev_list) > 1 else rev_list[0],
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


class TestRunner:
    def __init__(self, base_url: str, timeout: int, wait_seconds: int):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.wait_seconds = wait_seconds
        self.session = requests.Session()
        self.ctx: dict[str, Any] = {
            "token": None,
            "username": None,
            "password": None,
            "sample_id": None,
        }

    def _auth_headers(self) -> dict[str, str]:
        token = self.ctx.get("token")
        return {"Authorization": f"Bearer {token}"} if token else {}

    def run(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        results.append(self._te002_register())
        results.append(self._te001_login())
        results.append(self._te003_me())
        results.append(self._te004_upload())
        results.append(self._te005_result())
        results.append(self._te006_samples())
        results.append(self._te007_delete())
        results.append(self._te008_url_scan())
        results.append(self._te009_hash_scan())
        results.append(self._te010_health())
        # 按 TE001–TE010 排序输出
        order = {f"TE{i:03d}": i for i in range(1, 11)}
        results.sort(key=lambda x: order.get(x["case_id"], 99))
        return results

    def _te002_register(self) -> dict[str, Any]:
        suffix = _rand_suffix()
        username = f"autotest_{suffix}"
        email = f"{username}@example.com"
        password = "Passw0rd123"
        self.ctx["username"] = username
        self.ctx["password"] = password
        url = f"{self.base_url}/api/v1/auth/register"

        fwd: dict[str, Any] = {"label": "正向：新用户注册", "expected_status": 200}
        try:
            resp = self.session.post(
                url,
                json={"username": username, "email": email, "password": password},
                timeout=self.timeout,
            )
            data = _safe_json(resp)
            ok = resp.status_code == 200 and isinstance(data, dict) and data.get("username") == username
            fwd["passed"] = ok
            fwd["actual_status"] = resp.status_code
            fwd["detail"] = "注册成功" if ok else str(data)
        except Exception as exc:
            fwd["passed"] = False
            fwd["actual_status"] = None
            fwd["detail"] = f"请求异常: {exc}"

        rev: dict[str, Any] = {"label": "反向：重复用户名/邮箱", "expected_status": 400}
        try:
            resp2 = self.session.post(
                url,
                json={"username": username, "email": email, "password": password},
                timeout=self.timeout,
            )
            data2 = _safe_json(resp2)
            ok2 = resp2.status_code == 400
            rev["passed"] = ok2
            rev["actual_status"] = resp2.status_code
            rev["detail"] = (data2 or {}).get("detail", str(data2)) if isinstance(data2, dict) else str(data2)
        except Exception as exc:
            rev["passed"] = False
            rev["actual_status"] = None
            rev["detail"] = f"请求异常: {exc}"

        return _case_result("TE002", "用户注册系统用例", fwd, rev)

    def _te001_login(self) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/auth/login"
        u, p = self.ctx.get("username"), self.ctx.get("password")

        fwd: dict[str, Any] = {"label": "正向：正确密码登录", "expected_status": 200}
        if not u or not p:
            fwd["passed"] = False
            fwd["actual_status"] = None
            fwd["detail"] = "缺少注册上下文"
        else:
            try:
                resp = self.session.post(url, data={"username": u, "password": p}, timeout=self.timeout)
                data = _safe_json(resp)
                token = data.get("access_token") if isinstance(data, dict) else None
                if token:
                    self.ctx["token"] = token
                ok = resp.status_code == 200 and isinstance(token, str) and len(token) > 10
                fwd["passed"] = ok
                fwd["actual_status"] = resp.status_code
                fwd["detail"] = "返回JWT" if ok else str(data)
            except Exception as exc:
                fwd["passed"] = False
                fwd["actual_status"] = None
                fwd["detail"] = f"请求异常: {exc}"

        rev: dict[str, Any] = {"label": "反向：错误密码", "expected_status": 401}
        try:
            resp2 = self.session.post(
                url,
                data={"username": u, "password": "wrong_password_123"},
                timeout=self.timeout,
            )
            data2 = _safe_json(resp2)
            ok2 = resp2.status_code == 401
            rev["passed"] = ok2
            rev["actual_status"] = resp2.status_code
            rev["detail"] = (data2 or {}).get("detail", str(data2)) if isinstance(data2, dict) else str(data2)
        except Exception as exc:
            rev["passed"] = False
            rev["actual_status"] = None
            rev["detail"] = f"请求异常: {exc}"

        return _case_result("TE001", "用户登录系统用例", fwd, rev)

    def _te003_me(self) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/auth/me"

        fwd: dict[str, Any] = {"label": "正向：有效Token访问/me", "expected_status": 200}
        if not self.ctx.get("token"):
            fwd["passed"] = False
            fwd["actual_status"] = None
            fwd["detail"] = "无Token"
        else:
            try:
                resp = self.session.get(url, headers=self._auth_headers(), timeout=self.timeout)
                data = _safe_json(resp)
                ok = (
                    resp.status_code == 200
                    and isinstance(data, dict)
                    and data.get("username") == self.ctx.get("username")
                )
                fwd["passed"] = ok
                fwd["actual_status"] = resp.status_code
                fwd["detail"] = "返回当前用户" if ok else str(data)
            except Exception as exc:
                fwd["passed"] = False
                fwd["actual_status"] = None
                fwd["detail"] = f"请求异常: {exc}"

        rev_checks: list[dict[str, Any]] = [
            {"label": "反向：无Token访问/me", "expected_status": 401},
            {"label": "反向：无效Token访问/me", "expected_status": 401},
        ]
        try:
            r1 = self.session.get(url, timeout=self.timeout)
            d1 = _safe_json(r1)
            rev_checks[0]["passed"] = r1.status_code == 401
            rev_checks[0]["actual_status"] = r1.status_code
            rev_checks[0]["detail"] = (d1 or {}).get("detail", str(d1)) if isinstance(d1, dict) else str(d1)
        except Exception as exc:
            rev_checks[0]["passed"] = False
            rev_checks[0]["actual_status"] = None
            rev_checks[0]["detail"] = f"请求异常: {exc}"

        try:
            r2 = self.session.get(
                url,
                headers={"Authorization": "Bearer invalid_token_for_test"},
                timeout=self.timeout,
            )
            d2 = _safe_json(r2)
            rev_checks[1]["passed"] = r2.status_code == 401
            rev_checks[1]["actual_status"] = r2.status_code
            rev_checks[1]["detail"] = (d2 or {}).get("detail", str(d2)) if isinstance(d2, dict) else str(d2)
        except Exception as exc:
            rev_checks[1]["passed"] = False
            rev_checks[1]["actual_status"] = None
            rev_checks[1]["detail"] = f"请求异常: {exc}"

        overall_pass = bool(fwd.get("passed")) and all(c.get("passed") for c in rev_checks)
        return {
            "case_id": "TE003",
            "name": "获取当前用户信息用例",
            "passed": overall_pass,
            "forward": fwd,
            "reverse": rev_checks,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    def _te004_upload(self) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/upload"

        fwd: dict[str, Any] = {"label": "正向：上传.bin", "expected_status": 200}
        if not self.ctx.get("token"):
            fwd["passed"] = False
            fwd["actual_status"] = None
            fwd["detail"] = "未登录"
        else:
            try:
                dummy = os.urandom(256)
                files = {"file": ("autotest_sample.bin", dummy, "application/octet-stream")}
                resp = self.session.post(url, files=files, headers=self._auth_headers(), timeout=self.timeout)
                data = _safe_json(resp)
                sid = data.get("sample_id") if isinstance(data, dict) else None
                if sid:
                    self.ctx["sample_id"] = int(sid)
                ok = resp.status_code == 200 and bool(sid)
                fwd["passed"] = ok
                fwd["actual_status"] = resp.status_code
                fwd["detail"] = f"sample_id={sid}" if ok else str(data)
            except Exception as exc:
                fwd["passed"] = False
                fwd["actual_status"] = None
                fwd["detail"] = f"请求异常: {exc}"

        rev: dict[str, Any] = {"label": "反向：上传非法扩展名", "expected_status": 400}
        if not self.ctx.get("token"):
            rev["passed"] = False
            rev["actual_status"] = None
            rev["detail"] = "未登录"
        else:
            try:
                files2 = {"file": ("bad.txt", b"not a bin", "text/plain")}
                resp2 = self.session.post(url, files=files2, headers=self._auth_headers(), timeout=self.timeout)
                data2 = _safe_json(resp2)
                ok2 = resp2.status_code == 400
                rev["passed"] = ok2
                rev["actual_status"] = resp2.status_code
                rev["detail"] = (data2 or {}).get("detail", str(data2)) if isinstance(data2, dict) else str(data2)
            except Exception as exc:
                rev["passed"] = False
                rev["actual_status"] = None
                rev["detail"] = f"请求异常: {exc}"

        return _case_result("TE004", "样本文件上传并触发异步检测用例", fwd, rev)

    def _te005_result(self) -> dict[str, Any]:
        sid = self.ctx.get("sample_id")
        fwd: dict[str, Any] = {"label": "正向：查询有效样本结果", "expected_status": 200}
        if not self.ctx.get("token") or not sid:
            fwd["passed"] = False
            fwd["actual_status"] = None
            fwd["detail"] = "缺少token或sample_id"
        else:
            try:
                time.sleep(min(self.wait_seconds, 3))
                url = f"{self.base_url}/api/v1/result/{sid}"
                resp = self.session.get(url, headers=self._auth_headers(), timeout=self.timeout)
                data = _safe_json(resp)
                ok = resp.status_code == 200 and isinstance(data, dict) and "status" in data
                fwd["passed"] = ok
                fwd["actual_status"] = resp.status_code
                fwd["detail"] = f"status={data.get('status')}" if ok else str(data)
            except Exception as exc:
                fwd["passed"] = False
                fwd["actual_status"] = None
                fwd["detail"] = f"请求异常: {exc}"

        rev: dict[str, Any] = {"label": "反向：查询不存在ID", "expected_status": 404}
        if not self.ctx.get("token"):
            rev["passed"] = False
            rev["actual_status"] = None
            rev["detail"] = "未登录"
        else:
            try:
                url2 = f"{self.base_url}/api/v1/result/99999999"
                resp2 = self.session.get(url2, headers=self._auth_headers(), timeout=self.timeout)
                data2 = _safe_json(resp2)
                ok2 = resp2.status_code == 404
                rev["passed"] = ok2
                rev["actual_status"] = resp2.status_code
                rev["detail"] = (data2 or {}).get("detail", str(data2)) if isinstance(data2, dict) else str(data2)
            except Exception as exc:
                rev["passed"] = False
                rev["actual_status"] = None
                rev["detail"] = f"请求异常: {exc}"

        return _case_result("TE005", "查询单个样本检测结果用例", fwd, rev)

    def _te006_samples(self) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/samples"

        fwd: dict[str, Any] = {"label": "正向：有效Token列表", "expected_status": 200}
        if not self.ctx.get("token"):
            fwd["passed"] = False
            fwd["actual_status"] = None
            fwd["detail"] = "未登录"
        else:
            try:
                resp = self.session.get(url, headers=self._auth_headers(), timeout=self.timeout)
                data = _safe_json(resp)
                ok = resp.status_code == 200 and isinstance(data, list)
                fwd["passed"] = ok
                fwd["actual_status"] = resp.status_code
                fwd["detail"] = f"共{len(data)}条" if ok else str(data)
            except Exception as exc:
                fwd["passed"] = False
                fwd["actual_status"] = None
                fwd["detail"] = f"请求异常: {exc}"

        rev_checks: list[dict[str, Any]] = [
            {"label": "反向：无Token", "expected_status": 401},
            {"label": "反向：无效Token", "expected_status": 401},
        ]
        try:
            r1 = self.session.get(url, timeout=self.timeout)
            d1 = _safe_json(r1)
            rev_checks[0]["passed"] = r1.status_code == 401
            rev_checks[0]["actual_status"] = r1.status_code
            rev_checks[0]["detail"] = (d1 or {}).get("detail", str(d1)) if isinstance(d1, dict) else str(d1)
        except Exception as exc:
            rev_checks[0]["passed"] = False
            rev_checks[0]["actual_status"] = None
            rev_checks[0]["detail"] = f"请求异常: {exc}"
        try:
            r2 = self.session.get(
                url,
                headers={"Authorization": "Bearer invalid_token_for_test"},
                timeout=self.timeout,
            )
            d2 = _safe_json(r2)
            rev_checks[1]["passed"] = r2.status_code == 401
            rev_checks[1]["actual_status"] = r2.status_code
            rev_checks[1]["detail"] = (d2 or {}).get("detail", str(d2)) if isinstance(d2, dict) else str(d2)
        except Exception as exc:
            rev_checks[1]["passed"] = False
            rev_checks[1]["actual_status"] = None
            rev_checks[1]["detail"] = f"请求异常: {exc}"

        overall = bool(fwd.get("passed")) and all(c.get("passed") for c in rev_checks)
        return {
            "case_id": "TE006",
            "name": "查询当前用户样本记录列表用例",
            "passed": overall,
            "forward": fwd,
            "reverse": rev_checks,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    def _te007_delete(self) -> dict[str, Any]:
        sid = self.ctx.get("sample_id")

        rev: dict[str, Any] = {"label": "反向：删除不存在ID", "expected_status": 404}
        if not self.ctx.get("token"):
            rev["passed"] = False
            rev["actual_status"] = None
            rev["detail"] = "未登录"
        else:
            try:
                url_bad = f"{self.base_url}/api/v1/samples/99999999"
                resp0 = self.session.delete(url_bad, headers=self._auth_headers(), timeout=self.timeout)
                d0 = _safe_json(resp0)
                rev["passed"] = resp0.status_code == 404
                rev["actual_status"] = resp0.status_code
                rev["detail"] = (d0 or {}).get("detail", str(d0)) if isinstance(d0, dict) else str(d0)
            except Exception as exc:
                rev["passed"] = False
                rev["actual_status"] = None
                rev["detail"] = f"请求异常: {exc}"

        fwd: dict[str, Any] = {"label": "正向：删除有效样本", "expected_status": "204或200"}
        if not self.ctx.get("token") or not sid:
            fwd["passed"] = False
            fwd["actual_status"] = None
            fwd["detail"] = "缺少token或sample_id"
        else:
            try:
                url_ok = f"{self.base_url}/api/v1/samples/{sid}"
                resp = self.session.delete(url_ok, headers=self._auth_headers(), timeout=self.timeout)
                ok = resp.status_code in (200, 204)
                fwd["passed"] = ok
                fwd["actual_status"] = resp.status_code
                fwd["detail"] = "删除成功" if ok else _safe_json(resp)
            except Exception as exc:
                fwd["passed"] = False
                fwd["actual_status"] = None
                fwd["detail"] = f"请求异常: {exc}"

        overall = bool(fwd.get("passed")) and bool(rev.get("passed"))
        return {
            "case_id": "TE007",
            "name": "删除指定样本记录用例",
            "passed": overall,
            "forward": fwd,
            "reverse": rev,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    def _te008_url_scan(self) -> dict[str, Any]:
        base = f"{self.base_url}/api/v1/url/scan"

        fwd: dict[str, Any] = {"label": "正向：非空url", "expected_status": "200或503降级"}
        try:
            resp = self.session.get(base, params={"url": "http://example.com"}, timeout=self.timeout)
            data = _safe_json(resp)
            if resp.status_code == 503:
                fwd["passed"] = True
                fwd["actual_status"] = 503
                fwd["detail"] = "未配置URLHAUS_API_KEY，可接受降级"
                fwd["acceptable_degraded"] = True
            else:
                ok = resp.status_code == 200 and isinstance(data, dict)
                fwd["passed"] = ok
                fwd["actual_status"] = resp.status_code
                fwd["detail"] = "URLhaus返回" if ok else str(data)
                fwd["acceptable_degraded"] = False
        except Exception as exc:
            fwd["passed"] = False
            fwd["actual_status"] = None
            fwd["detail"] = f"请求异常: {exc}"

        rev: dict[str, Any] = {"label": "反向：url为空", "expected_status": 400}
        try:
            resp2 = self.session.get(base, params={"url": ""}, timeout=self.timeout)
            data2 = _safe_json(resp2)
            ok2 = resp2.status_code == 400
            rev["passed"] = ok2
            rev["actual_status"] = resp2.status_code
            rev["detail"] = (data2 or {}).get("detail", str(data2)) if isinstance(data2, dict) else str(data2)
        except Exception as exc:
            rev["passed"] = False
            rev["actual_status"] = None
            rev["detail"] = f"请求异常: {exc}"

        r = _case_result("TE008", "URL安全检测用例", fwd, rev)
        if fwd.get("acceptable_degraded"):
            r["acceptable_degraded"] = True
        return r

    def _te009_hash_scan(self) -> dict[str, Any]:
        base = f"{self.base_url}/api/v1/hash/scan"
        md5_eicar = "44d88612fea8a8f36de82e1278abb02f"

        fwd: dict[str, Any] = {"label": "正向：非空file_hash", "expected_status": "200或503降级"}
        try:
            resp = self.session.get(base, params={"file_hash": md5_eicar}, timeout=self.timeout)
            data = _safe_json(resp)
            if resp.status_code == 503:
                fwd["passed"] = True
                fwd["actual_status"] = 503
                fwd["detail"] = "未配置VIRUSTOTAL_API_KEY，可接受降级"
                fwd["acceptable_degraded"] = True
            else:
                ok = resp.status_code == 200 and isinstance(data, dict)
                fwd["passed"] = ok
                fwd["actual_status"] = resp.status_code
                fwd["detail"] = "VT返回" if ok else str(data)
                fwd["acceptable_degraded"] = False
        except Exception as exc:
            fwd["passed"] = False
            fwd["actual_status"] = None
            fwd["detail"] = f"请求异常: {exc}"

        rev: dict[str, Any] = {"label": "反向：file_hash为空", "expected_status": 400}
        try:
            resp2 = self.session.get(base, params={"file_hash": ""}, timeout=self.timeout)
            data2 = _safe_json(resp2)
            ok2 = resp2.status_code == 400
            rev["passed"] = ok2
            rev["actual_status"] = resp2.status_code
            rev["detail"] = (data2 or {}).get("detail", str(data2)) if isinstance(data2, dict) else str(data2)
        except Exception as exc:
            rev["passed"] = False
            rev["actual_status"] = None
            rev["detail"] = f"请求异常: {exc}"

        r = _case_result("TE009", "文件Hash情报查询用例", fwd, rev)
        if fwd.get("acceptable_degraded"):
            r["acceptable_degraded"] = True
        return r

    def _te010_health(self) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/health"

        fwd: dict[str, Any] = {"label": "正向：健康检查", "expected_status": 200}
        try:
            resp = self.session.get(url, timeout=self.timeout)
            data = _safe_json(resp)
            ok = resp.status_code == 200 and isinstance(data, dict) and data.get("status") == "healthy"
            fwd["passed"] = ok
            fwd["actual_status"] = resp.status_code
            fwd["detail"] = "healthy" if ok else str(data)
        except Exception as exc:
            fwd["passed"] = False
            fwd["actual_status"] = None
            fwd["detail"] = f"请求异常: {exc}"

        rev: dict[str, Any] = {
            "label": "反向：服务不可用（未自动执行）",
            "expected_status": "连接失败/5xx",
            "skipped": True,
            "passed": True,
            "actual_status": None,
            "detail": "需停止后端或改用错误地址后手动验证；本脚本不自动模拟",
        }

        overall = bool(fwd.get("passed"))
        return {
            "case_id": "TE010",
            "name": "健康检查接口用例",
            "passed": overall,
            "forward": fwd,
            "reverse": rev,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }


def _flatten_reverse(rev: Any) -> list[dict[str, Any]]:
    if rev is None:
        return []
    if isinstance(rev, list):
        return rev
    return [rev]


def write_reports(
    base_url: str,
    results: list[dict[str, Any]],
    output_dir: str,
    basename: str | None,
) -> tuple[str, str, dict[str, Any]]:
    os.makedirs(output_dir, exist_ok=True)
    ts = basename or f"api_test_report_{_now_str()}"
    json_path = os.path.join(output_dir, f"{ts}.json")
    md_path = os.path.join(output_dir, f"{ts}.md")

    total = len(results)
    passed = sum(1 for x in results if x["passed"])
    failed = total - passed
    degraded = sum(1 for x in results if x.get("acceptable_degraded"))

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "base_url": base_url,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "acceptable_degraded": degraded,
            "pass_rate": round((passed / total * 100), 2) if total else 0.0,
        },
        "results": results,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    lines = [
        "# FoxHunter API 自动化测试报告（10条，正向+反向）",
        "",
        f"- 生成时间：{payload['generated_at']}",
        f"- 目标地址：`{base_url}`",
        f"- 用例总数：{total}",
        f"- 通过数量：{passed}",
        f"- 失败数量：{failed}",
        f"- 可接受降级：{degraded}",
        f"- 通过率：{payload['summary']['pass_rate']}%",
        "",
        "## 用例明细",
        "",
        "| 用例ID | 用例名称 | 总结果 | 正向（HTTP） | 反向（HTTP） | 说明 |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        fid = r["case_id"]
        fname = r["name"]
        overall = "通过" if r["passed"] else "失败"
        if r.get("acceptable_degraded"):
            overall = "通过（含外部API降级）"

        fwd = r.get("forward") or {}
        f_st = fwd.get("actual_status")
        f_cell = f"{f_st}" if f_st is not None else "-"
        if fwd.get("acceptable_degraded"):
            f_cell += " 降级"

        rev_list = _flatten_reverse(r.get("reverse"))
        rev_parts = []
        for item in rev_list:
            if item.get("skipped"):
                rev_parts.append("跳过")
            else:
                rev_parts.append(str(item.get("actual_status", "-")))
        rev_cell = " / ".join(rev_parts) if rev_parts else "-"

        detail_bits = []
        if fwd.get("detail"):
            detail_bits.append(f"正向：{fwd.get('detail')}")
        for item in rev_list:
            if item.get("skipped"):
                detail_bits.append(f"反向：{item.get('detail', '')}")
            elif item.get("detail"):
                lbl = (item.get("label") or "").replace("反向：", "").strip()
                detail_bits.append(f"反向（{lbl}）：{item.get('detail')}")
        detail = "；".join(detail_bits)[:500]
        detail = detail.replace("|", "/")

        lines.append(f"| {fid} | {fname} | {overall} | {f_cell} | {rev_cell} | {detail} |")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return json_path, md_path, payload["summary"]


def main() -> None:
    parser = argparse.ArgumentParser(description="FoxHunter API 自动化测试（10条聚合用例）")
    parser.add_argument("--base-url", default="http://localhost:8000", help="后端服务地址")
    parser.add_argument("--timeout", type=int, default=15, help="单请求超时时间（秒）")
    parser.add_argument("--wait-seconds", type=int, default=20, help="等待异步任务窗口（秒）")
    parser.add_argument("--output-dir", default="test/reports", help="报告输出目录")
    parser.add_argument(
        "--basename",
        default=None,
        help="报告文件名（不含扩展名），默认 api_test_report_时间戳；可设为 api_test_report_20260410_025457",
    )
    args = parser.parse_args()

    runner = TestRunner(base_url=args.base_url, timeout=args.timeout, wait_seconds=args.wait_seconds)
    results = runner.run()
    json_path, md_path, summary = write_reports(args.base_url, results, args.output_dir, args.basename)

    print("=== FoxHunter API 自动化测试完成（10条） ===")
    print(f"总计: {summary['total']}  通过: {summary['passed']}  失败: {summary['failed']}  降级: {summary['acceptable_degraded']}")
    print(f"JSON报告: {json_path}")
    print(f"MD报告:   {md_path}")


if __name__ == "__main__":
    main()
