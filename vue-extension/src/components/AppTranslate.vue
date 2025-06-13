<template>
  <div class="translate-page">

    <!-- 1) Header with preview button -->
    <header class="translate-header">
      <h1>Translate</h1>
      <button class="settings-btn" @click="showSettings = true">
        {{ previewText }}
      </button>
    </header>

    <!-- 2) Language selectors -->
    <div class="lang-controls">
      <select v-model="sourceLang">
        <option
          v-for="lang in languages"
          :key="lang.code"
          :value="lang.code"
        >
          {{ lang.name }}
        </option>
      </select>

      <button class="swap-btn" @click="swapLanguages">⇄</button>

      <select v-model="targetLang">
        <option
          v-for="lang in languages"
          :key="lang.code"
          :value="lang.code"
        >
          {{ lang.name }}
        </option>
      </select>
    </div>

    <!-- 3) Input textarea -->
    <div class="input-container">
      <textarea
        v-model="text"
        placeholder="Type or paste text…"
        class="input-textarea"
      ></textarea>
      <button class="mic-btn">🎤</button>
    </div>

    <!-- 4) Translate trigger -->
    <button
      class="translate-btn"
      :disabled="!text.trim()"
      @click="doTranslate"
    >
      Translate
    </button>

    <!-- 5) Result + action buttons -->
    <div class="result-container" v-if="result">
      <textarea
        readonly
        class="result-textarea"
        :value="result"
        placeholder="Translation appears here…"
      ></textarea>

      <div class="action-buttons">
        <button @click="copyResult">Copy</button>
        <button @click="rewriteResult">Rewrite</button>
        <button @click="regenerate">Regenerate</button>
        <button @click="readAloud">Read loud</button>
      </div>
    </div>

    <!-- 6) Settings popup (unchanged) -->
    <SettingsModal
      v-if="showSettings"
      :model="model"
      :tone="tone"
      :styleLevel="styleLevel"
      :sourceLang="sourceLang"
      :targetLang="targetLang"
      :modelOptions="modelOptions"
      :toneOptions="toneOptions"
      :styleOptions="styleOptions"
      :languages="languages"
      @update:model="model = $event"
      @update:tone="tone = $event"
      @update:styleLevel="styleLevel = $event"
      @update:sourceLang="sourceLang = $event"
      @update:targetLang="targetLang = $event"
      @close="showSettings = false"
    />
  </div>
</template>

<script>
import SettingsModal from './SettingsModal.vue'

export default {
  name: 'AppTranslate',
  components: { SettingsModal },
  data() {
    return {
      showSettings: false,
      text:          '',
      result:        '',

      // your three preferences
      model:       'standard',
      tone:        'neutral',
      styleLevel:  'creative',

      // languages
      sourceLang:  'auto',
      targetLang:  'en',

      // options arrays…
      modelOptions: [
        { value: 'standard', label: 'Standard' },
        { value: 'creative',  label: 'Creative' },
        { value: 'precise',   label: 'Precise' },
      ],
      toneOptions: [
        { value: 'neutral', label: 'Neutral' },
        { value: 'formal',  label: 'Formal' },
        { value: 'casual',  label: 'Casual' },
      ],
      styleOptions: [
        { value: 'standard', label: 'Standard' },
        { value: 'creative',  label: 'Creative' },
        { value: 'precise',   label: 'Precise' },
      ],
      languages: [
        { code: 'auto', name: 'Auto Detect' },
        { code: 'en',   name: 'English'     },
        { code: 'es',   name: 'Spanish'     },
        { code: 'fr',   name: 'French'      },
        { code: 'de',   name: 'German'      },
        { code: 'zh',   name: 'Chinese'     },
        // …add more…
      ],
    }
  },
  computed: {
    previewText() {
      const m = this.modelOptions.find(o => o.value === this.model)?.label
      const t = this.toneOptions .find(o => o.value === this.tone )?.label
      const s = this.styleOptions.find(o => o.value === this.styleLevel)?.label
      return [m, t, s].filter(Boolean).join(' – ')
    },
  },
  methods: {
    doTranslate() {
      // → hook up your real API here
      this.result = `Translated [${this.text}] → ${this.targetLang}`
    },
    swapLanguages() {
      [this.sourceLang, this.targetLang] =
        [this.targetLang, this.sourceLang]
    },
    copyResult() {
      navigator.clipboard.writeText(this.result)
        .then(() => console.log('Copied!'))
        .catch(() => console.warn('Copy failed'))
    },
    rewriteResult() {
      // → call your “rewrite” endpoint
      console.log('Rewrite:', this.result)
    },
    regenerate() {
      // just re-run translate for now
      this.doTranslate()
    },
    readAloud() {
      if (!this.result) return
      const u = new SpeechSynthesisUtterance(this.result)
      speechSynthesis.speak(u)
    }
  }
}
</script>

<style scoped>
.translate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.settings-btn {
  background: none;
  border: none;
  font-size: 1rem;
  padding: 0.5rem 1rem;
  white-space: nowrap;
  cursor: pointer;
}

.lang-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.lang-controls select {
  padding: 0.4rem 0.6rem;
  border: 1px solid #bbb;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
}
.swap-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
}

.input-container {
  position: relative;
  margin-bottom: 0.75rem;
}
.input-textarea {
  width: 100%;
  height: 150px;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
  font-size: 1rem;
}
.mic-btn {
  position: absolute;
  bottom: 0.5rem;
  left: 0.5rem;
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
}

.translate-btn {
  width: 100%;
  padding: 0.75rem;
  background: #2c3e50;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.translate-btn:disabled {
  background: #aaa;
  cursor: not-allowed;
}

.result-container {
  margin-top: 1rem;
}
.result-textarea {
  width: 100%;
  min-height: 120px;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}
.action-buttons button {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #bbb;
  border-radius: 4px;
  background: #f8f8f8;
  cursor: pointer;
  transition: background 0.2s;
}
.action-buttons button:hover {
  background: #e0e0e0;
}
</style>
