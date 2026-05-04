<template>
  <aside class="sidebar left-sidebar" :class="{ 'collapsed': collapsed }">
    <div class="sidebar-header">
      <h2>{{ headerTitle }}</h2>
      <button class="collapse-btn" @click="$emit('toggle')">
        {{ collapsed ? '➤' : '◀' }}
      </button>
    </div>
    
    <div class="sidebar-content" v-show="!collapsed">
      <div class="nav-panel glass-panel">
        <div class="panel-header">
          <h3>主要功能模块</h3>
          <button class="reset-btn" @click="toggleAllGroups">{{ allExpanded ? '收起' : '展开' }}</button>
        </div>

        <div class="nav-group" v-for="group in menuGroups" :key="group.key">
          <button class="group-title" @click="toggleGroup(group.key)">
            <span class="caret">{{ openGroups[group.key] ? '▾' : '▸' }}</span>
            <span class="group-text">{{ group.label }}</span>
          </button>
          <div class="group-items" v-show="openGroups[group.key]">
            <button
              v-for="item in group.items"
              :key="item.key"
              class="nav-item"
              :class="{ active: activeNavKey === item.key }"
              @click="navigate(item.key)"
            >
              {{ item.label }}
            </button>
          </div>
        </div>
      </div>

      <SettingsPanel
        v-if="activeNavKey === 'settings'"
        :settings="uiSettings"
        @update="$emit('update-settings', $event)"
      />

      <template v-else>
      <!-- 核心指标卡片 -->
      <div class="metric-grid">
        <div class="metric-card">
          <div class="metric-label">矿山总数</div>
          <div class="metric-value text-cyan">{{ mineTotal }}</div>
          <div class="metric-unit">个</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">监测面积</div>
          <div class="metric-value text-blue">{{ (overviewArea / 10000).toFixed(2) }}</div>
          <div class="metric-unit">万m²</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">已治理</div>
          <div class="metric-value text-green">{{ treatedCount }}</div>
          <div class="metric-unit">个</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">治理率</div>
          <div class="metric-value text-yellow">{{ mineTotal ? ((treatedCount / mineTotal) * 100).toFixed(1) : 0 }}</div>
          <div class="metric-unit">%</div>
        </div>
      </div>

      <!-- 筛选控制区 -->
      <div class="control-panel glass-panel">
        <div class="panel-header">
          <h3>筛选查询</h3>
          <button class="reset-btn" @click="emitReset">重置</button>
        </div>
        <div class="filter-group">
          <label>所属州市</label>
          <select :value="filterCity" @change="$emit('update:filterCity', $event.target.value); emitApply()">
            <option value="">全部州市</option>
            <option v-for="city in cityOptions" :key="city" :value="city">{{ city }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>治理状态</label>
          <select :value="filterStatus" @change="$emit('update:filterStatus', $event.target.value); emitApply()">
            <option value="">全部状态</option>
            <option value="treated">已治理</option>
            <option value="untreated">未治理</option>
          </select>
        </div>
        <div class="filter-group">
          <label>开采方式</label>
          <select :value="filterMethod" @change="$emit('update:filterMethod', $event.target.value); emitApply()">
            <option value="">全部方式</option>
            <option v-for="method in miningMethodOptions" :key="method" :value="method">{{ method }}</option>
          </select>
        </div>
        <div class="search-box">
          <input type="text" :value="searchMineId" @input="$emit('update:searchMineId', $event.target.value)" placeholder="输入矿山名称或ID..." @keyup.enter="emitSearch">
          <button @click="emitSearch">🔍</button>
        </div>
      </div>

      <!-- 统计列表 -->
      <div class="ranking-panel glass-panel">
        <div class="panel-header"><h3>修复方式 TOP5</h3></div>
        <div class="ranking-list">
          <div class="ranking-item" v-for="(item, index) in restorationMethodList" :key="index">
            <span class="rank-num" :class="'top-' + (index + 1)">{{ index + 1 }}</span>
            <span class="rank-name">{{ item.name }}</span>
            <div class="rank-bar-container">
              <div class="rank-bar" :style="{ width: (item.count / (restorationMethodList[0]?.count || 1) * 100) + '%' }"></div>
            </div>
            <span class="rank-val">{{ item.count }}</span>
          </div>
        </div>
      </div>
      </template>
    </div>
  </aside>
</template>

<script setup>
import { computed, defineProps, defineEmits, reactive } from 'vue';
import SettingsPanel from './SettingsPanel.vue';

const props = defineProps({
  collapsed: Boolean,
  mineTotal: Number,
  overviewArea: Number,
  treatedCount: Number,
  untreatedCount: Number,
  restorationMethodList: Array,
  cityOptions: Array,
  miningMethodOptions: Array,
  filterCity: String,
  filterStatus: String,
  filterMethod: String,
  searchMineId: String,
  activeNavKey: String,
  uiSettings: Object
});

const emit = defineEmits([
  'toggle', 
  'update:filterCity', 
  'update:filterStatus', 
  'update:filterMethod', 
  'update:searchMineId',
  'apply-filters', 
  'reset-filters', 
  'search',
  'navigate',
  'update-settings'
]);

const emitApply = () => emit('apply-filters');
const emitReset = () => emit('reset-filters');
const emitSearch = () => emit('search');

const menuGroups = [
  {
    key: 'workbench',
    label: '监测工作台',
    items: [
      { key: 'dashboard', label: '地图监测' },
      { key: 'analysis', label: '分析统计' }
    ]
  },
  {
    key: 'data',
    label: '数据管理',
    items: [
      { key: 'query', label: '筛选查询' },
      { key: 'search', label: '矿山检索' }
    ]
  },
  {
    key: 'system',
    label: '系统管理',
    items: [
      { key: 'settings', label: '功能设置' },
      { key: 'about', label: '帮助与关于' }
    ]
  }
];

const openGroups = reactive({
  workbench: true,
  data: true,
  system: true
});

const allExpanded = computed(() => Object.values(openGroups).every(Boolean));

const toggleGroup = (key) => {
  openGroups[key] = !openGroups[key];
};

const toggleAllGroups = () => {
  const next = !allExpanded.value;
  Object.keys(openGroups).forEach(k => {
    openGroups[k] = next;
  });
};

const navigate = (key) => {
  emit('navigate', key);
};

const headerTitle = computed(() => {
  if (props.activeNavKey === 'settings') return '功能设置';
  return '数据概览';
});
</script>

<style scoped>
.sidebar {
  width: 300px;
  background: rgba(10, 25, 41, 0.65);
  backdrop-filter: blur(15px);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar.collapsed { width: 40px; }
.sidebar.collapsed .sidebar-content { opacity: 0; pointer-events: none; }

.sidebar-header {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  white-space: nowrap;
}
.sidebar-header h2 { font-size: 16px; margin: 0; color: #4ecdc4; flex: 1; text-align: center; }
.collapse-btn {
  background: none;
  border: none;
  color: #8da3b6;
  cursor: pointer;
  font-size: 12px;
  padding: 5px;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  transition: opacity 0.2s;
}

.glass-panel {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 12px;
}

.nav-panel {
  padding: 12px;
}

.nav-group {
  margin-top: 10px;
}

.group-title {
  width: 100%;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.08);
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
}

.caret {
  width: 14px;
  text-align: center;
  color: #4ecdc4;
}

.group-text {
  font-size: 12px;
}

.group-items {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-left: 22px;
}

.nav-item {
  width: 100%;
  text-align: left;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  color: rgba(224, 247, 255, 0.8);
  padding: 7px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.nav-item.active {
  background: rgba(78, 205, 196, 0.2);
  border-color: rgba(78, 205, 196, 0.35);
  color: #e0f7ff;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.panel-header h3 {
  font-size: 14px;
  color: #fff;
  margin: 0;
  border-left: 3px solid #4ecdc4;
  padding-left: 8px;
}
.reset-btn {
  background: rgba(255,255,255,0.1);
  border: none;
  color: #8da3b6;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  cursor: pointer;
}

/* Metric Cards */
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.metric-card {
  background: rgba(0,0,0,0.2);
  padding: 10px;
  border-radius: 6px;
  text-align: center;
}
.metric-label { font-size: 12px; color: #8da3b6; }
.metric-value { font-size: 18px; font-weight: bold; margin: 5px 0; }
.metric-unit { font-size: 10px; color: #666; }
.text-cyan { color: #4ecdc4; }
.text-blue { color: #24c1ff; }
.text-green { color: #00b894; }
.text-yellow { color: #f1c40f; }

/* Filter */
.filter-group { margin-bottom: 10px; }
.filter-group label { display: block; font-size: 12px; color: #8da3b6; margin-bottom: 4px; }
.filter-group select {
  width: 100%;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  padding: 6px;
  border-radius: 4px;
}
.search-box { display: flex; gap: 5px; margin-top: 15px; }
.search-box input {
  flex: 1;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  padding: 6px;
  border-radius: 4px;
}
.search-box button { background: #4ecdc4; border: none; border-radius: 4px; cursor: pointer; }

/* Ranking */
.ranking-list { display: flex; flex-direction: column; gap: 8px; }
.ranking-item { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.rank-num { width: 18px; height: 18px; background: #333; border-radius: 50%; text-align: center; line-height: 18px; font-size: 10px; }
.top-1 { background: #f1c40f; color: #000; }
.top-2 { background: #bdc3c7; color: #000; }
.top-3 { background: #e67e22; color: #000; }
.rank-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rank-bar-container { flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; }
.rank-bar { height: 100%; background: #4ecdc4; border-radius: 3px; }
</style>
