<template>
  <div class="translate-page">

    <!-- Page header with preview button -->
    <header class="translate-header">
      <h1>Translate</h1>
      <button class="settings-btn" @click="showSettings = true">
        {{ previewText }}
      </button>
    </header>

    <!-- ←→ Language selectors just above the panels -->
    <div class="lang-controls">
      <select v-model="sourceLang">
        <option
          v-for="lang in languages"
          :key="lang.code"
          :value="lang.code"
        >{{ lang.name }}</option>
      </select>

      <button class="swap-btn" @click="swapLanguages">⇄</button>

      <select v-model="targetLang">
        <option
          v-for="lang in languages"
          :key="lang.code"
          :value="lang.code"
        >{{ lang.name }}</option>
      </select>
    </div>

    <!-- The two text panels -->
    <div class="panels">
      <div class="panel left">
        <textarea
          v-model="text"
          placeholder="Type or paste text…"
        ></textarea>
        <button class="mic-btn">🎤</button>
      </div>

      <!-- You can remove this swap if you prefer just the ↑↑ controls above -->
      <div class="swap" @click="swapLanguages">⇄</div>

      <div class="panel right">
        <textarea
          v-model="result"
          readonly
          placeholder="Translation appears here…"
        ></textarea>
      </div>
    </div>

    <!-- Translate button -->
    <button
      class="translate-btn"
      :disabled="!text.trim()"
      @click="doTranslate"
    >
      Translate
    </button>

    <!-- Settings Modal (unchanged) -->
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
      model:        'standard',
      tone:         'neutral',
      styleLevel:   'creative',

      // language codes
      sourceLang:   'auto',
      targetLang:   'en',

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
        // …etc…
      ],
    }
  },
  computed: {
    // preview for top‐right button
    previewText() {
      const m = this.modelOptions.find(o => o.value === this.model)?.label
      const t = this.toneOptions .find(o => o.value === this.tone )?.label
      const s = this.styleOptions.find(o => o.value === this.styleLevel)?.label
      return [m, t, s].filter(Boolean).join(' – ')
    },
  },
  methods: {
    doTranslate() {
      // call your API…
      this.result = `Translated [${this.text}] → ${this.targetLang}`
    },
    swapLanguages() {
      [this.sourceLang, this.targetLang] =
        [this.targetLang, this.sourceLang]
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

/* new language controls above panels */
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

.panels {
  display: flex;
  margin-bottom: 1rem;
}
.panel {
  flex: 1;
  position: relative;
}
.panel textarea {
  width: 100%;
  height: 200px;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
  font-size: 1rem;
}
.left .mic-btn {
  position: absolute;
  bottom: 0.5rem;
  left: 0.5rem;
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
}
.swap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  cursor: pointer;
  user-select: none;
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
</style>
