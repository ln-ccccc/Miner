<template>
  <LoginView v-if="!isAuthenticated" :onLogin="handleLogin" />

  <div v-else class="dashboard">
    <!-- 顶部导航栏 -->
    <TheHeader 
      :weatherIcon="weatherIcon"
      :temperature="temperature"
      :airQuality="airQuality"
      :currentDate="currentDate"
      :currentTime="currentTime"
      :getAqiClass="getAqiClass"
      :userName="userName"
      @open-settings="activeNavKey = 'settings'"
      @logout="handleLogout"
    />

    <!-- 主体内容 -->
    <main class="main-container">
      <!-- 左侧边栏 -->
      <LeftSidebar
        v-model:filterCity="filterCity"
        v-model:filterStatus="filterStatus"
        v-model:filterMethod="filterMethod"
        v-model:searchMineId="searchMineId"
        :collapsed="leftCollapsed"
        :mineTotal="mineTotal"
        :overviewArea="overviewArea"
        :treatedCount="treatedCount"
        :untreatedCount="untreatedCount"
        :restorationMethodList="restorationMethodList"
        :cityOptions="cityOptions"
        :miningMethodOptions="miningMethodOptions"
        :activeNavKey="activeNavKey"
        :uiSettings="uiSettings"
        @toggle="leftCollapsed = !leftCollapsed"
        @apply-filters="applyFilters"
        @reset-filters="resetFilters"
        @search="performSearch"
        @navigate="handleNavigate"
        @update-settings="updateUiSettings"
      />

      <!-- 中间地图区域 -->
      <MapContainer
        ref="mapContainerRef"
        :minesData="filteredMinesData"
        :leftCollapsed="leftCollapsed"
        :rightCollapsed="rightCollapsed"
        :defaultLayer="uiSettings.defaultLayer"
        :showLegend="uiSettings.showLegend"
        :autoFitBounds="uiSettings.autoFitBounds"
        @select-mine="handleSelectMine"
        @layer-change="updateUiSettings({ defaultLayer: $event })"
      />

      <!-- 右侧边栏 -->
      <RightSidebar
        :collapsed="rightCollapsed"
        :treatedCount="treatedCount"
        :untreatedCount="untreatedCount"
        :landTypeList="landTypeList"
        :miningMethodList="miningMethodList" 
        @toggle="rightCollapsed = !rightCollapsed"
      />
    </main>

    <!-- 矿山详情弹窗 -->
    <MineDetailModal
      :visible="showMineDetail"
      :mineData="selectedMine"
      :indicesData="mineIndices"
      :changeMatrixData="mineChangeMatrix"
      :selectedTab="selectedTab"
      :formatMaybeNumber="formatMaybeNumber"
      :formatTrend="formatTrend"
      :getTrendClass="getTrendClass"
      @close="showMineDetail = false"
      @tab-change="selectedTab = $event"
    />
  </div>
</template>

<script setup>
import { onMounted, ref, nextTick, watch } from 'vue';

// Components
import TheHeader from './components/TheHeader.vue';
import LeftSidebar from './components/LeftSidebar.vue';
import RightSidebar from './components/RightSidebar.vue';
import MapContainer from './components/MapContainer.vue';
import MineDetailModal from './components/MineDetailModal.vue';
import LoginView from './components/LoginView.vue';

// Composables
import { useWeather } from './composables/useWeather';
import { useMineData } from './composables/useMineData';
import { useAuth } from './composables/useAuth';

// --- State ---
const leftCollapsed = ref(false);
const rightCollapsed = ref(false);
const showMineDetail = ref(false);
const selectedMine = ref({});
const selectedTab = ref('NDVI');
const activeNavKey = ref('dashboard');

const mapContainerRef = ref(null);

// --- Composables Usage ---
const { 
  currentDate, currentTime, temperature, weatherIcon, airQuality, getAqiClass, fetchRealtimeEnvironmentAt 
} = useWeather();

const { isAuthenticated, userName, initAuth, login, logout } = useAuth();

const UI_SETTINGS_KEY = 'mine_ui_settings_v1';
const uiSettings = ref({
  defaultLayer: 'satellite',
  showLegend: true,
  autoFitBounds: true
});

const loadUiSettings = () => {
  try {
    const raw = localStorage.getItem(UI_SETTINGS_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object') return;
    uiSettings.value = {
      defaultLayer: parsed.defaultLayer ?? 'satellite',
      showLegend: parsed.showLegend ?? true,
      autoFitBounds: parsed.autoFitBounds ?? true
    };
  } catch {}
};

const updateUiSettings = (next) => {
  uiSettings.value = { ...uiSettings.value, ...next };
  localStorage.setItem(UI_SETTINGS_KEY, JSON.stringify(uiSettings.value));
};

const {
  allMinesData,
  filteredMinesData,
  filterCity,
  filterStatus,
  filterMethod,
  searchMineId,
  cityOptions,
  miningMethodOptions,
  mineTotal,
  overviewArea,
  treatedCount,
  untreatedCount,
  restorationMethodList,
  miningMethodList,
  landTypeList,
  mineIndices,
  mineChangeMatrix,
  loadData,
  applyFilters,
  resetFilters,
  fetchIndices,
  formatMaybeNumber,
  formatTrend,
  getTrendClass
} = useMineData();

// --- Event Handlers ---

const performSearch = () => {
  if (!searchMineId.value) return;
  
  // Find target in all data
  const target = allMinesData.value.find(f => {
    const p = f.properties;
    const q = String(searchMineId.value).trim().toLowerCase();
    const candidates = [
      p.FID_1,
      p.KZ,
      p.ZTBH,
      p.CKZH,
      p.mine_name,
      p.name,
      p.GGKSMC,
      p.SBKSMC,
      p.ZLKSMC,
      p.KSWZ
    ]
      .filter(Boolean)
      .map(v => String(v).toLowerCase());
    return candidates.some(v => v.includes(q));
  });

  if (target) {
     // If filtered out, reset filters or ensure it is visible?
     // We can try to fly to it if it exists in filteredMinesData, otherwise we might need to reset.
     // Let's reset filters to be safe so it appears on map.
     if (!filteredMinesData.value.find(f => f.properties.FID_1 === target.properties.FID_1)) {
       resetFilters();
     }
     
     // Need to wait for map to re-render with new data
     nextTick(() => {
        if (mapContainerRef.value) {
          mapContainerRef.value.flyToMine(target.properties.FID_1);
        }
     });
  } else {
    alert('未找到该矿山');
  }
};

const handleSelectMine = async ({ feature, center }) => {
  const p = feature.properties;
  const displayName =
    p.mine_name ||
    p.name ||
    p.GGKSMC ||
    p.SBKSMC ||
    p.ZLKSMC ||
    (p.FID_1 ? `矿山 ${p.FID_1}` : '矿山详情');
  selectedMine.value = {
    mine_id: p.FID_1,
    name: displayName,
    area: p.area || p.TBTYMJ,
    status_raw: p.HFZLQK,
    status_normalized: p.status_normalized,
    center_lat: center.lat,
    center_lng: center.lng
  };
  
  showMineDetail.value = true;
  selectedTab.value = 'NDVI';
  
  await fetchIndices(p.FID_1);
  
  // Update weather for this location
  fetchRealtimeEnvironmentAt(center.lat, center.lng);
};

const handleNavigate = (key) => {
  if (key === 'about') {
    alert('矿山生态修复智能监测平台\n\n用于矿山治理状态与生态指标的可视化监测、筛选查询与统计分析。');
    return;
  }
  activeNavKey.value = key;
};

const handleLogin = ({ user, password }) => {
  return login({ user, password });
};

const handleLogout = () => {
  logout();
  activeNavKey.value = 'dashboard';
  showMineDetail.value = false;
};

// --- Lifecycle ---
onMounted(() => {
  initAuth();
  loadUiSettings();
});

const dataInitialized = ref(false);

watch(
  () => isAuthenticated.value,
  (authed) => {
    if (!authed) return;
    if (dataInitialized.value) return;
    dataInitialized.value = true;
    loadData();
    fetchRealtimeEnvironmentAt(25.6, 100.2);
    window.addEventListener('resize', () => {
      if (mapContainerRef.value) mapContainerRef.value.invalidateSize();
    });
  },
  { immediate: true }
);
</script>

<style scoped>
/* 基础变量 */
:root {
  --bg-dark: #0a1929;
  --panel-bg: rgba(13, 27, 42, 0.75);
  --border-color: rgba(78, 205, 196, 0.3);
  --text-primary: #e0f7ff;
  --text-secondary: #8da3b6;
  --accent-cyan: #4ecdc4;
  --accent-blue: #24c1ff;
}

.dashboard {
  width: 100vw;
  height: 100vh;
  background-color: #0a1929;
  color: #e0f7ff;
  overflow: hidden;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

/* Main Layout */
.main-container {
  flex: 1;
  position: relative;
  display: flex;
  overflow: hidden;
}
</style>
