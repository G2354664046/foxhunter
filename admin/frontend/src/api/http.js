import axios from "axios";
import { useAuthStore } from "@/stores/auth";
import { ElMessage } from "element-plus";
import router from "@/router";

const http = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

http.interceptors.request.use((config) => {
  const auth = useAuthStore();
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`;
  }
  return config;
});

http.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail;
    if (err.response?.status === 401) {
      const auth = useAuthStore();
      auth.clear();
      if (router.currentRoute.value.path !== "/login") {
        router.push("/login");
      }
      ElMessage.error(typeof msg === "string" ? msg : "登录已失效");
    } else {
      ElMessage.error(
        typeof msg === "string" ? msg : err.message || "请求失败"
      );
    }
    return Promise.reject(err);
  }
);

export default http;
