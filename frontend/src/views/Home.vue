<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">信息发布平台</h1>
        <p class="hero-subtitle">发布公告、发布任务，让信息触达更多人</p>
        <div class="hero-actions">
          <router-link to="/new-post" class="btn-primary">
            <el-icon><Edit /></el-icon>
            发布信息
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { Edit } from '@element-plus/icons-vue'
</script>

<style scoped>
.home-page {
  flex: 1;
}

.hero-section {
  background: linear-gradient(180deg, #ffffff 0%, #f5f5f7 100%);
  padding: 80px 20px 60px;
  text-align: center;
}

.hero-content {
  max-width: 600px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 600;
  letter-spacing: -0.015em;
  line-height: 1.15;
  margin: 0 0 16px;
  background: linear-gradient(135deg, #1d1d1f 0%, #6e6e73 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 21px;
  line-height: 1.47059;
  font-weight: 400;
  letter-spacing: -0.01em;
  color: var(--color-text-secondary);
  margin: 0 0 32px;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.hero-actions .btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  font-size: 17px;
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: white;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 36px;
  }
  
  .hero-subtitle {
    font-size: 19px;
  }
}
</style>
