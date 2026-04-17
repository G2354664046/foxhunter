from __future__ import annotations

import os
import random
import uuid

from locust import HttpUser, between, task


def _rand_suffix() -> str:
    return uuid.uuid4().hex[:8]


class FoxHunterUser(HttpUser):
    """
    核心接口压测用户：
    - on_start 阶段自动注册+登录，拿到 token
    - task 阶段按权重覆盖核心 API
    """

    wait_time = between(0.2, 1.2)

    def on_start(self) -> None:
        self.username = f"locust_{_rand_suffix()}"
        self.email = f"{self.username}@example.com"
        self.password = "Passw0rd123"
        self.token: str | None = None
        self.sample_ids: list[int] = []

        self._register()
        self._login()

    def _auth_headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def _register(self) -> None:
        payload = {
            "username": self.username,
            "email": self.email,
            "password": self.password,
        }
        with self.client.post(
            "/api/v1/auth/register",
            json=payload,
            name="auth_register",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"register failed: {resp.status_code} {resp.text[:200]}")

    def _login(self) -> None:
        data = {"username": self.username, "password": self.password}
        with self.client.post(
            "/api/v1/auth/login",
            data=data,
            name="auth_login",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"login failed: {resp.status_code} {resp.text[:200]}")
                return
            token = resp.json().get("access_token")
            if not token:
                resp.failure("login missing access_token")
                return
            self.token = token
            resp.success()

    @task(2)
    def health(self) -> None:
        self.client.get("/api/v1/health", name="health")

    @task(4)
    def auth_me(self) -> None:
        self.client.get("/api/v1/auth/me", headers=self._auth_headers(), name="auth_me")

    @task(4)
    def list_samples(self) -> None:
        self.client.get("/api/v1/samples", headers=self._auth_headers(), name="samples_list")

    @task(6)
    def upload_sample(self) -> None:
        # 上传较小随机数据，降低本地压测时磁盘与模型推理压力
        filename = f"locust_{_rand_suffix()}.bin"
        files = {"file": (filename, os.urandom(256), "application/octet-stream")}
        with self.client.post(
            "/api/v1/upload",
            files=files,
            headers=self._auth_headers(),
            name="upload",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"upload failed: {resp.status_code} {resp.text[:200]}")
                return
            body = resp.json()
            sample_id = body.get("sample_id")
            if not sample_id:
                resp.failure("upload missing sample_id")
                return
            self.sample_ids.append(int(sample_id))
            # 防止无限增长
            if len(self.sample_ids) > 30:
                self.sample_ids = self.sample_ids[-20:]
            resp.success()

    @task(5)
    def query_result(self) -> None:
        # 优先查已上传样本；为空时查一个不存在 ID 也能测到接口耗时
        sample_id = random.choice(self.sample_ids) if self.sample_ids else 99999999
        self.client.get(
            f"/api/v1/result/{sample_id}",
            headers=self._auth_headers(),
            name="result_get",
        )

    @task(2)
    def delete_sample(self) -> None:
        if not self.sample_ids:
            return
        sample_id = self.sample_ids.pop(0)
        self.client.delete(
            f"/api/v1/samples/{sample_id}",
            headers=self._auth_headers(),
            name="samples_delete",
        )

    @task(1)
    def url_scan(self) -> None:
        self.client.get(
            "/api/v1/url/scan",
            params={"url": "http://example.com"},
            name="url_scan",
        )

    @task(1)
    def hash_scan(self) -> None:
        self.client.get(
            "/api/v1/hash/scan",
            params={"file_hash": "44d88612fea8a8f36de82e1278abb02f"},
            name="hash_scan",
        )


class FoxHunterHighUploadUser(FoxHunterUser):
    """
    上传偏重压测模型：
    通过环境变量 LOCUST_UPLOAD_HEAVY=1 启用（推荐单独场景使用）
    """

    weight = 1 if os.getenv("LOCUST_UPLOAD_HEAVY", "0") == "1" else 0

    @task(20)
    def upload_sample(self) -> None:
        super().upload_sample()
