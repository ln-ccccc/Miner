<template>
  <div class="settings">
    <div class="panel-header">
      <h3>功能设置</h3>
      <button class="save-btn" @click="persist">保存</button>
    </div>

    <div class="form">
      <div class="row">
        <div class="label">默认底图</div>
        <select v-model="draft.defaultLayer">
          <option value="base">标准地图</option>
          <option value="satellite">卫星影像</option>
          <option value="terrain">地形图</option>
        </select>
      </div>

      <div class="row">
        <div class="label">显示图例</div>
        <label class="switch">
          <input type="checkbox" v-model="draft.showLegend" />
          <span class="slider"></span>
        </label>
      </div>

      <div class="row">
        <div class="label">进入系统后自动定位</div>
        <label class="switch">
          <input type="checkbox" v-model="draft.autoFitBounds" />
          <span class="slider"></span>
        </label>
      </div>

      <div class="tip">
        设置会保存到本机浏览器，下次打开系统自动生效。
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue';

const props = defineProps({
  settings: Object
});

const emit = defineEmits(['update']);

const draft = reactive({
  defaultLayer: 'satellite',
  showLegend: true,
  autoFitBounds: true
});

watch(
  () => props.settings,
  (val) => {
    if (!val) return;
    draft.defaultLayer = val.defaultLayer ?? 'satellite';
    draft.showLegend = val.showLegend ?? true;
    draft.autoFitBounds = val.autoFitBounds ?? true;
  },
  { immediate: true, deep: true }
);

const persist = () => {
  emit('update', { ...draft });
};
</script>

<style scoped>
.settings {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 12px;
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

.save-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #8da3b6;
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-size: 12px;
}

.label {
  color: #8da3b6;
}

select {
  width: 160px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 6px;
  border-radius: 6px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.15);
  transition: 0.2s;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.slider:before {
  position: absolute;
  content: '';
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 2px;
  background-color: #fff;
  transition: 0.2s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: rgba(78, 205, 196, 0.35);
  border-color: rgba(78, 205, 196, 0.55);
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.tip {
  margin-top: 4px;
  font-size: 11px;
  color: rgba(224, 247, 255, 0.55);
  line-height: 1.4;
}
</style>

