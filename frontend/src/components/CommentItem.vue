<template>
  <div class="comment-item" :class="{ 'nested': isNested }">
    <div class="comment-header">
      <div class="comment-avatar">
        <img v-if="comment.author?.avatar" :src="`/uploads/${comment.author?.avatar}`" alt="头像" class="avatar-img" />
        <el-icon v-else><User /></el-icon>
      </div>
      <div class="comment-info">
        <div class="comment-author">
          <span class="author-name">{{ comment.author?.username }}</span>
          <span class="level-badge" :class="comment.author?.level">{{ comment.author?.level_name }}</span>
          <span v-if="comment.reply_to_user" class="reply-to">
            回复 <span class="reply-to-name">{{ comment.reply_to_user.username }}</span>
          </span>
        </div>
        <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
      </div>
      <div class="comment-actions">
        <button 
          v-if="currentUser" 
          class="reply-btn" 
          @click="startReply"
          title="回复"
        >
          <el-icon><ChatDotRound /></el-icon>
          回复
        </button>
        <button 
          v-if="currentUser && comment.user_id === currentUser.id"
          class="delete-comment-btn" 
          @click="$emit('delete', comment)"
          title="删除"
        >
          <el-icon><Delete /></el-icon>
        </button>
      </div>
    </div>
    <div class="comment-content">
      <p>{{ comment.content }}</p>
    </div>
    
    <div v-if="showReplyForm" class="reply-form-container">
      <div class="reply-form">
        <div class="form-header">
          <div class="user-avatar-small">
            <img v-if="currentUser.avatar" :src="`/uploads/${currentUser.avatar}`" alt="头像" class="avatar-img" />
            <el-icon v-else><User /></el-icon>
          </div>
          <span class="user-name">{{ currentUser.username }}</span>
          <span v-if="comment.reply_to_user || (!isNested && replyToAuthor)" class="reply-indicator">
            回复 @{{ replyToUsername }}
          </span>
        </div>
        <textarea 
          v-model="replyContent" 
          :placeholder="`回复 @${replyToUsername}...`" 
          class="comment-textarea"
          rows="2"
          @keydown.ctrl.enter="submitReply"
        ></textarea>
        <div class="form-actions">
          <span class="char-count">{{ replyContent.length }}/500</span>
          <div class="action-buttons">
            <button class="btn-text" @click="cancelReply">取消</button>
            <button class="btn-primary btn-sm" @click="submitReply" :disabled="!replyContent.trim() || submitting">
              <span v-if="!submitting">发送</span>
              <span v-else>发送中...</span>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="comment.replies && comment.replies.length > 0" class="replies-section">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :is-nested="true"
        :current-user="currentUser"
        @delete="onDeleteReply"
        @reply="onReplyToReply"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { User, ChatDotRound, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  isNested: {
    type: Boolean,
    default: false
  },
  currentUser: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['delete', 'reply'])

const showReplyForm = ref(false)
const replyContent = ref('')
const submitting = ref(false)

const replyToUsername = computed(() => {
  if (props.comment.reply_to_user) {
    return props.comment.reply_to_user.username
  }
  return props.comment.author?.username || ''
})

const formatTime = (time) => {
  if (!time) return ''
  return time.replace(' GMT', '')
}

const startReply = () => {
  showReplyForm.value = true
  replyContent.value = ''
}

const cancelReply = () => {
  showReplyForm.value = false
  replyContent.value = ''
}

const submitReply = async () => {
  if (!replyContent.value.trim() || submitting.value) return
  
  emit('reply', {
    parentId: props.isNested ? props.comment.parent_id : props.comment.id,
    replyToUserId: props.comment.user_id,
    replyToUsername: props.comment.author?.username || '',
    content: replyContent.value.trim(),
    targetComment: props.comment,
    isNested: props.isNested
  })
  
  cancelReply()
}

const onDeleteReply = (reply) => {
  emit('delete', reply)
}

const onReplyToReply = (data) => {
  emit('reply', data)
}
</script>

<style scoped>
.comment-item {
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.comment-item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.comment-item.nested {
  margin-left: 52px;
  padding-left: 16px;
  border-left: 2px solid var(--color-border-light);
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.comment-item.nested:last-child {
  margin-bottom: 0;
}

.comment-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, #5856d6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.comment-info {
  flex: 1;
  min-width: 0;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.author-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.reply-to {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.reply-to-name {
  color: var(--color-primary);
  font-weight: 500;
}

.level-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
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
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  color: #1d1d1f;
}

.level-badge.black {
  background: linear-gradient(135deg, #2f2f2f 0%, #1a1a1a 100%);
  color: white;
}

.level-badge.diamond {
  background: linear-gradient(135deg, #b9f2ff 0%, #87ceeb 100%);
  color: #1d1d1f;
}

.comment-time {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.comment-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reply-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  font-size: 13px;
  color: var(--color-primary);
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.reply-btn:hover {
  background: rgba(0, 122, 255, 0.08);
}

.delete-comment-btn {
  padding: 4px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.delete-comment-btn:hover {
  color: var(--color-danger);
  background: rgba(255, 59, 48, 0.1);
}

.comment-content {
  margin-left: 52px;
}

.comment-item.nested .comment-content {
  margin-left: 52px;
}

.comment-content p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text);
  white-space: pre-wrap;
}

.reply-form-container {
  margin-left: 52px;
  margin-top: 12px;
  padding: 16px;
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.reply-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, #5856d6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  overflow: hidden;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
}

.reply-indicator {
  font-size: 13px;
  color: var(--color-primary);
}

.comment-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  outline: none;
  transition: border-color var(--transition-fast);
  background: var(--color-background-secondary);
}

.comment-textarea:focus {
  border-color: var(--color-primary);
}

.comment-textarea::placeholder {
  color: var(--color-text-secondary);
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-count {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-text {
  background: transparent;
  color: var(--color-text-secondary);
  border: none;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  border-radius: var(--radius-sm);
}

.btn-text:hover {
  background: rgba(0, 0, 0, 0.04);
  color: var(--color-text);
}

.btn-primary.btn-sm {
  padding: 8px 20px;
  font-size: 14px;
}

.replies-section {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .comment-item.nested {
    margin-left: 20px;
    padding-left: 12px;
  }
  
  .comment-content,
  .comment-item.nested .comment-content,
  .reply-form-container {
    margin-left: 44px;
  }
}
</style>
