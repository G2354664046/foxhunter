import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/Login.vue"),
    meta: { public: true, title: "登录" },
  },
  {
    path: "/",
    component: () => import("@/layouts/MainLayout.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("@/views/Dashboard.vue"),
        meta: { title: "首页" },
      },
      {
        path: "users",
        name: "Users",
        component: () => import("@/views/Users.vue"),
        meta: { title: "用户管理" },
      },
      {
        path: "samples",
        name: "Samples",
        component: () => import("@/views/Samples.vue"),
        meta: { title: "CNN 样本" },
      },
      {
        path: "cnn-results",
        name: "CnnResults",
        component: () => import("@/views/CnnResults.vue"),
        meta: { title: "检测记录" },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, _from, next) => {
  document.title = to.meta.title
    ? `${to.meta.title} - FoxHunter 管理后台`
    : "FoxHunter 管理后台";
  const auth = useAuthStore();
  if (to.meta.public) {
    if (auth.isLoggedIn && to.path === "/login") {
      next("/dashboard");
      return;
    }
    next();
    return;
  }
  if (!auth.isLoggedIn) {
    next({ path: "/login", query: { redirect: to.fullPath } });
    return;
  }
  if (!auth.me) {
    try {
      await auth.fetchMe();
    } catch {
      next({ path: "/login", query: { redirect: to.fullPath } });
      return;
    }
  }
  next();
});

export default router;
