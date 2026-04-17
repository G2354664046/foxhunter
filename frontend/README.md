# FoxHunter Frontend

FoxHunter 前端项目，基于 Vue 3 + Vite，提供恶意样本检测平台的 Web 界面。

## 技术栈

- Vue 3（Composition API）
- Vue Router
- Pinia
- Axios
- ECharts + vue-echarts
- Tailwind CSS

## 主要功能

- 用户认证：登录、注册、找回密码、个人资料、设置页
- 首页检测入口：文件检测、URL 检测、哈希查询
- 文件上传：支持 `.exe/.dll/.bin`，提交后跳转结果页
- 结果展示：支持轮询检测状态、摘要可视化、明细 JSON
- 样本记录：查看历史检测记录并删除
- 鉴权访问控制：受保护页面需登录后访问

## 路由说明

- `/`：首页（检测入口）
- `/samples`：样本记录（需登录）
- `/results/:id`：检测结果（需登录；`preview` 支持预览）
- `/login`：登录/注册入口（通过 query 切换模式）
- `/forgot-password`：找回密码
- `/profile`：个人信息（需登录）
- `/settings`：系统设置（需登录）

## 目录结构

```text
frontend/
├── src/
│   ├── components/        # 通用组件（如 Header）
│   ├── views/             # 页面视图
│   ├── router/            # 路由配置
│   ├── stores/            # Pinia 状态管理
│   ├── lib/               # API 与 JWT 工具
│   ├── assets/            # 样式与静态资源
│   ├── App.vue
│   └── main.js
├── public/
├── package.json
└── README.md
```

## 安装与运行

```bash
cd frontend
npm install
npm run dev
```

默认开发地址：`http://localhost:5173`

## 打包与预览

```bash
npm run build
npm run preview
```

## 后端联调

前端通过 `axios` 调用后端 `/api/v1/*` 接口，并自动在请求头携带本地保存的 JWT：

- `Authorization: Bearer <access_token>`

核心接口包含：

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `GET /api/v1/auth/me`
- `POST /api/v1/upload`
- `GET /api/v1/result/{id}`
- `GET /api/v1/samples`
- `DELETE /api/v1/samples/{id}`
- `GET /api/v1/url/scan`
- `GET /api/v1/hash/scan`

## 开发提示

- 进入受保护路由前会检查 `localStorage.access_token`
- 首页 URL/哈希检测支持结果预览并可跳转结果页
- 结果页在样本状态为 `pending/processing` 时会自动轮询