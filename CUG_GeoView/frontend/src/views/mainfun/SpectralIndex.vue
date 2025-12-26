<template>
  <div>
    <Tabinfor>
      <template #left>
        <div id="sub-title">光谱指数计算<i class="iconfont icon-dianji"/></div>
      </template>
    </Tabinfor>
    <el-divider />

    <p>
      请上传<span class="go-bold">图片文件</span>，支持多波段 GeoTIFF（.tif/.tiff）与常见格式（jpg/png）。
    </p>

    <el-row type="flex" justify="center">
      <el-col :span="24">
        <el-card style="border: 4px dashed var(--el-border-color)">
          <div style="display:flex; gap:16px; flex-wrap:wrap; align-items:center; margin-bottom:12px;">
            <el-radio-group v-model="indexName" size="small">
              <el-radio-button label="NDVI" />
              <el-radio-button label="NDWI" />
              <el-radio-button label="NDBI" />
            </el-radio-group>
            <el-select v-model="preset" placeholder="卫星预设" size="small" style="width:180px" @change="applyPreset">
              <el-option label="Landsat 8" value="landsat8" />
              <el-option label="Sentinel-2" value="sentinel2" />
            </el-select>
            <el-select v-model="colormap" placeholder="颜色映射" size="small" style="width:180px">
              <el-option label="RdYlGn" value="RdYlGn" />
              <el-option label="Blues" value="Blues" />
              <el-option label="BrBG" value="BrBG" />
              <el-option label="viridis" value="viridis" />
            </el-select>
          </div>
          <div style="display:flex; gap:16px; flex-wrap:wrap; align-items:center;">
            <el-input-number v-model="bands.red" :min="1" :max="20" size="small" label="Red" />
            <el-input-number v-model="bands.green" :min="1" :max="20" size="small" label="Green" />
            <el-input-number v-model="bands.nir" :min="1" :max="20" size="small" label="NIR" />
            <el-input-number v-model="bands.swir1" :min="1" :max="20" size="small" label="SWIR1" />
          </div>
          <div v-if="fileList.length" class="clear-queue" style="margin-top:8px;">
            <el-button type="primary" class="btn-animate2 btn-animate__surround" @click="clearQueue">清空图片</el-button>
          </div>
          <el-upload
            ref="upload"
            v-model:file-list="fileList"
            class="upload-card"
            drag
            action="#"
            multiple
            :auto-upload="false"
            @change="beforeUpload(fileList[fileList.length - 1]?.raw || fileList[fileList.length - 1])"
          >
            <i class="iconfont icon-yunduanshangchuan" />
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
          </el-upload>
          <div class="handle-button">
            <el-button type="primary" class="btn-animate btn-animate__shiny" @click="doUpload">开始处理</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <Tabinfor>
      <template #left>
        <div id="sub-title">结果图预览<i class="iconfont icon-dianji"/></div>
      </template>
      <template #right>
        <span class="go-bold">
          <i class="iconfont icon-shuaxin" style="padding-right:55px" @click="getMore"><span class="hidden-sm-and-down">点击刷新</span></i>
        </span>
      </template>
    </Tabinfor>
    <el-divider />

    <el-card class="result-card">
      <div>
        <el-empty v-if="!isUpload" :image-size="300" />
        <div v-else>
          <el-row class="swiper-img">
            <div v-for="(item, index) in imgArr" :key="item.id" class="img-box">
              <el-card shadow="hover" class="img-card">
                <div class="img-header">
                  <div class="title">{{ indexName }} 结果</div>
                  <div class="stats">min={{ item.stats.min.toFixed(3) }} · mean={{ item.stats.mean.toFixed(3) }} · max={{ item.stats.max.toFixed(3) }}</div>
                </div>
                <div class="img-pair">
                  <el-image :src="item.before_img" fit="contain" />
                  <el-image :src="item.after_img" fit="contain" />
                </div>
                <div class="legend">
                  <span class="legend-label">-1</span>
                  <span class="legend-label">0</span>
                  <span class="legend-label">1</span>
                </div>
                <div class="actions">
                  <el-button type="primary" class="btn-animate btn-animate__shiny" @click="downloadimgWithWords(item.id, item.after_img, '指数结果图.png')">下载结果图</el-button>
                </div>
              </el-card>
            </div>
          </el-row>
        </div>
      </div>
    </el-card>
    <Bottominfor />
  </div>
</template>

<script>
import { fromArrayBuffer } from 'geotiff';
import { downloadimgWithWords } from "@/utils/download.js";
import Tabinfor from "@/components/Tabinfor";
import Bottominfor from "@/components/Bottominfor";

export default {
  name: "SpectralIndex",
  components: { Tabinfor, Bottominfor },
  data() {
    return {
      fileList: [],
      imgArr: [],
      isUpload: false,
      indexName: "NDVI",
      preset: "sentinel2",
      colormap: "RdYlGn",
      bands: { red: 4, green: 3, nir: 8, swir1: 11 },
    };
  },
  methods: {
    downloadimgWithWords,
    clearQueue() {
      this.fileList = [];
      this.imgArr = [];
      this.isUpload = false;
      this.$message.success("清除成功");
    },
    getMore() {
      if (this.imgArr.length === 0) this.$message.info("暂无结果");
    },
    beforeUpload(file) {},
    applyPreset() {
      if (this.preset === "landsat8") {
        this.bands = { red: 4, green: 3, nir: 5, swir1: 6 };
      } else if (this.preset === "sentinel2") {
        this.bands = { red: 4, green: 3, nir: 8, swir1: 11 };
      }
    },
    async doUpload() {
      if (this.fileList.length === 0) {
        this.$message.error("请上传图片！");
        return;
      }
      this.imgArr = [];
      for (const item of this.fileList) {
        const file = item.raw || item;
        try {
          const res = await this.processFile(file);
          this.imgArr.push({ before_img: res.before, after_img: res.after, stats: res.stats, id: Math.random().toString(36).slice(2) });
        } catch (e) {
          this.$message.error(e.message || "处理失败，请检查波段设置或文件格式");
        }
      }
      this.isUpload = this.imgArr.length > 0;
    },
    async processFile(file) {
      const name = String(file?.name || "");
      const type = String(file?.type || "");
      const isTiff = /\.tiff?$/i.test(name) || /tiff/i.test(type);
      if (isTiff) return await this.processTiff(file);
      return await this.processRgbImage(file);
    },
    async processTiff(file) {
      const buffer = await file.arrayBuffer();
      const tiff = await fromArrayBuffer(buffer);
      const image = await tiff.getImage();
      const rasters = await image.readRasters({ interleave: false });
      const nb = rasters.length;
      let { red, green, nir, swir1 } = this.bands;
      const pick = (idx) => {
        if (!idx || idx < 1 || idx > nb) throw new Error(`波段索引超出范围: ${idx}，当前影像共有 ${nb} 个波段`);
        return rasters[idx - 1];
      };

      let vals;
      if (this.indexName === "NDVI") {
        if ((red > nb || nir > nb) && nb === 4) { red = 1; nir = 4; }
        vals = this.computeND(pick(nir), pick(red));
      } else if (this.indexName === "NDWI") {
        if ((green > nb || nir > nb) && nb === 4) { green = 2; nir = 4; }
        vals = this.computeND(pick(green), pick(nir));
      } else if (this.indexName === "NDBI") {
        vals = this.computeND(pick(swir1), pick(nir));
      }

      const W = image.getWidth();
      const H = image.getHeight();
      const beforeUrl = this.renderGrayscalePreview(pick(Math.min(Math.max(1, red || 1), nb)), W, H);
      const afterUrl = this.renderColorMapped(vals, W, H, this.colormap);

      let min = 1, max = -1, sum = 0;
      for (let i = 0; i < vals.length; i++) {
        const v = Math.max(-1, Math.min(1, vals[i]));
        if (v < min) min = v;
        if (v > max) max = v;
        sum += v;
      }
      const mean = sum / vals.length;
      return { before: beforeUrl, after: afterUrl, stats: { min, mean, max } };
    },
    async processRgbImage(file) {
      const beforeUrl = URL.createObjectURL(file);
      const img = await new Promise((resolve, reject) => {
        const el = new Image();
        el.onload = () => resolve(el);
        el.onerror = () => reject(new Error("图片读取失败"));
        el.src = beforeUrl;
      });
      const canvas = document.createElement("canvas");
      canvas.width = img.naturalWidth || img.width;
      canvas.height = img.naturalHeight || img.height;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);

      const W = canvas.width;
      const H = canvas.height;
      const a = new Float32Array(W * H);
      const b = new Float32Array(W * H);
      for (let i = 0; i < W * H; i++) {
        const r = data[i * 4 + 0];
        const g = data[i * 4 + 1];
        const bl = data[i * 4 + 2];
        if (this.indexName === "NDVI") { a[i] = g; b[i] = r; }
        else if (this.indexName === "NDWI") { a[i] = g; b[i] = bl; }
        else { a[i] = r; b[i] = bl; }
      }
      const vals = this.computeND(a, b);
      const afterUrl = this.renderColorMapped(vals, W, H, this.colormap);

      let min = 1, max = -1, sum = 0;
      for (let i = 0; i < vals.length; i++) {
        const v = Math.max(-1, Math.min(1, vals[i]));
        if (v < min) min = v;
        if (v > max) max = v;
        sum += v;
      }
      const mean = sum / vals.length;
      return { before: beforeUrl, after: afterUrl, stats: { min, mean, max } };
    },
    computeND(a, b) {
      const out = new Float32Array(a.length);
      for (let i = 0; i < a.length; i++) {
        const ai = a[i];
        const bi = b[i];
        const den = ai + bi + 1e-6;
        out[i] = (ai - bi) / den;
      }
      return out;
    },
    renderGrayscalePreview(band, W, H) {
      const canvas = document.createElement("canvas");
      canvas.width = W;
      canvas.height = H;
      const ctx = canvas.getContext("2d");
      const img = ctx.createImageData(W, H);

      let min = Infinity;
      let max = -Infinity;
      for (let i = 0; i < band.length; i++) {
        const v = Number(band[i]);
        if (!Number.isFinite(v)) continue;
        if (v < min) min = v;
        if (v > max) max = v;
      }
      if (!Number.isFinite(min) || !Number.isFinite(max) || max === min) {
        min = 0;
        max = 1;
      }
      const scale = 255 / (max - min);
      for (let i = 0; i < W * H; i++) {
        const v = Number(band[i]);
        const n = Number.isFinite(v) ? Math.max(0, Math.min(255, Math.round((v - min) * scale))) : 0;
        img.data[i * 4 + 0] = n;
        img.data[i * 4 + 1] = n;
        img.data[i * 4 + 2] = n;
        img.data[i * 4 + 3] = 255;
      }
      ctx.putImageData(img, 0, 0);
      return canvas.toDataURL("image/png");
    },
    renderColorMapped(vals, W, H, cmapName) {
      const canvas = document.createElement("canvas");
      canvas.width = W;
      canvas.height = H + 40;
      const ctx = canvas.getContext("2d");
      const img = ctx.createImageData(W, H);
      const map = this.getColorMap(cmapName);
      for (let i = 0; i < W * H; i++) {
        const v = Math.max(-1, Math.min(1, vals[i]));
        const [r, g, b] = this.sampleMap(map, (v + 1) / 2);
        img.data[i * 4 + 0] = r;
        img.data[i * 4 + 1] = g;
        img.data[i * 4 + 2] = b;
        img.data[i * 4 + 3] = 255;
      }
      ctx.putImageData(img, 0, 0);
      const bar = ctx.createLinearGradient(0, H + 15, W, H + 15);
      for (const s of map) bar.addColorStop(s.p, `rgb(${s.c[0]},${s.c[1]},${s.c[2]})`);
      ctx.fillStyle = bar;
      ctx.fillRect(0, H + 10, W, 14);
      ctx.fillStyle = "#333";
      ctx.font = "12px sans-serif";
      ctx.fillText("-1", 4, H + 34);
      ctx.fillText("0", W / 2 - 4, H + 34);
      ctx.fillText("1", W - 14, H + 34);
      return canvas.toDataURL("image/png");
    },
    getColorMap(name) {
      if (name === "Blues") {
        return [
          { p: 0.0, c: [222, 235, 247] },
          { p: 0.5, c: [107, 174, 214] },
          { p: 1.0, c: [33, 113, 181] },
        ];
      } else if (name === "BrBG") {
        return [
          { p: 0.0, c: [216, 179, 101] },
          { p: 0.5, c: [245, 245, 245] },
          { p: 1.0, c: [90, 180, 172] },
        ];
      } else if (name === "RdYlGn") {
        return [
          { p: 0.0, c: [165, 0, 38] },
          { p: 0.5, c: [255, 255, 191] },
          { p: 1.0, c: [0, 104, 55] },
        ];
      }
      return [
        { p: 0.0, c: [68, 1, 84] },
        { p: 0.5, c: [58, 82, 139] },
        { p: 1.0, c: [253, 231, 37] },
      ];
    },
    sampleMap(stops, p) {
      let s0 = stops[0], s1 = stops[stops.length - 1];
      for (let i = 1; i < stops.length; i++) {
        if (p <= stops[i].p) { s0 = stops[i - 1]; s1 = stops[i]; break; }
      }
      const t = (p - s0.p) / (s1.p - s0.p + 1e-6);
      const r = Math.round(s0.c[0] + t * (s1.c[0] - s0.c[0]));
      const g = Math.round(s0.c[1] + t * (s1.c[1] - s0.c[1]));
      const b = Math.round(s0.c[2] + t * (s1.c[2] - s0.c[2]));
      return [r, g, b];
    },
  },
};
</script>

<style scoped>
.result-card { background: rgba(255,255,255,0.75); }
.swiper-img { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 16px; }
.img-box { margin-bottom: 0; }
.img-card { border-radius: 12px; overflow: hidden; }
.img-header { display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background: rgba(0,0,0,0.03); }
.title { font-weight: 600; }
.stats { font-size: 12px; color: #666; }
.img-pair { display:flex; gap:12px; align-items:center; }
.img-pair .el-image { width: 48%; border-radius:8px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
.legend { display:flex; justify-content:space-between; padding: 4px 12px; font-size: 12px; color:#666; }
.legend-label { }
.actions { text-align:center; padding: 8px 12px; }
</style>
