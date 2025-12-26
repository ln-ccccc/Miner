<template>
  <div class="dashboard">
    <div class="header">
      <div class="header-left">
        <div class="weather">
          <span class="weather-icon">{{ weatherIcon }}</span>
          <span class="temperature">{{ temperature }}°C</span>
          <span class="air-quality">空气{{ airQuality }}</span>
        </div>
      </div>
      <div class="header-title">
        <h1>云南矿山生态修复智能监测平台</h1>
      </div>
      <div class="header-right">
        <div class="date-time">{{ currentDate }} {{ currentTime }}</div>
        <div class="login-info">
          <span class="icon">👤</span>
          <span>管理员</span>
        </div>
        <button class="enter-system-btn" @click="goGeoView">进入系统</button>
      </div>
    </div>

    <div class="main-content">
      <div class="mine-type-card glass-card floating-card">
        <div class="panel-title fancy-title">矿山类型统计</div>
        <div class="chart-inner">
          <div class="pie-segments">
            <div class="segment segment-1"></div>
            <div class="segment segment-2"></div>
            <div class="segment segment-3"></div>
            <div class="segment segment-4"></div>
            <div class="segment segment-5"></div>
          </div>
          <div class="pie-center">
            <div class="pie-value gradient-number">{{ mineTotal }}</div>
            <div class="pie-label subtle-label">矿山</div>
          </div>
        </div>
      </div>

      <div class="overlay-right">
        <div class="data-overview glass-card floating-card">
          <div class="panel-title fancy-title">数据概览</div>
          <div class="overview-item">
            <div class="overview-value gradient-number">{{ overviewArea }}</div>
            <div class="overview-label subtle-label">监测面积(㎡)</div>
          </div>
          <div class="overview-item">
            <div class="overview-value gradient-number">{{ overviewSoilCover }}</div>
            <div class="overview-label subtle-label">土壤覆盖</div>
          </div>
        </div>

        <div class="env-indicators glass-card floating-card">
          <div class="panel-title fancy-title">环境指标</div>
          <div class="env-grid">
            <div class="env-item">
              <div class="env-value gradient-number">{{ humidity }}%</div>
              <div class="env-label subtle-label">湿度</div>
            </div>
            <div class="env-item">
              <div class="env-value gradient-number">{{ rainfall }}mm</div>
              <div class="env-label subtle-label">降雨</div>
            </div>
            <div class="env-item">
              <div class="env-value gradient-number">{{ airTemp }}°C</div>
              <div class="env-label subtle-label">气温</div>
            </div>
          </div>
        </div>

        <div class="ranking glass-card floating-card">
          <div class="panel-title fancy-title">视图信息</div>
          <div class="detail-item">
            <div class="detail-label">缩放级别</div>
            <div class="detail-value">{{ mapZoom ?? '—' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">中心坐标</div>
            <div class="detail-value">{{ mapCenterText }}</div>
          </div>
        </div>

        <div class="personnel glass-card floating-card">
          <div class="panel-title fancy-title">人员与设备</div>
          <div class="personnel-grid">
            <div class="personnel-item">
              <div class="personnel-value gradient-number">{{ mineTotal }}</div>
              <div class="personnel-label subtle-label">矿山总数</div>
            </div>
            <div class="personnel-item">
              <div class="personnel-value gradient-number">{{ monitorCount }}</div>
              <div class="personnel-label subtle-label">监测设备</div>
            </div>
            <div class="personnel-item">
              <div class="personnel-value gradient-number">{{ interventionCount }}</div>
              <div class="personnel-label subtle-label">修复项目</div>
            </div>
          </div>
        </div>
      </div>

      <div class="map-container">
        <div class="map-controls">
          <div class="layer-switch">
            <div class="layer-btn" :class="{ active: currentLayer === 'base' }" @click="switchLayer('base')">基础地图</div>
            <div class="layer-btn" :class="{ active: currentLayer === 'satellite' }" @click="switchLayer('satellite')">卫星图层</div>
            <div class="layer-btn" :class="{ active: currentLayer === 'terrain' }" @click="switchLayer('terrain')">地形图层</div>
          </div>
          <div class="search-container">
            <input type="text" v-model="searchMineId" placeholder="输入矿山ID" class="search-input" />
            <button @click="searchMineById" class="search-btn">搜索</button>
          </div>
        </div>
        <div id="map"></div>

        <div class="mine-detail glass-card" v-if="showMineDetail">
          <div class="panel-title fancy-title">矿山详情</div>
          <div class="detail-item">
            <div class="detail-label">名称</div>
            <div class="detail-value">{{ selectedMine.name ?? '—' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">面积</div>
            <div class="detail-value">{{ selectedMine.area ?? '暂无' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">位置坐标</div>
            <div class="detail-value">{{ (selectedMine.center_lat != null && selectedMine.center_lng != null) ? `${Number(selectedMine.center_lat).toFixed(6)}, ${Number(selectedMine.center_lng).toFixed(6)}` : '—' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">边界范围</div>
            <div class="detail-value">{{ selectedMine.bbox ?? '—' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">NDVI均值</div>
            <div class="detail-value">{{ selectedMine.ndvi_mean != null ? Number(selectedMine.ndvi_mean).toFixed(3) : '—' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">NDVI趋势</div>
            <div class="detail-value" :class="getTrendClass(selectedMine.ndvi_trend)">{{ selectedMine.ndvi_trend != null ? formatTrend(selectedMine.ndvi_trend) : '—' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">MK趋势</div>
            <div class="detail-value" :class="getMkTrendClass(selectedMine.mk_trend)">{{ selectedMine.mk_trend ?? '—' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Sen's Slope</div>
            <div class="detail-value">{{ selectedMine.sens_slope != null ? formatSensSlope(selectedMine.sens_slope) : '—' }}</div>
          </div>
          <div class="trend-chart">
            <div ref="ndviChart" class="chart-placeholder"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </template>

<script>
import { onMounted, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  name: 'MineHome',
  setup() {
    const router = useRouter()
    const goGeoView = () => { router.push('/detectchanges') }

    const currentLayer = ref('base')
    const showMineDetail = ref(false)
    const selectedMine = ref({})
    const currentDate = ref('')
    const currentTime = ref('')

    const temperature = ref(25)
    const weatherIcon = ref('🌤️')
    const airQuality = ref('优')
    const humidity = ref(69)

    const soilMoisture = ref(12)
    const rainfall = ref(23)
    const airTemp = ref(45)

    const overviewArea = ref(0)
    const overviewSoilCover = ref(0)
    const donutTotal = ref(0)

    const searchMineId = ref('')
    const ndviChart = ref(null)
    let map = null
    let baseMaps = {}
    let mineLayer = null
    let minesData = []

    const mapCenter = ref(null)
    const mapZoom = ref(null)
    const mapCenterText = ref('—')

    const personnelData = ref([
      { label: '监测设备', value: 1237 },
      { label: '修复项目', value: 2584 }
    ])

    const mineTotal = ref(3821)
    const monitorCount = ref(1237)
    const interventionCount = ref(2584)

    const animateNumber = (refObj, target, duration = 800) => {
      const start = Number(refObj.value) || 0
      const startTime = performance.now()
      const step = (t) => {
        const p = Math.min((t - startTime) / duration, 1)
        const v = Math.floor(start + (target - start) * p)
        refObj.value = v
        if (p < 1) requestAnimationFrame(step)
      }
      requestAnimationFrame(step)
    }

    const formatTrend = (trend) => {
      if (!trend && trend !== 0) return '暂无数据'
      const v = Number(trend) || 0
      return (v > 0 ? '上升' : (v < 0 ? '下降' : '无趋势')) + '（' + v.toFixed(3) + '）'
    }

    const getTrendClass = (trend) => {
      if (!trend) return ''
      if (String(trend).includes('上升')) return 'trend-up'
      if (String(trend).includes('下降')) return 'trend-down'
      return ''
    }

    const getMkTrendClass = (mk) => {
      if (!mk) return ''
      if (String(mk).includes('上升')) return 'trend-up'
      if (String(mk).includes('下降')) return 'trend-down'
      return ''
    }

    const formatSensSlope = (slope) => {
      if (!slope && slope !== 0) return '暂无数据'
      return (Number(slope) || 0).toFixed(4) + ' / 年'
    }

    const switchLayer = (layer) => {
      currentLayer.value = layer
      updateMapLayer()
    }

    const updateMapLayer = () => {
      if (!map) return
      Object.values(baseMaps).forEach(layer => { if (map.hasLayer(layer)) map.removeLayer(layer) })
      if (baseMaps[currentLayer.value]) baseMaps[currentLayer.value].addTo(map)
      if (mineLayer && !map.hasLayer(mineLayer)) mineLayer.addTo(map)
    }

    const searchMineById = async () => {
      if (!searchMineId.value) return
      try {
        const { data: feature } = await axios.get(`http://localhost:8000/api/mines/search?q=${encodeURIComponent(searchMineId.value)}`)
        const bounds = L.geoJSON(feature).getBounds()
        map.fitBounds(bounds, { padding: [50, 50] })
        mineLayer.resetStyle()
        const targetFid = feature.properties.FID_1
        mineLayer.eachLayer(layer => {
          const fid = layer.feature?.properties?.FID_1
          if (fid === targetFid) layer.setStyle({ color: '#00d2d3', weight: 3, opacity: 1, fillColor: '#00d2d3', fillOpacity: 0.35 })
        })
      } catch (e) {}
    }

    const renderNdviTrendChart = () => {
      if (!ndviChart.value || !selectedMine.value?.ndvi_data?.length) return
      const el = ndviChart.value
      const myChart = echarts.init(el)
      const years = selectedMine.value.ndvi_data.map(d => d.year)
      const values = selectedMine.value.ndvi_data.map(d => Number(d.ndvi_value))
      const slope = Number(selectedMine.value.ndvi_trend) || 0
      const base = values[0] || 0
      const trendData = years.map((y, i) => Number((base + slope * i).toFixed(3)))
      const option = {
        grid: { left: 40, right: 20, top: 26, bottom: 28 },
        legend: { data: ['NDVI值', '趋势线'], textStyle: { color: '#bbb' }, right: 10, top: 0 },
        xAxis: { type: 'category', data: years, axisLine: { lineStyle: { color: '#666' } }, axisLabel: { color: '#bbb', fontSize: 10 } },
        yAxis: { type: 'value', name: 'NDVI', nameTextStyle: { color: '#bbb' }, min: Math.max(0, Math.min(...values) - 0.1), max: Math.min(1, Math.max(...values) + 0.1), axisLine: { lineStyle: { color: '#666' } }, axisLabel: { color: '#bbb', fontSize: 10 }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
        series: [
          { name: 'NDVI值', data: values, type: 'line', smooth: true, symbol: 'circle', symbolSize: 6, itemStyle: { color: '#4ecdc4' }, lineStyle: { width: 3, color: '#4ecdc4' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [ { offset: 0, color: 'rgba(78, 205, 196, 0.5)' }, { offset: 1, color: 'rgba(78, 205, 196, 0.1)' } ]) } },
          { name: '趋势线', type: 'line', data: trendData, smooth: false, symbol: 'none', lineStyle: { width: 2, type: 'dashed', color: slope > 0 ? '#4ecdc4' : '#ff6b6b' } }
        ],
        tooltip: { trigger: 'axis', formatter: function(params) { const ndviData = params[0]; const trendData = params[1]; return `${ndviData.name}年<br/>NDVI: ${Number(ndviData.value).toFixed(3)}<br/>趋势值: ${Number(trendData.value).toFixed(3)}`; }, backgroundColor: 'rgba(0,21,41,0.9)', borderColor: '#1e3a5f', textStyle: { color: '#fff' } }
      }
      myChart.setOption(option)
      window.addEventListener('resize', () => { myChart.resize() })
    }

    const initMap = () => {
      map = L.map('map', { zoomControl: false, attributionControl: false }).setView([25.6, 100.2], 9)
      L.control.zoom({ position: 'bottomright' }).addTo(map)
      baseMaps = {
        base: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }),
        satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 }),
        terrain: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', { maxZoom: 17 })
      }
      baseMaps[currentLayer.value].addTo(map)
      loadMinesData()
      registerMapListeners()
    }

    const registerMapListeners = () => {
      if (!map) return
      map.on('moveend', () => {
        const c = map.getCenter()
        mapCenter.value = c
        mapZoom.value = map.getZoom()
        mapCenterText.value = `${Number(c.lat).toFixed(6)}, ${Number(c.lng).toFixed(6)}`
        fetchRealtimeEnvironmentAt(c.lat, c.lng)
      })
      map.on('zoomend', () => {
        const c = map.getCenter()
        mapCenter.value = c
        mapZoom.value = map.getZoom()
        mapCenterText.value = `${Number(c.lat).toFixed(6)}, ${Number(c.lng).toFixed(6)}`
      })
      const c = map.getCenter()
      mapCenter.value = c
      mapZoom.value = map.getZoom()
      mapCenterText.value = `${Number(c.lat).toFixed(6)}, ${Number(c.lng).toFixed(6)}`
      fetchRealtimeEnvironmentAt(c.lat, c.lng)
    }

    const loadMinesData = async () => {
      try {
        const { data } = await axios.get('http://localhost:8000/api/geojson')
        if (!data || !data.features) throw new Error('invalid geojson')
        const geojsonData = data
        minesData = geojsonData.features
        mineLayer = L.geoJSON(geojsonData, {
          style: { color: '#4ecdc4', weight: 2, opacity: 0.9, fillColor: '#4ecdc4', fillOpacity: 0.15 },
          onEachFeature: (feature, layer) => {
            layer.on('mouseover', (e) => { e.target.setStyle({ weight: 3, color: '#81ecec', fillOpacity: 0.25 }); e.target.bringToFront() })
            layer.on('mouseout', (e) => { mineLayer.resetStyle(e.target) })
            layer.on('click', async () => {
              const fid = feature.properties.FID_1
              const mineName = feature.properties.mine_name || feature.properties.name || `矿山 ${fid}`
              mineLayer.resetStyle()
              layer.setStyle({ color: '#00d2d3', weight: 3, opacity: 1, fillColor: '#00d2d3', fillOpacity: 0.35 })
              const bounds = layer.getBounds()
              map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 })
              const center = bounds.getCenter()
              fetchRealtimeEnvironmentAt(center.lat, center.lng)
              try {
                const res = await axios.get(`http://localhost:8000/api/mines/ndvi?fid=${fid}`)
                const ndvi = res.data
                selectedMine.value = { mine_id: fid, name: mineName, area: feature.properties.area, center_lat: center.lat, center_lng: center.lng, bbox: bounds.toBBoxString && bounds.toBBoxString(), ndvi_mean: ndvi.ndvi_mean ?? null, ndvi_trend: ndvi.ndvi_trend ?? null, mk_trend: ndvi.mk_trend ?? null, sens_slope: ndvi.ndvi_trend != null ? ndvi.ndvi_trend / 10 : null, ndvi_data: ndvi.ndvi_data?.length ? ndvi.ndvi_data : [] }
              } catch (err) {
                selectedMine.value = { mine_id: fid, name: mineName, area: feature.properties.area, center_lat: center.lat, center_lng: center.lng, bbox: bounds.toBBoxString && bounds.toBBoxString(), ndvi_mean: null, ndvi_trend: null, mk_trend: null, sens_slope: null, ndvi_data: [] }
              }
              showMineDetail.value = true
              nextTick(() => { renderNdviTrendChart() })
            })
          }
        })
        mineLayer.addTo(map)
      } catch (error) {
        const geojsonData = { type: 'FeatureCollection', features: [ { type: 'Feature', properties: { FID_1: 1, mine_name: '示例矿山1', area: 12000 }, geometry: { type: 'Polygon', coordinates: [[[100.10,25.20],[100.20,25.20],[100.20,25.30],[100.10,25.30],[100.10,25.20]]] } }, { type: 'Feature', properties: { FID_1: 2, mine_name: '示例矿山2', area: 8400 }, geometry: { type: 'Polygon', coordinates: [[[100.20,25.10],[100.30,25.10],[100.30,25.20],[100.20,25.20],[100.20,25.10]]] } }, { type: 'Feature', properties: { FID_1: 3, mine_name: '示例矿山3', area: 6500 }, geometry: { type: 'Polygon', coordinates: [[[100.15,25.25],[100.25,25.25],[100.25,25.35],[100.15,25.35],[100.15,25.25]]] } }, { type: 'Feature', properties: { FID_1: 4, mine_name: '示例矿山4', area: 22000 }, geometry: { type: 'Polygon', coordinates: [[[100.35,25.15],[100.45,25.15],[100.45,25.25],[100.35,25.25],[100.35,25.15]]] } }, { type: 'Feature', properties: { FID_1: 5, mine_name: '示例矿山5', area: 18000 }, geometry: { type: 'Polygon', coordinates: [[[100.40,25.20],[100.50,25.20],[100.50,25.30],[100.40,25.30],[100.40,25.20]]] } } ] }
        minesData = geojsonData.features
        mineLayer = L.geoJSON(geojsonData, {
          style: { color: '#4ecdc4', weight: 2, opacity: 0.9, fillColor: '#4ecdc4', fillOpacity: 0.15 },
          onEachFeature: (feature, layer) => {
            layer.on('mouseover', (e) => { e.target.setStyle({ weight: 3, color: '#81ecec', fillOpacity: 0.25 }); e.target.bringToFront() })
            layer.on('mouseout', (e) => { mineLayer.resetStyle(e.target) })
            layer.on('click', async () => {
              const fid = feature.properties.FID_1
              const mineName = feature.properties.mine_name
              mineLayer.resetStyle()
              layer.setStyle({ color: '#00d2d3', weight: 3, opacity: 1, fillColor: '#00d2d3', fillOpacity: 0.35 })
              map.fitBounds(layer.getBounds(), { padding: [50, 50] })
              const center = layer.getBounds().getCenter()
              fetchRealtimeEnvironmentAt(center.lat, center.lng)
              selectedMine.value = { mine_id: fid, name: mineName, area: feature.properties.area, center_lat: center.lat, center_lng: center.lng, bbox: layer.getBounds().toBBoxString && layer.getBounds().toBBoxString(), ndvi_mean: null, ndvi_trend: null, mk_trend: null, sens_slope: null, ndvi_data: [] }
              showMineDetail.value = true
              nextTick(() => { renderNdviTrendChart() })
            })
          }
        })
        mineLayer.addTo(map)
      }
    }

    const fetchRealtimeEnvironmentAt = (lat, lng) => {
      temperature.value = 20 + Math.floor(Math.random() * 10)
      airQuality.value = ['优', '良', '一般'][Math.floor(Math.random() * 3)]
      humidity.value = 50 + Math.floor(Math.random() * 30)
      soilMoisture.value = 10 + Math.floor(Math.random() * 20)
      rainfall.value = Math.floor(Math.random() * 30)
      airTemp.value = 15 + Math.floor(Math.random() * 20)
    }

    const updateDateTime = () => {
      const now = new Date()
      const y = now.getFullYear()
      const m = String(now.getMonth() + 1).padStart(2, '0')
      const d = String(now.getDate()).padStart(2, '0')
      const h = String(now.getHours()).padStart(2, '0')
      const mm = String(now.getMinutes()).padStart(2, '0')
      const s = String(now.getSeconds()).padStart(2, '0')
      currentDate.value = `${y}-${m}-${d}`
      currentTime.value = `${h}:${mm}:${s}`
    }

    const startMineStatsTicker = () => {
      const targets = [ { ref: mineTotal, value: 3821 }, { ref: monitorCount, value: 1237 }, { ref: interventionCount, value: 2584 } ]
      let idx = 0
      setInterval(() => { const t = targets[idx]; t.ref.value = 0; animateNumber(t.ref, t.value, 900); idx = (idx + 1) % targets.length }, 3500)
    }

    onMounted(() => {
      setInterval(updateDateTime, 1000)
      animateNumber(overviewArea, 86532)
      animateNumber(overviewSoilCover, 11256)
      animateNumber(donutTotal, 1221)
      nextTick(() => { initMap() })
      startMineStatsTicker()
    })

    return { currentLayer, showMineDetail, selectedMine, currentDate, currentTime, temperature, weatherIcon, airQuality, humidity, soilMoisture, rainfall, airTemp, overviewArea, overviewSoilCover, donutTotal, searchMineId, ndviChart, mapCenter, mapZoom, mapCenterText, personnelData, switchLayer, searchMineById, formatTrend, getTrendClass, getMkTrendClass, formatSensSlope, mineTotal, monitorCount, interventionCount, goGeoView }
  }
}
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; width: 100%; height: 100vh; background-color: #0a1929; color: #fff; font-family: 'Arial', sans-serif; background-image: linear-gradient(to bottom, #001529, #0a1929); }
.header { display: flex; justify-content: space-between; align-items: center; height: 60px; padding: 0 20px; background-color: rgba(10, 25, 41, 0.35); border-bottom: 1px solid rgba(78,205,196,0.25); }
.header-left .weather { display: flex; gap: 10px; align-items: center; color: #a4b6c8; }
.header-title h1 { margin: 0; font-size: 18px; letter-spacing: 2px; color: #e6f7ff; text-shadow: 0 0 8px rgba(36, 193, 255, 0.2); }
.header-right { display: flex; align-items: center; gap: 12px; }
.enter-system-btn { padding: 6px 12px; background-color: #4ecdc4; color: #0a1929; border: none; border-radius: 4px; cursor: pointer; }
.enter-system-btn:hover { background-color: #3db9b0; }
.date-time { color: #a4b6c8; font-size: 12px; }
.main-content { position: relative; flex: 1; }
.overlay-right { position: absolute; right: 20px; top: 70px; bottom: 20px; width: 48%; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; z-index: 10; pointer-events: none; }
.overlay-right > * { pointer-events: auto; }
.glass-card { background: rgba(10, 25, 41, 0.45); border: 1px solid rgba(78, 205, 196, 0.18); border-radius: 10px; box-shadow: 0 8px 25px rgba(36, 193, 255, 0.12); backdrop-filter: blur(10px); }
.floating-card { padding: 12px; }
.panel-title { font-size: 14px; font-weight: 600; color: #5cd3c9; letter-spacing: 1px; border-bottom: 1px dashed rgba(78,205,196,0.35); padding-bottom: 6px; margin-bottom: 8px; }
.gradient-number { font-size: 26px; font-weight: 800; background: linear-gradient(135deg, #4ecdc4 0%, #24c1ff 60%, #fefefe 100%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 0 12px rgba(36, 193, 255, 0.35); }
.subtle-label { font-size: 12px; color: rgba(255,255,255,0.75); }
.mine-type-card .chart-inner { position: relative; height: 180px; display: flex; align-items: center; justify-content: center; }
.pie-segments { position: absolute; width: 140px; height: 140px; border-radius: 50%; background: conic-gradient(#4ecdc4 0% 28%, #24c1ff 28% 53%, #81ecec 53% 68%, #00d2d3 68% 85%, #74b9ff 85% 100%); filter: drop-shadow(0 2px 6px rgba(36,193,255,0.3)); }
.pie-center { position: absolute; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 70px; height: 70px; border-radius: 50%; background: rgba(30,58,95,0.6); border: 1px solid rgba(78,205,196,0.35); box-shadow: inset 0 0 12px rgba(36,193,255,0.25); }
.map-container { position: absolute; left: 20px; top: 70px; bottom: 20px; width: calc(52% - 40px); border-radius: 12px; overflow: hidden; border: 1px solid rgba(78,205,196,0.18); box-shadow: 0 6px 28px rgba(36, 193, 255, 0.2); }
#map { width: 100%; height: 100%; }
.map-controls { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000; background-color: rgba(10, 25, 41, 0.5); border: 1px solid #1e3a5f; border-radius: 8px; padding: 8px; display: flex; flex-direction: column; gap: 10px; backdrop-filter: blur(8px); box-shadow: 0 6px 22px rgba(36, 193, 255, 0.25); }
.layer-switch { display: flex; gap: 5px; }
.layer-btn { padding: 5px 10px; font-size: 12px; cursor: pointer; border-radius: 3px; background-color: rgba(30, 58, 95, 0.5); transition: all 0.3s; }
.layer-btn:hover { background-color: rgba(78, 205, 196, 0.3); }
.layer-btn.active { background-color: #4ecdc4; color: #0a1929; }
.search-container { display: flex; gap: 5px; margin-top: 5px; }
.search-input { flex: 1; padding: 5px 10px; background-color: rgba(255, 255, 255, 0.1); color: #fff; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 4px; outline: none; }
.search-input::placeholder { color: rgba(255, 255, 255, 0.5); }
.search-btn { padding: 5px 10px; background-color: #4ecdc4; color: #0a1929; border: none; border-radius: 4px; cursor: pointer; transition: all 0.3s; }
.search-btn:hover { background-color: #3db9b0; }
.mine-detail { position: absolute; left: 20px; bottom: 20px; width: calc(52% - 40px); border-radius: 12px; padding: 12px; }
.detail-item { display: grid; grid-template-columns: 120px 1fr; gap: 6px; padding: 6px 0; }
.detail-label { color: #9fb3c8; font-size: 12px; }
.detail-value { color: #f0f6ff; font-weight: 600; }
.trend-up { color: #4ecdc4; }
.trend-down { color: #ff6b6b; }
.ranking { }
.ranking-list { display: flex; flex-direction: column; gap: 8px; }
.ranking-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; border-radius: 8px; background: rgba(30,58,95,0.35); border: 1px solid rgba(78,205,196,0.18); }
.rank-pill { font-size: 12px; color: #0a1929; background: linear-gradient(135deg, #4ecdc4, #24c1ff); padding: 4px 8px; border-radius: 999px; box-shadow: 0 2px 8px rgba(36,193,255,0.3); }
.rank-name { font-weight: 600; color: #f0f6ff; }
.personnel-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
.personnel-item { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 8px; border-radius: 8px; background: rgba(30,58,95,0.35); border: 1px solid rgba(78,205,196,0.18); }
.personnel-value { font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #4ecdc4 0%, #24c1ff 60%, #fefefe 100%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 0 12px rgba(36, 193, 255, 0.35); }
.personnel-label { font-size: 12px; color: rgba(255,255,255,0.75); }
</style>
