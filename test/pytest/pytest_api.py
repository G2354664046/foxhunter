from __future__ import annotations

import os
import uuid
from typing import Any

import httpx
import pytest


def _rand_suffix() -> str:
    return uuid.uuid4().hex[:8]


def _safe_json(resp: httpx.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return None


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("FOXHUNTER_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture(scope="session")
def timeout_seconds() -> float:
    return float(os.getenv("FOXHUNTER_TIMEOUT", "20"))


@pytest.fixture()
def client(timeout_seconds: float) -> httpx.Client:
    with httpx.Client(timeout=timeout_seconds) as c:
        yield c


@pytest.fixture()
def user_payload() -> dict[str, str]:
    suffix = _rand_suffix()
    return {
        "username": f"autotest_{suffix}",
        "email": f"autotest_{suffix}@example.com",
        "password": "Passw0rd123",
    }


@pytest.fixture()
def registered_user(client: httpx.Client, base_url: str, user_payload: dict[str, str]) -> dict[str, str]:
    resp = client.post(f"{base_url}/api/v1/auth/register", json=user_payload)
    assert resp.status_code == 200, f"注册失败: {resp.status_code}, body={_safe_json(resp)}"
    data = resp.json()
    assert data["username"] == user_payload["username"]
    return user_payload


@pytest.fixture()
def auth_token(client: httpx.Client, base_url: str, registered_user: dict[str, str]) -> str:
    resp = client.post(
        f"{base_url}/api/v1/auth/login",
        data={"username": registered_user["username"], "password": registered_user["password"]},
    )
    assert resp.status_code == 200, f"登录失败: {resp.status_code}, body={_safe_json(resp)}"
    token = resp.json().get("access_token")
    assert isinstance(token, str) and len(token) > 10
    return token


@pytest.fixture()
def auth_headers(auth_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture()
def uploaded_sample_id(client: httpx.Client, base_url: str, auth_headers: dict[str, str]) -> int:
    files = {
        "file": (
            f"autotest_{_rand_suffix()}.bin",
            os.urandom(512),
            "application/octet-stream",
        )
    }
    resp = client.post(f"{base_url}/api/v1/upload", files=files, headers=auth_headers)
    assert resp.status_code == 200, f"上传失败: {resp.status_code}, body={_safe_json(resp)}"
    data = resp.json()
    assert "sample_id" in data and data["sample_id"]
    return int(data["sample_id"])


def test_te010_health(base_url: str, client: httpx.Client) -> None:
    resp = client.get(f"{base_url}/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "healthy"


def test_te002_register_success_and_duplicate(base_url: str, client: httpx.Client, user_payload: dict[str, str]) -> None:
    resp = client.post(f"{base_url}/api/v1/auth/register", json=user_payload)
    assert resp.status_code == 200
    assert resp.json().get("username") == user_payload["username"]

    resp_dup = client.post(f"{base_url}/api/v1/auth/register", json=user_payload)
    assert resp_dup.status_code == 400


@pytest.mark.parametrize(
    ("wrong_password", "expected_status"),
    [
        ("wrong_password_123", 401),
    ],
)
def test_te001_login_success_and_wrong_password(
    base_url: str,
    client: httpx.Client,
    registered_user: dict[str, str],
    wrong_password: str,
    expected_status: int,
) -> None:
    ok_resp = client.post(
        f"{base_url}/api/v1/auth/login",
        data={"username": registered_user["username"], "password": registered_user["password"]},
    )
    assert ok_resp.status_code == 200
    assert ok_resp.json().get("access_token")

    bad_resp = client.post(
        f"{base_url}/api/v1/auth/login",
        data={"username": registered_user["username"], "password": wrong_password},
    )
    assert bad_resp.status_code == expected_status


def test_te003_me_auth_cases(
    base_url: str,
    client: httpx.Client,
    registered_user: dict[str, str],
    auth_headers: dict[str, str],
) -> None:
    ok_resp = client.get(f"{base_url}/api/v1/auth/me", headers=auth_headers)
    assert ok_resp.status_code == 200
    assert ok_resp.json().get("username") == registered_user["username"]

    no_token_resp = client.get(f"{base_url}/api/v1/auth/me")
    assert no_token_resp.status_code == 401

    invalid_token_resp = client.get(
        f"{base_url}/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_for_test"},
    )
    assert invalid_token_resp.status_code == 401


def test_te004_upload_valid_and_invalid_ext(
    base_url: str,
    client: httpx.Client,
    auth_headers: dict[str, str],
) -> None:
    ok_files = {
        "file": (
            f"autotest_{_rand_suffix()}.bin",
            os.urandom(512),
            "application/octet-stream",
        )
    }
    ok_resp = client.post(f"{base_url}/api/v1/upload", files=ok_files, headers=auth_headers)
    assert ok_resp.status_code == 200
    assert ok_resp.json().get("sample_id")

    bad_files = {"file": ("bad.txt", b"not_a_bin", "text/plain")}
    bad_resp = client.post(f"{base_url}/api/v1/upload", files=bad_files, headers=auth_headers)
    assert bad_resp.status_code == 400


def test_te005_result_valid_and_not_found(
    base_url: str,
    client: httpx.Client,
    auth_headers: dict[str, str],
    uploaded_sample_id: int,
) -> None:
    ok_resp = client.get(f"{base_url}/api/v1/result/{uploaded_sample_id}", headers=auth_headers)
    assert ok_resp.status_code == 200
    body = ok_resp.json()
    assert body.get("id") == uploaded_sample_id
    assert "status" in body

    bad_resp = client.get(f"{base_url}/api/v1/result/99999999", headers=auth_headers)
    assert bad_resp.status_code == 404


def test_te006_samples_list_auth_cases(
    base_url: str,
    client: httpx.Client,
    auth_headers: dict[str, str],
    uploaded_sample_id: int,
) -> None:
    ok_resp = client.get(f"{base_url}/api/v1/samples", headers=auth_headers)
    assert ok_resp.status_code == 200
    body = ok_resp.json()
    assert isinstance(body, list)
    assert any(int(item.get("id", 0)) == uploaded_sample_id for item in body if isinstance(item, dict))

    no_token_resp = client.get(f"{base_url}/api/v1/samples")
    assert no_token_resp.status_code == 401

    invalid_token_resp = client.get(
        f"{base_url}/api/v1/samples",
        headers={"Authorization": "Bearer invalid_token_for_test"},
    )
    assert invalid_token_resp.status_code == 401


def test_te007_delete_valid_and_not_found(
    base_url: str,
    client: httpx.Client,
    auth_headers: dict[str, str],
    uploaded_sample_id: int,
) -> None:
    not_found_resp = client.delete(f"{base_url}/api/v1/samples/99999999", headers=auth_headers)
    assert not_found_resp.status_code == 404

    ok_resp = client.delete(f"{base_url}/api/v1/samples/{uploaded_sample_id}", headers=auth_headers)
    assert ok_resp.status_code == 204

    verify_resp = client.get(f"{base_url}/api/v1/result/{uploaded_sample_id}", headers=auth_headers)
    assert verify_resp.status_code == 404


def test_te008_url_scan(base_url: str, client: httpx.Client) -> None:
    ok_resp = client.get(f"{base_url}/api/v1/url/scan", params={"url": "http://example.com"})
    assert ok_resp.status_code in (200, 503)
    if ok_resp.status_code == 200:
        assert isinstance(ok_resp.json(), dict)

    bad_resp = client.get(f"{base_url}/api/v1/url/scan", params={"url": ""})
    assert bad_resp.status_code == 400


def test_te009_hash_scan(base_url: str, client: httpx.Client) -> None:
    md5_eicar = "44d88612fea8a8f36de82e1278abb02f"
    ok_resp = client.get(f"{base_url}/api/v1/hash/scan", params={"file_hash": md5_eicar})
    assert ok_resp.status_code in (200, 503)
    if ok_resp.status_code == 200:
        assert isinstance(ok_resp.json(), dict)

    bad_resp = client.get(f"{base_url}/api/v1/hash/scan", params={"file_hash": ""})
    assert bad_resp.status_code == 400
