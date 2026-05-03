<template>
  <div class="profile-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">个人中心</h1>
      </div>

      <div class="tab-nav">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'profile' }"
          @click="activeTab = 'profile'"
        >
          账户信息
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'points' }"
          @click="activeTab = 'points'"
        >
          积分中心
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'invite' }"
          @click="activeTab = 'invite'"
        >
          邀请好友
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'favorites' }"
          @click="activeTab = 'favorites'"
        >
          我的收藏
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'edit-logs' }"
          @click="activeTab = 'edit-logs'"
        >
          编辑日志
        </button>
      </div>

      <div class="profile-grid" v-if="user" v-show="activeTab === 'profile'">
        <div class="profile-card card">
          <div class="profile-header">
            <div class="avatar-wrapper" @click="triggerAvatarUpload">
              <div class="avatar-display">
                <img v-if="user.avatar" :src="`/uploads/${user.avatar}`" alt="头像" class="avatar-img" />
                <el-icon v-else><User /></el-icon>
              </div>
              <div class="avatar-overlay">
                <el-icon><Camera /></el-icon>
                <span>更换头像</span>
              </div>
              <input 
                type="file" 
                ref="avatarInput" 
                @change="handleAvatarChange" 
                accept="image/*"
                style="display: none"
              />
            </div>
            <div class="profile-info">
              <h2 class="username">{{ user.username }}</h2>
              <span class="level-badge" :class="user.level">{{ user.level_name }}</span>
            </div>
          </div>

          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ user.posts_count }}</div>
              <div class="stat-label">已发布</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ user.posts_limit - user.posts_count }}</div>
              <div class="stat-label">剩余额度</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">¥{{ user.balance }}</div>
              <div class="stat-label">账户余额</div>
            </div>
            <div class="stat-item">
              <div class="stat-value points-value">{{ user.points || 0 }}</div>
              <div class="stat-label">积分</div>
            </div>
          </div>

          <div class="info-section">
            <h3 class="section-title">账户信息</h3>
            <div class="info-list">
              <div class="info-item">
                <span class="info-label">用户名</span>
                <span class="info-value">{{ user.username }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">邮箱</span>
                <span class="info-value">{{ user.email || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">会员等级</span>
                <span class="info-value">{{ user.level_name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">注册时间</span>
                <span class="info-value">{{ user.created_at }}</span>
              </div>
            </div>
          </div>

          <div class="password-section">
            <h3 class="section-title">修改密码</h3>
            <form class="password-form" @submit.prevent="changePassword">
              <div class="form-group">
                <label class="form-label">原密码</label>
                <input 
                  type="password" 
                  v-model="passwordForm.oldPassword" 
                  class="form-input"
                  placeholder="请输入原密码"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">新密码</label>
                <input 
                  type="password" 
                  v-model="passwordForm.newPassword" 
                  class="form-input"
                  placeholder="请输入新密码（至少6位）"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">确认新密码</label>
                <input 
                  type="password" 
                  v-model="passwordForm.confirmPassword" 
                  class="form-input"
                  placeholder="请再次输入新密码"
                  required
                />
              </div>
              <button type="submit" class="btn-primary" :disabled="changingPassword">
                <span v-if="!changingPassword">确认修改</span>
                <span v-else>修改中...</span>
              </button>
            </form>
          </div>

          <div class="action-buttons">
            <router-link to="/recharge" class="btn-primary">
              <el-icon><Wallet /></el-icon>
              充值
            </router-link>
            <router-link to="/upgrade" class="btn-secondary">
              <el-icon><TrendCharts /></el-icon>
              升级会员
            </router-link>
          </div>
        </div>

        <div class="transactions-card card" v-if="transactions.length > 0">
          <h3 class="section-title">交易记录</h3>
          <div class="transactions-list">
            <div 
              v-for="tx in transactions" 
              :key="tx.id"
              class="transaction-item"
            >
              <div class="tx-info">
                <div class="tx-type" :class="tx.transaction_type">
                  <el-icon v-if="tx.transaction_type === 'recharge'"><Plus /></el-icon>
                  <el-icon v-else><Minus /></el-icon>
                </div>
                <div class="tx-content">
                  <div class="tx-description">{{ tx.description }}</div>
                  <div class="tx-time">{{ tx.created_at }}</div>
                </div>
              </div>
              <div class="tx-amount" :class="tx.transaction_type">
                {{ tx.transaction_type === 'recharge' ? '+' : '' }}¥{{ tx.amount }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="points-section" v-show="activeTab === 'points'">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon><Coin /></el-icon>
            积分中心
          </h3>
        </div>

        <div class="points-overview card">
          <div class="points-header">
            <div class="points-info">
              <div class="points-display">
                <span class="points-label">当前积分</span>
                <span class="points-amount">{{ user?.points || 0 }}</span>
              </div>
              <div class="checkin-status" v-if="checkinStatus">
                <span class="checkin-days">连续签到 {{ checkinStatus.continuous_days || 0 }} 天</span>
                <button 
                  class="checkin-btn" 
                  :class="{ 'checked-in': checkinStatus.has_checked_in }"
                  @click="handleCheckin"
                  :disabled="checkinStatus.has_checked_in || checkingIn"
                >
                  <span v-if="checkingIn">签到中...</span>
                  <span v-else-if="checkinStatus.has_checked_in">今日已签到</span>
                  <span v-else>立即签到</span>
                </button>
              </div>
            </div>
          </div>

          <div class="checkin-rules" v-if="checkinStatus?.config">
            <div class="rules-title">签到奖励规则</div>
            <div class="rules-grid">
              <div class="rule-item">
                <span class="rule-label">每日签到</span>
                <span class="rule-value">+{{ checkinStatus.config.daily_checkin_points }} 积分</span>
              </div>
              <div class="rule-item">
                <span class="rule-label">连续签到奖励</span>
                <span class="rule-value">每天 +{{ checkinStatus.config.continuous_bonus_base }} 积分</span>
              </div>
              <div class="rule-item">
                <span class="rule-label">最多连续</span>
                <span class="rule-value">{{ checkinStatus.config.max_continuous_days }} 天</span>
              </div>
            </div>
          </div>
        </div>

        <div class="exchange-section card">
          <h3 class="section-title">积分兑换</h3>
          <div class="exchange-grid">
            <div class="exchange-item">
              <div class="exchange-icon">
                <el-icon><Wallet /></el-icon>
              </div>
              <div class="exchange-info">
                <div class="exchange-title">兑换余额</div>
                <div class="exchange-rate">
                  {{ checkinStatus?.config?.points_to_balance_rate || 100 }} 积分 = {{ checkinStatus?.config?.balance_per_exchange || 1 }} 元
                </div>
              </div>
              <div class="exchange-action">
                <el-input-number 
                  v-model="exchangeBalanceCount" 
                  :min="1"
                  :max="10"
                  size="small"
                />
                <el-button 
                  type="primary" 
                  size="small"
                  @click="handleExchangeBalance"
                  :disabled="exchanging"
                >
                  兑换
                </el-button>
              </div>
            </div>

            <div class="exchange-item">
              <div class="exchange-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="exchange-info">
                <div class="exchange-title">兑换发布额度</div>
                <div class="exchange-rate">
                  {{ checkinStatus?.config?.points_to_posts_rate || 50 }} 积分 = {{ checkinStatus?.config?.posts_per_exchange || 1 }} 个
                </div>
              </div>
              <div class="exchange-action">
                <el-input-number 
                  v-model="exchangePostsCount" 
                  :min="1"
                  :max="10"
                  size="small"
                />
                <el-button 
                  type="primary" 
                  size="small"
                  @click="handleExchangePosts"
                  :disabled="exchanging"
                >
                  兑换
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <div class="points-transactions-section card">
          <h3 class="section-title">积分记录</h3>
          <div class="points-transactions-list" v-if="pointsTransactions.length > 0">
            <div 
              v-for="pt in pointsTransactions" 
              :key="pt.id"
              class="points-transaction-item"
            >
              <div class="pt-info">
                <div class="pt-type" :class="pt.points > 0 ? 'income' : 'expense'">
                  <el-icon v-if="pt.points > 0"><Plus /></el-icon>
                  <el-icon v-else><Minus /></el-icon>
                </div>
                <div class="pt-content">
                  <div class="pt-description">{{ pt.description || pt.type_name }}</div>
                  <div class="pt-time">{{ pt.created_at }}</div>
                </div>
              </div>
              <div class="pt-amount" :class="pt.points > 0 ? 'income' : 'expense'">
                {{ pt.points > 0 ? '+' : '' }}{{ pt.points }}
              </div>
            </div>
          </div>
          <div class="empty-state" v-else-if="!loadingPointsTransactions">
            <p>暂无积分记录</p>
          </div>
        </div>
      </div>

      <div class="invite-section" v-show="activeTab === 'invite'">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon><Share /></el-icon>
            邀请好友
          </h3>
        </div>

        <div class="invite-overview card">
          <div class="invite-header">
            <div class="invite-info">
              <div class="invite-stats">
                <div class="stat-item">
                  <div class="stat-value">{{ inviteInfo?.total_invited || 0 }}</div>
                  <div class="stat-label">已邀请用户</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">¥{{ inviteInfo?.total_reward || 0 }}</div>
                  <div class="stat-label">累计奖励</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ inviteInfo?.unclaimed_count || 0 }}</div>
                  <div class="stat-label">待领取奖励</div>
                </div>
              </div>
            </div>
          </div>

          <div class="invite-rules" v-if="inviteConfig">
            <div class="rules-title">邀请奖励规则</div>
            <div class="rules-desc">
              <p>每成功邀请一位好友注册，您将获得 <span class="highlight">¥{{ inviteConfig.invite_reward_balance }}</span> 奖励</p>
              <p>被邀请的新用户也将获得 <span class="highlight">{{ inviteConfig.invited_new_user_bonus }}</span> 积分奖励</p>
            </div>
          </div>
        </div>

        <div class="invite-code-section card">
          <h3 class="section-title">我的邀请码</h3>
          <div class="invite-code-display">
            <div class="invite-code">{{ inviteInfo?.invite_code || '加载中...' }}</div>
            <div class="invite-actions">
              <el-button 
                type="primary" 
                @click="copyInviteCode"
                :loading="copyingInviteCode"
              >
                <el-icon><CopyDocument /></el-icon>
                复制邀请码
              </el-button>
              <el-button 
                @click="generateShareLink"
                :loading="generatingLink"
              >
                <el-icon><Link /></el-icon>
                生成邀请链接
              </el-button>
              <el-button 
                @click="generateInviteQRCode"
                :loading="generatingQRCode"
              >
                <el-icon><Picture /></el-icon>
                生成二维码
              </el-button>
            </div>
          </div>

          <el-dialog 
            v-model="showQRCodeDialog" 
            title="邀请二维码"
            width="400px"
          >
            <div class="qrcode-display">
              <img v-if="qrcodeImage" :src="qrcodeImage" alt="邀请二维码" class="qrcode-img" />
              <p class="qrcode-desc">扫描二维码即可注册成为您的邀请用户</p>
            </div>
            <template #footer>
              <el-button @click="showQRCodeDialog = false">关闭</el-button>
              <el-button type="primary" @click="downloadQRCode">
                <el-icon><Download /></el-icon>
                保存二维码
              </el-button>
            </template>
          </el-dialog>

          <el-dialog 
            v-model="showShareLinkDialog" 
            title="邀请链接"
            width="500px"
          >
            <div class="share-link-display">
              <div class="share-link-preview">
                <div class="share-link-title" v-if="shareInfo?.title">{{ shareInfo.title }}</div>
                <div class="share-link-desc" v-if="shareInfo?.description">{{ shareInfo.description }}</div>
                <div class="share-link-url">
                  <el-input 
                    :value="shareInfo?.url" 
                    readonly
                    placeholder="点击生成邀请链接"
                  >
                    <template #append>
                      <el-button 
                        @click="copyShareLink"
                        :disabled="!shareInfo?.url"
                      >
                        <el-icon><CopyDocument /></el-icon>
                        复制
                      </el-button>
                    </template>
                  </el-input>
                </div>
              </div>
            </div>
          </el-dialog>
        </div>

        <div class="invite-records-section card">
          <div class="records-header">
            <h3 class="section-title">邀请记录</h3>
            <el-button 
              v-if="inviteInfo?.unclaimed_count > 0"
              type="primary" 
              size="small"
              @click="claimAllRewards"
              :disabled="claimingRewards"
            >
              <el-icon><Wallet /></el-icon>
              领取所有奖励
            </el-button>
          </div>
          
          <div class="invite-records-list" v-if="inviteRecords.length > 0">
            <div 
              v-for="record in inviteRecords" 
              :key="record.id"
              class="invite-record-item"
            >
              <div class="record-user">
                <div class="user-avatar">
                  <img v-if="record.invited_user?.avatar" :src="`/uploads/${record.invited_user.avatar}`" alt="" class="avatar-img" />
                  <el-icon v-else><User /></el-icon>
                </div>
                <div class="user-info">
                  <div class="username">{{ record.invited_user?.username || '未知用户' }}</div>
                  <div class="register-time">注册时间: {{ record.created_at }}</div>
                </div>
              </div>
              <div class="record-reward">
                <div class="reward-amount" :class="record.reward_claimed ? 'claimed' : 'unclaimed'">
                  ¥{{ record.reward_amount || 0 }}
                </div>
                <el-button 
                  v-if="!record.reward_claimed"
                  type="primary" 
                  size="small"
                  @click="claimReward(record)"
                  :disabled="claimingRewards"
                >
                  领取
                </el-button>
                <span v-else class="claimed-text">已领取</span>
              </div>
            </div>
          </div>
          <div class="empty-state" v-else-if="!loadingInviteRecords">
            <p>暂无邀请记录，快去邀请好友吧！</p>
          </div>
        </div>
      </div>

      <div class="favorites-section" v-show="activeTab === 'favorites'">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon><Star /></el-icon>
            我的收藏
          </h3>
        </div>

        <div class="posts-list" v-if="favorites.length > 0">
          <div 
            v-for="post in favorites" 
            :key="post.id" 
            class="post-item card"
            @click="goToPost(post.id)"
          >
            <div class="post-main">
              <div class="post-header-row">
                <h3 class="post-title">{{ post.title }}</h3>
                <span 
                  class="favorite-btn favorited" 
                  @click.stop="unfavorite(post)"
                  title="取消收藏"
                >
                  <el-icon><Star /></el-icon>
                </span>
              </div>
              <p class="post-excerpt">{{ truncate(post.content, 120) }}</p>
              
              <div class="post-images" v-if="post.images?.length > 0">
                <div class="image-grid">
                  <img 
                    v-for="(img, imgIndex) in post.images.slice(0, 3)" 
                    :key="imgIndex"
                    :src="`/uploads/${img}`"
                    class="post-image"
                    alt="图片"
                  />
                </div>
              </div>
            </div>

            <div class="post-footer-row">
              <div class="post-meta-left">
                <span class="author-name">{{ post.author?.username }}</span>
                <span class="stat-item">
                  <el-icon><View /></el-icon>
                  {{ post.views_count }}
                </span>
              </div>
              <span class="post-time">{{ formatTime(post.favorited_at || post.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="empty-state" v-else-if="!loadingFavorites">
          <div class="empty-icon">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3 class="empty-title">暂无收藏</h3>
          <p class="empty-desc">
            去首页发现感兴趣的公告，点击星星图标即可收藏
          </p>
          <router-link to="/" class="btn-primary">
            <el-icon><ArrowRight /></el-icon>
            去首页
          </router-link>
        </div>

        <div class="loading-state" v-else>
          <div class="loading-spinner">
            <div class="spinner-circle"></div>
          </div>
          <p>加载中...</p>
        </div>

        <div class="load-more" v-if="hasMoreFavorites && !loadingFavorites">
          <button class="load-more-btn" @click="loadMoreFavorites" :disabled="loadingFavorites">
            <span v-if="!loadingFavorites">加载更多</span>
            <span v-else>加载中...</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </button>
        </div>
      </div>

      <div class="edit-logs-section" v-show="activeTab === 'edit-logs'">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon><Document /></el-icon>
            编辑日志
          </h3>
        </div>

        <div class="edit-logs-list" v-if="editLogs.length > 0">
          <div 
            v-for="log in editLogs" 
            :key="log.id"
            class="edit-log-item card"
          >
            <div class="log-header">
              <div class="log-post-title">
                <router-link :to="`/post/${log.post_id}`" class="post-link">
                  {{ log.post?.title || '该帖子已删除' }}
                </router-link>
              </div>
              <span class="log-time">{{ formatTime(log.created_at) }}</span>
            </div>
            
            <div class="log-changes">
              <span class="changes-badge">{{ log.changes_summary }}</span>
            </div>
            
            <div class="log-reason" v-if="log.edit_reason">
              <span class="reason-label">修改原因：</span>
              <span class="reason-text">{{ log.edit_reason }}</span>
            </div>

            <el-divider v-if="!log.has_title_changed && !log.has_content_changed" />
            <div class="log-details" v-else>
              <div class="detail-section" v-if="log.has_title_changed">
                <div class="detail-label">标题修改</div>
                <div class="detail-before">
                  <span class="change-label">修改前：</span>
                  <span class="before-text">{{ log.title_before || '-' }}</span>
                </div>
                <div class="detail-after">
                  <span class="change-label">修改后：</span>
                  <span class="after-text">{{ log.title_after || '-' }}</span>
                </div>
              </div>

              <div class="detail-section" v-if="log.has_content_changed">
                <div class="detail-label">内容修改</div>
                <div class="content-compare">
                  <div class="compare-col">
                    <div class="compare-header">修改前</div>
                    <div class="compare-content before">
                      {{ truncate(log.content_before, 200) }}
                    </div>
                  </div>
                  <div class="compare-col">
                    <div class="compare-header">修改后</div>
                    <div class="compare-content after">
                      {{ truncate(log.content_after, 200) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="empty-state" v-else-if="!loadingEditLogs">
          <div class="empty-icon">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M14 2V8H20" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 13H8" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 17H8" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M10 9H9H8" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3 class="empty-title">暂无编辑记录</h3>
          <p class="empty-desc">
            您还没有编辑过任何帖子，编辑后的修改记录将在这里显示
          </p>
        </div>

        <div class="loading-state" v-else>
          <div class="loading-spinner">
            <div class="spinner-circle"></div>
          </div>
          <p>加载中...</p>
        </div>

        <div class="load-more" v-if="hasMoreEditLogs && !loadingEditLogs">
          <button class="load-more-btn" @click="loadMoreEditLogs" :disabled="loadingEditLogs">
            <span v-if="!loadingEditLogs">加载更多</span>
            <span v-else>加载中...</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, Wallet, TrendCharts, Plus, Minus, Camera, Star, View, ArrowDown, ArrowRight, Document,
  Coin, Share, CopyDocument, Link, Picture, Download
} from '@element-plus/icons-vue'
import { userApi, postApi, shareApi } from '../services/api'

const router = useRouter()

const activeTab = ref('profile')
const user = ref(null)
const transactions = ref([])
const avatarInput = ref(null)
const uploadingAvatar = ref(false)
const changingPassword = ref(false)

const favorites = ref([])
const loadingFavorites = ref(false)
const favoritesPage = ref(1)
const hasMoreFavorites = ref(true)

const editLogs = ref([])
const loadingEditLogs = ref(false)
const editLogsPage = ref(1)
const hasMoreEditLogs = ref(true)

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const checkinStatus = ref(null)
const checkingIn = ref(false)
const exchangeBalanceCount = ref(1)
const exchangePostsCount = ref(1)
const exchanging = ref(false)
const pointsTransactions = ref([])
const loadingPointsTransactions = ref(false)

const inviteInfo = ref(null)
const inviteConfig = ref(null)
const inviteRecords = ref([])
const loadingInviteRecords = ref(false)
const copyingInviteCode = ref(false)
const generatingLink = ref(false)
const generatingQRCode = ref(false)
const claimingRewards = ref(false)
const showQRCodeDialog = ref(false)
const showShareLinkDialog = ref(false)
const qrcodeImage = ref('')
const shareInfo = ref(null)

const loadProfile = async () => {
  try {
    const response = await userApi.getProfile()
    if (response.data.success) {
      user.value = response.data.user
      transactions.value = response.data.transactions
    }
  } catch (error) {
    console.error('加载个人信息失败:', error)
  }
}

const loadFavorites = async (append = false) => {
  if (loadingFavorites.value) return
  loadingFavorites.value = true
  
  try {
    const response = await userApi.getFavorites({
      page: favoritesPage.value,
      per_page: 20
    })
    
    if (response.data.success) {
      const newPosts = response.data.posts
      if (append) {
        favorites.value = [...favorites.value, ...newPosts]
      } else {
        favorites.value = newPosts
      }
      hasMoreFavorites.value = response.data.has_more
    }
  } catch (error) {
    console.error('加载收藏失败:', error)
  } finally {
    loadingFavorites.value = false
  }
}

const loadMoreFavorites = () => {
  favoritesPage.value++
  loadFavorites(true)
}

const loadEditLogs = async (append = false) => {
  if (loadingEditLogs.value) return
  loadingEditLogs.value = true
  
  try {
    const response = await userApi.getEditLogs({
      page: editLogsPage.value,
      per_page: 20
    })
    
    if (response.data.success) {
      const newLogs = response.data.edit_logs
      if (append) {
        editLogs.value = [...editLogs.value, ...newLogs]
      } else {
        editLogs.value = newLogs
      }
      hasMoreEditLogs.value = (editLogsPage.value * 20) < response.data.total
    }
  } catch (error) {
    console.error('加载编辑日志失败:', error)
  } finally {
    loadingEditLogs.value = false
  }
}

const loadMoreEditLogs = () => {
  editLogsPage.value++
  loadEditLogs(true)
}

const unfavorite = async (post) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消收藏这条公告吗？',
      '确认取消',
      {
        confirmButtonText: '确定取消',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await postApi.toggleFavorite(post.id)
    if (response.data.success) {
      ElMessage.success('已取消收藏')
      favorites.value = favorites.value.filter(p => p.id !== post.id)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消收藏失败:', error)
    }
  }
}

const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}

const handleAvatarChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 JPG、PNG、GIF 格式的图片')
    return
  }
  
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }
  
  uploadingAvatar.value = true
  try {
    const formData = new FormData()
    formData.append('avatar', file)
    
    const response = await userApi.uploadAvatar(formData)
    if (response.data.success) {
      ElMessage.success('头像上传成功')
      user.value = response.data.user
    }
  } catch (error) {
    console.error('上传头像失败:', error)
  } finally {
    uploadingAvatar.value = false
    if (avatarInput.value) {
      avatarInput.value.value = ''
    }
  }
}

const changePassword = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    ElMessage.warning('请填写所有字段')
    return
  }
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  
  if (passwordForm.newPassword.length < 6) {
    ElMessage.warning('新密码长度不能少于6位')
    return
  }
  
  changingPassword.value = true
  try {
    const response = await userApi.changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword,
      confirm_password: passwordForm.confirmPassword
    })
    
    if (response.data.success) {
      ElMessage.success('密码修改成功')
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    changingPassword.value = false
  }
}

const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}

const truncate = (text, length) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.slice(0, length) + '...'
}

const formatTime = (time) => {
  if (!time) return ''
  return time.replace(' GMT', '')
}

const loadCheckinStatus = async () => {
  try {
    const response = await userApi.getCheckinStatus()
    if (response.data.success) {
      checkinStatus.value = response.data.data
      if (response.data.config) {
        checkinStatus.value.config = response.data.config
      }
    }
  } catch (error) {
    console.error('加载签到状态失败:', error)
  }
}

const handleCheckin = async () => {
  if (checkinStatus.value?.has_checked_in || checkingIn.value) return
  
  checkingIn.value = true
  try {
    const response = await userApi.checkin()
    if (response.data.success) {
      ElMessage.success(`签到成功！获得 ${response.data.data.points} 积分`)
      checkinStatus.value = response.data.data
      if (response.data.config) {
        checkinStatus.value.config = response.data.config
      }
      user.value.points = (user.value.points || 0) + response.data.data.points
      loadPointsTransactions()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '签到失败')
  } finally {
    checkingIn.value = false
  }
}

const loadPointsTransactions = async () => {
  loadingPointsTransactions.value = true
  try {
    const response = await userApi.getPointsTransactions({
      page: 1,
      per_page: 20
    })
    if (response.data.success) {
      pointsTransactions.value = response.data.transactions || []
    }
  } catch (error) {
    console.error('加载积分记录失败:', error)
  } finally {
    loadingPointsTransactions.value = false
  }
}

const handleExchangeBalance = async () => {
  if (exchanging.value) return
  
  const pointsNeeded = (checkinStatus.value?.config?.points_to_balance_rate || 100) * exchangeBalanceCount.value
  if ((user.value?.points || 0) < pointsNeeded) {
    ElMessage.warning(`积分不足，需要 ${pointsNeeded} 积分`)
    return
  }
  
  exchanging.value = true
  try {
    const response = await userApi.exchangePointsToBalance({
      count: exchangeBalanceCount.value
    })
    if (response.data.success) {
      ElMessage.success(`兑换成功！获得 ¥${exchangeBalanceCount.value}`)
      user.value.points = response.data.user.points
      user.value.balance = response.data.user.balance
      loadPointsTransactions()
      loadProfile()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '兑换失败')
  } finally {
    exchanging.value = false
  }
}

const handleExchangePosts = async () => {
  if (exchanging.value) return
  
  const pointsNeeded = (checkinStatus.value?.config?.points_to_posts_rate || 50) * exchangePostsCount.value
  if ((user.value?.points || 0) < pointsNeeded) {
    ElMessage.warning(`积分不足，需要 ${pointsNeeded} 积分`)
    return
  }
  
  exchanging.value = true
  try {
    const response = await userApi.exchangePointsToPosts({
      count: exchangePostsCount.value
    })
    if (response.data.success) {
      ElMessage.success(`兑换成功！获得 ${exchangePostsCount.value} 个发布额度`)
      user.value.points = response.data.user.points
      user.value.posts_limit = response.data.user.posts_limit
      loadPointsTransactions()
      loadProfile()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '兑换失败')
  } finally {
    exchanging.value = false
  }
}

const loadInviteInfo = async () => {
  try {
    const response = await userApi.getInviteInfo()
    if (response.data.success) {
      inviteInfo.value = response.data.data
      inviteConfig.value = response.data.config
    }
  } catch (error) {
    console.error('加载邀请信息失败:', error)
  }
}

const loadInviteRecords = async () => {
  loadingInviteRecords.value = true
  try {
    const response = await userApi.getInviteRecords({
      page: 1,
      per_page: 20
    })
    if (response.data.success) {
      inviteRecords.value = response.data.records || []
    }
  } catch (error) {
    console.error('加载邀请记录失败:', error)
  } finally {
    loadingInviteRecords.value = false
  }
}

const copyInviteCode = async () => {
  if (!inviteInfo.value?.invite_code) return
  
  copyingInviteCode.value = true
  try {
    await navigator.clipboard.writeText(inviteInfo.value.invite_code)
    ElMessage.success('邀请码已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  } finally {
    copyingInviteCode.value = false
  }
}

const generateShareLink = async () => {
  if (generatingLink.value) return
  
  generatingLink.value = true
  try {
    const response = await shareApi.getShareLink('invite', user.value.id)
    if (response.data.success) {
      shareInfo.value = response.data.data
      showShareLinkDialog.value = true
    }
  } catch (error) {
    ElMessage.error('生成分享链接失败')
  } finally {
    generatingLink.value = false
  }
}

const copyShareLink = async () => {
  if (!shareInfo.value?.url) return
  
  try {
    await navigator.clipboard.writeText(shareInfo.value.url)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const generateInviteQRCode = async () => {
  if (generatingQRCode.value) return
  
  generatingQRCode.value = true
  try {
    const shareResponse = await shareApi.getShareLink('invite', user.value.id)
    if (shareResponse.data.success) {
      const qrResponse = await shareApi.getQRCode(shareResponse.data.data.url)
      if (qrResponse.data.success) {
        qrcodeImage.value = qrResponse.data.data.image
        showQRCodeDialog.value = true
      }
    }
  } catch (error) {
    ElMessage.error('生成二维码失败')
  } finally {
    generatingQRCode.value = false
  }
}

const downloadQRCode = () => {
  if (!qrcodeImage.value) return
  
  const link = document.createElement('a')
  link.href = qrcodeImage.value
  link.download = `invite-qrcode-${inviteInfo.value?.invite_code || 'code'}.png`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('二维码已下载')
}

const claimReward = async (record) => {
  if (claimingRewards.value || record.reward_claimed) return
  
  claimingRewards.value = true
  try {
    const response = await userApi.claimInviteReward(record.id)
    if (response.data.success) {
      ElMessage.success(`领取成功！获得 ¥${record.reward_amount}`)
      record.reward_claimed = true
      loadInviteInfo()
      loadProfile()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '领取失败')
  } finally {
    claimingRewards.value = false
  }
}

const claimAllRewards = async () => {
  if (claimingRewards.value) return
  
  const unclaimedRecords = inviteRecords.value.filter(r => !r.reward_claimed)
  if (unclaimedRecords.length === 0) {
    ElMessage.warning('没有可领取的奖励')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要领取 ${unclaimedRecords.length} 个奖励吗？`,
      '确认领取',
      {
        confirmButtonText: '确定领取',
        cancelButtonText: '取消',
        type: 'success'
      }
    )
    
    claimingRewards.value = true
    const response = await userApi.claimAllInviteRewards()
    if (response.data.success) {
      ElMessage.success(response.data.message)
      unclaimedRecords.forEach(r => {
        r.reward_claimed = true
      })
      loadInviteInfo()
      loadProfile()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '领取失败')
    }
  } finally {
    claimingRewards.value = false
  }
}

watch(activeTab, (newTab) => {
  if (newTab === 'points') {
    if (!checkinStatus.value) {
      loadCheckinStatus()
    }
    if (pointsTransactions.value.length === 0) {
      loadPointsTransactions()
    }
  } else if (newTab === 'invite') {
    if (!inviteInfo.value) {
      loadInviteInfo()
    }
    if (inviteRecords.value.length === 0) {
      loadInviteRecords()
    }
  }
})

onMounted(() => {
  loadProfile()
  loadFavorites()
  loadEditLogs()
})
</script>

<style scoped>
.profile-page {
  flex: 1;
  padding: 40px 0;
  background: var(--color-background);
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.003em;
  margin: 0;
  color: var(--color-text);
}

.tab-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  padding: 4px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: var(--radius-md);
  width: fit-content;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  color: var(--color-text);
}

.tab-btn.active {
  background: white;
  color: var(--color-text);
  font-weight: var(--font-weight-medium);
  box-shadow: var(--shadow-sm);
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.profile-card {
  padding: 32px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.avatar-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  cursor: pointer;
}

.avatar-display {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, #5856d6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 36px;
  overflow: hidden;
}

.avatar-display .avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.avatar-overlay span {
  font-size: 12px;
  margin-top: 4px;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.profile-info {
  flex: 1;
}

.username {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--color-text);
}

.level-badge {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 500;
}

.level-badge.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #a0522d 100%);
  color: white;
}

.level-badge.silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #a9a9a9 100%);
  color: #1d1d1f;
}

.level-badge.gold {
  background: var(--gradient-gold);
  color: #1d1d1f;
}

.level-badge.black {
  background: var(--gradient-dark);
  color: white;
}

.level-badge.diamond {
  background: linear-gradient(135deg, #b9f2ff 0%, #64d2ff 100%);
  color: #1d1d1f;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  margin: 0 0 16px;
  color: var(--color-text);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 15px;
  color: var(--color-text-secondary);
}

.info-value {
  font-size: 15px;
  color: var(--color-text);
  font-weight: 500;
}

.password-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.form-input {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  outline: none;
  transition: border-color var(--transition-fast);
}

.form-input:focus {
  border-color: var(--color-primary);
}

.form-input::placeholder {
  color: var(--color-text-tertiary);
}

.password-form .btn-primary {
  align-self: flex-start;
  padding: 12px 32px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.password-form .btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.action-buttons .btn-primary,
.action-buttons .btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: center;
  padding: 12px 24px;
  border-radius: var(--radius-md);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
}

.action-buttons .btn-primary {
  background: var(--color-primary);
  color: white;
}

.action-buttons .btn-primary:hover {
  background: var(--color-primary-hover);
}

.action-buttons .btn-secondary {
  background: rgba(0, 0, 0, 0.04);
  color: var(--color-text);
}

.action-buttons .btn-secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}

.transactions-card {
  padding: 32px;
}

.transactions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.transaction-item:last-child {
  border-bottom: none;
}

.tx-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tx-type {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.tx-type.recharge {
  background: rgba(52, 199, 89, 0.1);
  color: var(--color-success);
}

.tx-type.upgrade {
  background: rgba(255, 59, 48, 0.1);
  color: var(--color-danger);
}

.tx-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tx-description {
  font-size: 15px;
  color: var(--color-text);
}

.tx-time {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.tx-amount {
  font-size: 17px;
  font-weight: 600;
}

.tx-amount.recharge {
  color: var(--color-success);
}

.tx-amount.upgrade {
  color: var(--color-danger);
}

.favorites-section {
  width: 100%;
}

.favorites-section .section-header {
  margin-bottom: 24px;
}

.favorites-section .section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-xl);
}

.favorites-section .section-title .el-icon {
  color: var(--color-danger);
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-item {
  width: 100%;
  padding: 20px 24px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.post-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary);
}

.post-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.post-title {
  flex: 1;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  line-height: 1.4;
  margin: 0;
  color: var(--color-text);
  transition: color var(--transition-fast);
}

.post-item:hover .post-title {
  color: var(--color-primary);
}

.post-excerpt {
  font-size: var(--font-size-sm);
  line-height: 1.6;
  color: var(--color-text-secondary);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-images {
  margin-top: 8px;
}

.image-grid {
  display: flex;
  gap: 8px;
  overflow: hidden;
}

.post-image {
  width: 72px;
  height: 72px;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: var(--color-background);
}

.post-footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-light);
}

.post-meta-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.author-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.post-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.favorite-btn {
  cursor: pointer;
  transition: all var(--transition-fast);
  padding: 4px;
  border-radius: var(--radius-sm);
  color: var(--color-text-tertiary);
}

.favorite-btn:hover {
  background: rgba(255, 59, 48, 0.1);
  color: var(--color-danger);
}

.favorite-btn.favorited {
  color: var(--color-danger);
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

.empty-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 8px;
  color: var(--color-text);
}

.empty-desc {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0 0 24px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.spinner-circle {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border-light);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.load-more {
  text-align: center;
  margin-top: 48px;
}

.load-more-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 40px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  font-size: var(--font-size-base);
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.load-more-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.arrow-icon {
  transition: transform var(--transition-fast);
}

.load-more-btn:hover .arrow-icon {
  transform: translateY(2px);
}

.edit-logs-section {
  width: 100%;
}

.edit-logs-section .section-header {
  margin-bottom: 24px;
}

.edit-logs-section .section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-xl);
}

.edit-logs-section .section-title .el-icon {
  color: var(--color-primary);
}

.edit-logs-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.edit-log-item {
  padding: 20px 24px;
  transition: all var(--transition-normal);
}

.edit-log-item:hover {
  box-shadow: var(--shadow-md);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 12px;
}

.log-post-title {
  flex: 1;
}

.post-link {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.post-link:hover {
  color: var(--color-primary);
}

.log-time {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.log-changes {
  margin-bottom: 12px;
}

.changes-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.log-reason {
  margin-bottom: 12px;
  padding: 12px;
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.reason-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.reason-text {
  font-size: var(--font-size-sm);
  color: var(--color-text);
  margin-left: 4px;
}

.log-details {
  margin-top: 12px;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  margin-bottom: 8px;
}

.detail-before,
.detail-after {
  padding: 8px 12px;
  border-radius: var(--radius-md);
  margin-bottom: 4px;
  font-size: var(--font-size-sm);
}

.detail-before {
  background: rgba(255, 59, 48, 0.05);
  border-left: 3px solid var(--color-danger);
}

.detail-after {
  background: rgba(52, 199, 89, 0.05);
  border-left: 3px solid var(--color-success);
}

.change-label {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin-right: 4px;
}

.before-text {
  color: var(--color-danger);
}

.after-text {
  color: var(--color-success);
}

.content-compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.compare-col {
  display: flex;
  flex-direction: column;
}

.compare-header {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: 8px 12px;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  margin-bottom: 0;
}

.compare-col:nth-child(1) .compare-header {
  background: rgba(255, 59, 48, 0.1);
  color: var(--color-danger);
}

.compare-col:nth-child(2) .compare-header {
  background: rgba(52, 199, 89, 0.1);
  color: var(--color-success);
}

.compare-content {
  padding: 12px;
  font-size: var(--font-size-sm);
  line-height: 1.6;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}

.compare-content.before {
  background: rgba(255, 59, 48, 0.03);
  border: 1px solid rgba(255, 59, 48, 0.1);
  text-decoration: line-through;
  opacity: 0.7;
}

.compare-content.after {
  background: rgba(52, 199, 89, 0.03);
  border: 1px solid rgba(52, 199, 89, 0.1);
}

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .post-item {
    padding: 16px;
  }
  
  .post-header-row {
    flex-direction: column;
    gap: 8px;
  }
  
  .post-footer-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .post-meta-left {
    width: 100%;
    justify-content: space-between;
  }
  
  .load-more-btn {
    width: 100%;
  }

  .log-header {
    flex-direction: column;
    gap: 8px;
  }
  
  .log-time {
    align-self: flex-start;
  }
  
  .content-compare {
    grid-template-columns: 1fr;
  }
  
  .edit-log-item {
    padding: 16px;
  }
}

.points-section,
.invite-section {
  width: 100%;
}

.section-header {
  margin-bottom: 24px;
}

.section-header .section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-xl);
}

.points-overview {
  padding: 32px;
  margin-bottom: 24px;
}

.points-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.points-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.points-display {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.points-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.points-amount {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-primary);
}

.points-value {
  color: var(--color-primary) !important;
}

.checkin-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.checkin-days {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.checkin-btn {
  padding: 12px 32px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--color-primary);
  color: white;
}

.checkin-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.checkin-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.checkin-btn.checked-in {
  background: var(--color-success);
}

.checkin-rules {
  padding: 16px;
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.rules-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 12px;
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.rule-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rule-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.rule-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary);
}

.exchange-section {
  padding: 32px;
  margin-bottom: 24px;
}

.exchange-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.exchange-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: var(--color-background);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}

.exchange-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(0, 113, 227, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  font-size: 24px;
}

.exchange-info {
  flex: 1;
  margin-left: 16px;
}

.exchange-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.exchange-rate {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.exchange-action {
  display: flex;
  align-items: center;
  gap: 12px;
}

.points-transactions-section {
  padding: 32px;
}

.points-transactions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.points-transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.points-transaction-item:last-child {
  border-bottom: none;
}

.pt-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pt-type {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.pt-type.income {
  background: rgba(52, 199, 89, 0.1);
  color: var(--color-success);
}

.pt-type.expense {
  background: rgba(255, 59, 48, 0.1);
  color: var(--color-danger);
}

.pt-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.pt-description {
  font-size: 15px;
  color: var(--color-text);
}

.pt-time {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.pt-amount {
  font-size: 17px;
  font-weight: 600;
}

.pt-amount.income {
  color: var(--color-success);
}

.pt-amount.expense {
  color: var(--color-danger);
}

.invite-overview {
  padding: 32px;
  margin-bottom: 24px;
}

.invite-header {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.invite-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.invite-stats .stat-item {
  text-align: center;
  padding: 20px;
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.invite-stats .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 4px;
}

.invite-stats .stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.invite-rules {
  padding: 16px;
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.invite-rules .rules-desc {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.invite-rules .rules-desc p {
  font-size: 14px;
  color: var(--color-text);
  margin: 0;
}

.invite-rules .highlight {
  color: var(--color-primary);
  font-weight: 600;
}

.invite-code-section {
  padding: 32px;
  margin-bottom: 24px;
}

.invite-code-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: var(--color-background);
  border-radius: var(--radius-md);
  border: 2px dashed var(--color-primary);
}

.invite-code {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 4px;
  font-family: 'Courier New', monospace;
}

.invite-actions {
  display: flex;
  gap: 12px;
}

.qrcode-display {
  text-align: center;
  padding: 24px;
}

.qrcode-img {
  width: 200px;
  height: 200px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.qrcode-desc {
  margin-top: 16px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.share-link-display {
  padding: 24px;
}

.share-link-preview {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.share-link-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.share-link-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.share-link-url {
  margin-top: 16px;
}

.invite-records-section {
  padding: 32px;
}

.records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.records-header .section-title {
  margin-bottom: 0;
}

.invite-records-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.invite-record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-background);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}

.record-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, #5856d6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  overflow: hidden;
}

.user-avatar .avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-info .username {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.register-time {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.record-reward {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reward-amount {
  font-size: 18px;
  font-weight: 700;
}

.reward-amount.unclaimed {
  color: var(--color-primary);
}

.reward-amount.claimed {
  color: var(--color-text-secondary);
  text-decoration: line-through;
}

.claimed-text {
  font-size: 14px;
  color: var(--color-success);
  font-weight: 500;
}

@media (max-width: 768px) {
  .points-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .points-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    width: 100%;
  }
  
  .checkin-status {
    align-items: flex-start;
    width: 100%;
  }
  
  .checkin-btn {
    width: 100%;
  }
  
  .rules-grid {
    grid-template-columns: 1fr;
  }
  
  .exchange-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .exchange-action {
    width: 100%;
    justify-content: space-between;
  }
  
  .invite-stats {
    grid-template-columns: 1fr;
  }
  
  .invite-code-display {
    flex-direction: column;
    gap: 20px;
  }
  
  .invite-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .invite-actions .el-button {
    flex: 1;
    min-width: 120px;
  }
  
  .invite-record-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .record-reward {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
