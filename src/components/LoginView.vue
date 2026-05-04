<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand">
        <div class="title">矿山生态修复智能监测平台</div>
        <div class="subtitle">登录后进入系统工作台</div>
      </div>

      <form class="form" @submit.prevent="onSubmit">
        <div class="field">
          <label>账号</label>
          <input v-model="user" autocomplete="username" placeholder="请输入账号" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" autocomplete="current-password" placeholder="请输入密码" />
        </div>

        <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

        <button class="submit" type="submit">登录</button>
        <div class="hint">
          默认账号：{{ defaultUser }} / {{ defaultPass }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  onLogin: Function
});

const user = ref('');
const password = ref('');
const errorMessage = ref('');

const defaultUser = computed(() => import.meta.env.VITE_DEMO_USER || 'admin');
const defaultPass = computed(() => import.meta.env.VITE_DEMO_PASS || 'admin123');

const onSubmit = async () => {
  errorMessage.value = '';
  const result = await props.onLogin?.({ user: user.value, password: password.value });
  if (result?.ok === false) {
    errorMessage.value = result.message || '登录失败';
  }
};
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  background: radial-gradient(1200px 600px at 20% 20%, rgba(78, 205, 196, 0.25), transparent 60%),
    radial-gradient(1000px 500px at 80% 10%, rgba(9, 132, 227, 0.25), transparent 60%),
    #0a1929;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #e0f7ff;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.login-card {
  width: 420px;
  padding: 28px 28px 22px;
  background: rgba(13, 27, 42, 0.78);
  border: 1px solid rgba(78, 205, 196, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(14px);
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.45);
}

.brand {
  margin-bottom: 18px;
}

.title {
  font-size: 18px;
  font-weight: 650;
  letter-spacing: 0.5px;
  background: linear-gradient(90deg, #ffffff, #4ecdc4);
  -webkit-background-clip: text;
  color: transparent;
}

.subtitle {
  margin-top: 6px;
  font-size: 12px;
  color: rgba(224, 247, 255, 0.7);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field label {
  display: block;
  font-size: 12px;
  color: rgba(224, 247, 255, 0.7);
  margin-bottom: 6px;
}

.field input {
  width: 100%;
  height: 38px;
  box-sizing: border-box;
  padding: 0 12px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  outline: none;
}

.field input:focus {
  border-color: rgba(78, 205, 196, 0.65);
  box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.12);
}

.submit {
  height: 40px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #0984e3, #00cec9);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.submit:hover {
  filter: brightness(1.03);
}

.error {
  font-size: 12px;
  color: #ff7675;
  background: rgba(255, 118, 117, 0.12);
  border: 1px solid rgba(255, 118, 117, 0.25);
  padding: 8px 10px;
  border-radius: 8px;
}

.hint {
  margin-top: 2px;
  font-size: 11px;
  color: rgba(224, 247, 255, 0.55);
}
</style>
