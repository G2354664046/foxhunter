# FoxHunter Locust 压测脚本

该目录用于对核心接口进行压力测试，脚本文件为 `locustfile.py`。

## 1) 安装依赖

```bash
pip install locust
```

## 2) 启动压测（Web UI 模式）

在项目根目录执行：

```bash
locust -f test/locus/locustfile.py --host http://127.0.0.1:8000
```

然后打开浏览器：

- <http://localhost:8089>

建议先从小并发开始，例如：

- Users: `20`
- Spawn rate: `5`
- Run time: `3m`

## 3) 无界面模式（适合论文复现实验）

```bash
locust -f test/locus/locustfile.py --host http://127.0.0.1:8000 --headless -u 50 -r 10 -t 5m --csv test/locus/report/core_api
```

## 4) 可选：上传高压场景

默认脚本已包含常规混合流量（登录/鉴权/上传/查询/删除/情报/健康）。
如果你希望突出上传压力，可启用上传偏重用户：

```bash
set LOCUST_UPLOAD_HEAVY=1
locust -f test/locus/locustfile.py --host http://127.0.0.1:8000
```

## 5) 覆盖接口

- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/upload`
- `GET /api/v1/result/{sample_id}`
- `GET /api/v1/samples`
- `DELETE /api/v1/samples/{sample_id}`
- `GET /api/v1/url/scan`
- `GET /api/v1/hash/scan`

## 6) 注意事项

- 请确保 FastAPI、MySQL、Redis、Celery worker 已启动。
- `url_scan/hash_scan` 在未配置 API Key 时可能返回 `503`，这属于可接受降级行为。
- 上传接口会真实写入数据库，建议压测前后清理测试数据。
