# FoxHunter Admin 管理后台

本目录是 FoxHunter 的管理端子项目，包含：

- `backend`：管理员 API（FastAPI）
- `frontend`：管理后台界面（Vue 3 + Element Plus）

用于管理员登录、用户管理、样本管理、CNN 检测记录查看与仪表盘统计。

## 目录结构

```text
admin/
├── backend/        # 管理端后端（FastAPI）
├── frontend/       # 管理端前端（Vue 3 + Vite）
└── README.md
```

## 后端说明（admin/backend）

### 技术栈

- FastAPI
- SQLAlchemy
- MySQL（与主项目共库）
- JWT 鉴权

### 环境变量

可参考 `admin/backend/.env.example`：

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `FOXHUNTER_API_BASE`
- `BOOTSTRAP_ADMIN_USERNAME`
- `BOOTSTRAP_ADMIN_PASSWORD`

### 安装与启动

```bash
cd admin/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

说明：

- 服务启动时会自动检查并创建管理员表
- 当无管理员账号时，会按环境变量自动初始化默认管理员

### 主要接口（前缀 `/api`）

- 认证
  - `POST /api/auth/login`
  - `GET /api/auth/me`
- 用户管理
  - `GET /api/users`
  - `GET /api/users/{id}`
  - `POST /api/users`
  - `PUT /api/users/{id}`
  - `DELETE /api/users/{id}`
- 样本管理
  - `GET /api/samples`
  - `GET /api/samples/{id}`
  - `POST /api/samples`
  - `PUT /api/samples/{id}`
  - `DELETE /api/samples/{id}`
- CNN 结果管理
  - `GET /api/cnn-results`
  - `GET /api/cnn-results/{id}`
  - `POST /api/cnn-results`
  - `PUT /api/cnn-results/{id}`
  - `DELETE /api/cnn-results/{id}`
- 仪表盘
  - `GET /api/dashboard/summary`
  - `GET /api/dashboard/foxhunter`
- 健康检查
  - `GET /api/health`

## 前端说明（admin/frontend）

### 技术栈

- Vue 3
- Vue Router
- Pinia
- Element Plus
- Axios
- Vite

### 安装与启动

```bash
cd admin/frontend
npm install
npm run dev
```

默认端口：`5174`  
预览端口：`4173`

### 代理配置

前端开发服务已在 `vite.config.js` 配置代理：

- `/api` -> `http://127.0.0.1:8010`

即：启动前端前，请先启动管理端后端（8010）。

## 使用流程（本地）

1. 启动 MySQL 并确保 `DATABASE_URL` 可连接
2. 启动管理后端（8010）
3. 启动管理前端（5174）
4. 打开 `http://localhost:5174`，使用管理员账号登录

## 常见问题

- 前端登录后立即退出/401：
  - 检查后端 `JWT_SECRET_KEY` 是否正确
  - 检查前端代理目标是否为 `8010`
- 无法看到管理员账号：
  - 检查 `BOOTSTRAP_ADMIN_USERNAME/PASSWORD` 配置
  - 确认后端启动日志中无数据库连接错误
