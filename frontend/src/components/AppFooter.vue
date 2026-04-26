<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-brand">
          <span class="logo-icon">📢</span>
          <span class="logo-text">信息发布平台</span>
        </div>
        <p class="footer-description">
          发布公告、发布任务，让信息触达更多人
        </p>
      </div>
      <div class="footer-links">
        <div class="link-group">
          <h4>功能</h4>
          <router-link to="/">首页</router-link>
          <router-link to="/new-post" v-if="user">发布信息</router-link>
        </div>
        <div class="link-group">
          <h4>会员</h4>
          <router-link to="/upgrade">升级会员</router-link>
          <router-link to="/recharge" v-if="user">账户充值</router-link>
        </div>
        <div class="link-group">
          <h4>账户</h4>
          <router-link to="/login" v-if="!user">登录</router-link>
          <router-link to="/register" v-if="!user">注册</router-link>
          <router-link to="/profile" v-if="user">个人中心</router-link>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="footer-container">
        <p class="copyright">© 2024 信息发布平台. 保留所有权利.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
defineProps({
  user: {
    type: Object,
    default: null
  }
})
</script>

<style scoped>
.app-footer {
  background: #f5f5f7;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  margin-top: auto;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-content {
  padding: 40px 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 40px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.footer-brand .logo-icon {
  font-size: 24px;
}

.footer-brand .logo-text {
  font-weight: 600;
  font-size: 18px;
  color: var(--color-text);
}

.footer-description {
  font-size: 14px;
  color: var(--color-text-secondary);
  max-width: 300px;
  line-height: 1.5;
}

.footer-links {
  display: flex;
  gap: 60px;
}

.link-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.link-group h4 {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.link-group a {
  font-size: 14px;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.link-group a:hover {
  color: var(--color-primary);
}

.footer-bottom {
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  padding: 16px 0;
}

.copyright {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0;
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    gap: 32px;
  }
  
  .footer-links {
    flex-wrap: wrap;
    gap: 32px;
  }
}
</style>
