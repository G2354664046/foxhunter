import { defineStore } from "pinia";
import { ref, computed } from "vue";
import http from "@/api/http";

const TOKEN_KEY = "fh_admin_token";

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || "");
  const me = ref(null);

  const isLoggedIn = computed(() => !!token.value);

  function setToken(t) {
    token.value = t;
    if (t) localStorage.setItem(TOKEN_KEY, t);
    else localStorage.removeItem(TOKEN_KEY);
  }

  function clear() {
    token.value = "";
    me.value = null;
    localStorage.removeItem(TOKEN_KEY);
  }

  async function login(username, password) {
    const { data } = await http.post("/auth/login", { username, password });
    setToken(data.access_token);
    await fetchMe();
  }

  async function fetchMe() {
    if (!token.value) return;
    const { data } = await http.get("/auth/me");
    me.value = data;
  }

  async function logout() {
    clear();
  }

  return {
    token,
    me,
    isLoggedIn,
    login,
    fetchMe,
    logout,
    clear,
  };
});
