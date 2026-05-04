import { ref } from 'vue';

const STORAGE_KEY = 'mine_auth_v1';

const isAuthenticated = ref(false);
const userName = ref('');

const readStored = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object') return null;
    if (!parsed.userName) return null;
    return parsed;
  } catch {
    return null;
  }
};

const persist = (payload) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
};

export function useAuth() {
  const initAuth = () => {
    const stored = readStored();
    if (!stored) {
      isAuthenticated.value = false;
      userName.value = '';
      return;
    }
    isAuthenticated.value = true;
    userName.value = stored.userName;
  };

  const login = ({ user, password }) => {
    const expectedUser = import.meta.env.VITE_DEMO_USER || 'admin';
    const expectedPass = import.meta.env.VITE_DEMO_PASS || 'admin123';

    if (String(user).trim() !== expectedUser || String(password) !== expectedPass) {
      return { ok: false, message: '账号或密码错误' };
    }

    isAuthenticated.value = true;
    userName.value = expectedUser;
    persist({ userName: expectedUser, loginAt: Date.now() });
    return { ok: true };
  };

  const logout = () => {
    isAuthenticated.value = false;
    userName.value = '';
    localStorage.removeItem(STORAGE_KEY);
  };

  return {
    isAuthenticated,
    userName,
    initAuth,
    login,
    logout
  };
}

