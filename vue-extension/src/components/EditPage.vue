<template>
  <div class="edit-page">
    <header class="edit-header">
      <button class="tab" :class="{ active: mode === 'write' }" @click="mode = 'write'">
        Write
      </button>
      <button class="tab" :class="{ active: mode === 'reply' }" @click="mode = 'reply'">
        Reply
      </button>
      <span class="clock-icon">🕒</span>
    </header>

    <div class="type-selector">
      <button
        v-for="opt in currentTypes"
        :key="opt"
        :class="{ active: selectedType === opt }"
        @click="selectedType = opt"
      >
        {{ opt }}
      </button>
      <button class="more">☰</button>
    </div>

    <div class="pill">
      <span>{{ style }} – {{ length }} – {{ language }}</span>
      <span class="dropdown-arrow">▾</span>
    </div>

    <div v-if="mode === 'write'">
      <textarea
        v-model="contentWrite"
        placeholder="Enter the topic you want to write about"
      ></textarea>
    </div>
    <div v-else>
      <textarea
        class="reply-original"
        v-model="contentOriginal"
        placeholder="Enter the original text you want to reply to"
      ></textarea>
      <textarea
        class="second"
        v-model="contentIdea"
        placeholder="Describe the general idea of your response"
      ></textarea>
    </div>

    <button
      class="submit-btn"
      :disabled="!canSubmit"
      @click="onSubmit"
    >
      Submit
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Mode: write vs reply
const mode = ref('write')

// Type options
const writeTypes = ['Essay', 'Paragraph', 'Email', 'Idea']
const replyTypes = ['Comment', 'Email', 'Message', 'Twitter']
const currentTypes = computed(() => (mode.value === 'write' ? writeTypes : replyTypes))
const selectedType = ref(currentTypes.value[0])

// Style / length / language
const style = ref('Formal')
const length = ref('Short')
const language = ref('English')

// Content models
const contentWrite = ref('')
const contentOriginal = ref('')
const contentIdea = ref('')

// Enable submit only when inputs are filled
const canSubmit = computed(() => {
  return mode.value === 'write'
    ? contentWrite.value.trim().length > 0
    : contentOriginal.value.trim().length > 0 && contentIdea.value.trim().length > 0
})

function onSubmit() {
  const payload = mode.value === 'write'
    ? {
        mode: 'write',
        type: selectedType.value,
        style: style.value,
        length: length.value,
        language: language.value,
        content: contentWrite.value.trim(),
      }
    : {
        mode: 'reply',
        type: selectedType.value,
        style: style.value,
        length: length.value,
        language: language.value,
        original: contentOriginal.value.trim(),
        idea: contentIdea.value.trim(),
      }
  console.log('submit', payload)
}
</script>

<style scoped>
.edit-page {
  max-width: 600px;
  margin: 2rem auto;
  font-family: sans-serif;
}

.edit-header {
  display: flex;
  align-items: center;
}

.tab {
  background: none;
  border: none;
  font-size: 1.25rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  color: #666;
}

.tab.active {
  color: #000;
  border-bottom: 2px solid #000;
}

.clock-icon {
  margin-left: auto;
  font-size: 1.2rem;
}

.type-selector {
  display: flex;
  margin: 1rem 0;
}

.type-selector button {
  background: #f0f0f0;
  border: none;
  padding: 0.5rem 1rem;
  margin-right: 0.5rem;
  cursor: pointer;
}

.type-selector button.active {
  background: #ddd;
}

.type-selector .more {
  flex: 1;
  text-align: right;
}

.pill {
  display: inline-flex;
  align-items: center;
  background: #f5f5f5;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.pill .dropdown-arrow {
  margin-left: 0.5rem;
}

textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
  font-size: 1rem;
  margin-bottom: 1rem;
  min-height: 120px;
}

.reply-original {
  border: 2px solid #7f5aff;
}

textarea.second {
  margin-top: 0;
}

.submit-btn {
  float: right;
  background: #007aff;
  color: #fff;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
