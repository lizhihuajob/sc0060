<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  color: #333;
  background: #f0f2f5;
}

a {
  text-decoration: none;
  color: inherit;
}

ul, ol {
  list-style: none;
}

:root {
  --color-primary: #0071e3;
  --color-primary-light: #4a9eff;
  --color-primary-dark: #0056b3;
  --color-success: #67c23a;
  --color-warning: #ff9500;
  --color-danger: #ff3b30;
  --color-info: #909399;
  --color-text: #1d1d1f;
  --color-text-secondary: #86868b;
  --color-text-tertiary: #b8b8b8;
  --color-border: #d2d2d7;
  --color-background: #f5f5f7;
  --color-white: #ffffff;
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 18px;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
}

.admin-layout {
  display: flex;
  min-height: 100vh;
}

.admin-sidebar {
  width: 200px;
  background: #001529;
  flex-shrink: 0;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
}

.admin-sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.admin-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.admin-logo .logo-icon {
  font-size: 24px;
  color: var(--color-primary);
}

.admin-menu {
  padding: 12px 0;
}

.admin-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.65);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
}

.admin-menu-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.08);
}

.admin-menu-item.router-link-active {
  color: white;
  background: var(--color-primary);
}

.admin-menu-item .menu-icon {
  font-size: 16px;
}

.admin-main {
  flex: 1;
  margin-left: 200px;
  display: flex;
  flex-direction: column;
}

.admin-header {
  height: 60px;
  background: white;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.admin-header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
}

.admin-username {
  font-weight: 500;
  color: var(--color-text);
}

.admin-content {
  flex: 1;
  padding: 24px;
  background: #f0f2f5;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.card {
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: 24px;
}

.stat-card {
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-icon.primary {
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
}

.stat-icon.success {
  background: rgba(103, 194, 58, 0.1);
  color: var(--color-success);
}

.stat-icon.warning {
  background: rgba(255, 149, 0, 0.1);
  color: var(--color-warning);
}

.stat-icon.danger {
  background: rgba(255, 59, 48, 0.1);
  color: var(--color-danger);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.search-bar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.search-bar .el-input {
  width: 200px;
}

.search-bar .el-select {
  width: 150px;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 4px 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  font-size: 14px;
}

.action-btn.edit {
  color: var(--color-primary);
}

.action-btn.edit:hover {
  background: rgba(0, 113, 227, 0.1);
}

.action-btn.delete {
  color: var(--color-danger);
}

.action-btn.delete:hover {
  background: rgba(255, 59, 48, 0.1);
}

.tag-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.tag-badge.active {
  background: rgba(103, 194, 58, 0.1);
  color: var(--color-success);
}

.tag-badge.inactive {
  background: rgba(144, 147, 153, 0.1);
  color: var(--color-info);
}

.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

-login-logo {
  font-size: 48px;
  color: var(--color-primary);
  margin-bottom: 16px;
}

.login-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.login-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 8px;
}

.login-form {
  margin-top: 24px;
}

.login-form-item {
  margin-bottom: 20px;
}

.login-form-item .el-input__wrapper {
  padding: 12px 16px;
}

.login-form-item .el-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  border-radius: var(--radius-md);
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.dialog-header {
  margin-bottom: 16px;
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.color-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-preview {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
}

.color-input {
  flex: 1;
}

.empty-wrapper {
  padding: 40px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  color: var(--color-text-tertiary);
  margin-bottom: 16px;
}

.empty-text {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.loading-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

@media (max-width: 768px) {
  .admin-sidebar {
    width: 60px;
  }
  
  .admin-main {
    margin-left: 60px;
  }
  
  .admin-menu-item span {
    display: none;
  }
  
  .admin-logo span {
    display: none;
  }
  
  .login-card {
    width: 90%;
    padding: 24px;
  }
}
</style>
