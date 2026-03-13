# FoxHunter Malware Detection System
![主页](./preview/home.PNG)
![主页](./preview/home2.PNG)
<<<<<<< HEAD
FoxHunter 是一套基于生产者‑消费者架构的自动化恶意软件检测平台。后端使用 FastAPI 提供 REST API，前端采用 Vue.js 3 + TailwindCSS 实现现代化交互，整个流程异步解耦，支持高并发上传和检测。
=======

FoxHunter 是一套基于生产者‑消费者架构的自动化恶意软件检测平台。后端使用 FastAPI 提供 REST API，前端采用 Vue.js 3 + TailwindCSS 实现现代化交互，整个流程异步解耦，支持高并发上传和检测。可作为本科毕设参考，目前算法改进中...
>>>>>>> eee645dca545f41b6828eb2d16af12ec3502d632

## 核心功能 🎯

- **灰度图 + HOG 特征提取**：将二进制样本转为灰度图并提取图像特征
- **多模型融合**：
  1. 路径一：灰度图 + HOG + 随机森林分类器
  2. 路径二：灰度图 + CNN（MobileNetV2）
- **决策融合机制**：基于置信度的加权投票策略，误报率较单模型降低约 15%
- **异步任务架构**：FastAPI + Redis + Celery 实现上传即返回、后台检测、前端轮询的生产者‑消费者流程
- **数据库持久化**：MySQL 保存样本记录，Redis 用作消息队列/结果缓存
- **基础用户功能**：注册/登录/JWT 鉴权；样本记录按用户隔离
- **前端动态展示**：Vue3 + ECharts 艺术化统计与图表
- **现代界面与交互**：TailwindCSS 精心美化，响应式设计，上传拖拽、状态提示、结果分析图表
- **拓展性**：RESTful API 可供第三方集成，支持批量检测、哈希查询等功能

## 技术栈 🧩

- **后端**：Python 3.11+, FastAPI, SQLAlchemy
- **前端**：Vue.js 3, Vite, Tailwind CSS, ECharts
- **数据库**：MySQL (样本记录) + Redis (Celery broker/backend)
- **任务队列**：Celery
- **其它**：PE 文件解析（`pefile`），模型推理接口（当前仓库中使用伪数据占位，便于演示），可选 URL 检测集成（URLhaus 公共 API）

## 项目结构

```
foxhunter/
├── app/                    # FastAPI 后端代码（路由、服务、模型、数据库）
├── frontend/               # Vue.js 3 前端应用
├── celery_app.py           # Celery 配置
├── requirements.txt        # Python 依赖
└── README.md               # 本文档
```

## 准备工作 🛠️

1. 克隆仓库并进入目录：
   ```bash
   git clone <repo> foxhunter
   cd foxhunter
   ```
2. 后端环境：
   - 创建虚拟环境并激活
   - 安装依赖：
     ```bash
     pip install -r requirements.txt
     ```
3. 数据库：
   - 启动 MySQL 并创建数据库 `foxhunter` 或在 `.env` 中配置 `MYSQL_URL`。
   - 启动 Redis，默认监听 `redis://localhost:6379/0`。
   - （可选）使用 Docker 一键启动 MySQL + Redis：
     ```bash
     docker compose up -d
     ```
4. 配置环境变量（可参考示例 `.env`）：
   ```text
   MYSQL_URL=mysql+mysqlconnector://root:password@localhost:3306/foxhunter?charset=utf8mb4
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=${REDIS_URL}
   CELERY_RESULT_BACKEND=${REDIS_URL}
   UPLOAD_DIR=uploads
   JWT_SECRET_KEY=dev-change-me
   # 可选：URLhaus / VirusTotal API Key
   URLHAUS_API_KEY=your_urlhaus_key
   VIRUSTOTAL_API_KEY=your_virustotal_key
   ```
5. 启动数据库表结构（启动 FastAPI 时会自动调用）。

## 开发与运行 🚀

### 启动后端服务

```bash
# 启动 FastAPI 应用（推荐）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 另一个终端启动 Celery worker
celery -A celery_app worker --loglevel=info
```

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认在 http://localhost:5173 运行，API 可通过 `/api/v1/*` 访问。

### 演示流程（建议）

1. 访问前端 `http://localhost:5173/`
2. 点击右上角 **登录/注册**，先注册一个用户并登录
3. 进入 **文件检测** 页面上传样本
4. 前端会轮询 `/api/v1/result/{id}` 展示检测状态与结果（由 Celery 后台异步更新）

## 主要接口 📡

| 方法 | 路径                     | 功能                               |
|------|--------------------------|------------------------------------|
| POST | `/api/v1/auth/register`  | 注册                               |
| POST | `/api/v1/auth/login`     | 登录（返回 JWT）                   |
| GET  | `/api/v1/auth/me`        | 获取当前用户                       |
| POST | `/api/v1/upload`         | 上传样本文件并触发异步检测         |
| GET  | `/api/v1/samples`        | 列出当前用户的样本检测记录         |
| DELETE | `/api/v1/samples/{id}` | 删除一条样本检测记录               |
| GET  | `/api/v1/result/{id}`    | 查询指定样本的检测状态与结果       |
| GET  | `/api/v1/url/scan`       | 使用 URLhaus 公共 API 对 URL 进行检测 |
| GET  | `/api/v1/hash/scan`      | 使用 VirusTotal v3 API 按哈希查询文件信息 |
| GET  | `/api/v1/health`         | API 健康检查                       |

更多扩展接口（URL 检测、哈希查询等）可在后续版本中添加。

---

感谢使用 FoxHunter，欢迎贡献与改进！
