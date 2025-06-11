<template>
    <div class="translate-page">
      <h1 class="page-title">Translate</h1>
  
      <!-- Top controls -->
      <div class="controls">
        <select v-model="model" class="control-select">
          <option value="gpt">🤖 GPT-4</option>
          <option value="mini">🧠 GPT-4.1 mini</option>
        </select>
  
        <select v-model="prefs" class="control-select">
          <option value="default">Default preferences</option>
          <option value="formal">Formal tone</option>
          <option value="casual">Casual tone</option>
        </select>
      </div>
  
      <!-- Input / Output panels -->
      <div class="panels">
        <!-- Source text panel -->
        <div class="panel left">
          <div class="panel-header">
            <select v-model="sourceLang">
              <option value="auto">Auto Detect</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <!-- … -->
            </select>
          </div>
  
          <textarea
            v-model="text"
            placeholder="Type or paste text here…"
            class="panel-textarea"
          ></textarea>
  
          <button class="mic-btn">
            🎤
          </button>
        </div>
  
        <!-- Swap / arrow -->
        <div class="swap">
          ⇄
        </div>
  
        <!-- Target text panel -->
        <div class="panel right">
          <div class="panel-header">
            <select v-model="targetLang">
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <!-- … -->
            </select>
          </div>
  
          <textarea
            v-model="result"
            readonly
            placeholder="Translation appears here…"
            class="panel-textarea"
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
    </div>
  </template>
  
  <script>
  export default {
    name: 'AppTranslate',
    data() {
      return {
        model: 'gpt',
        prefs: 'default',
        sourceLang: 'auto',
        targetLang: 'en',
        text: '',
        result: ''
      }
    },
    methods: {
      doTranslate() {
        // call your API / service here
        // for demo:
        this.result = `Translated [${this.text}] → (${this.targetLang})`
      }
    }
  }
  </script>
  
  <style scoped>
  .translate-page {
    max-width: 600px;
    margin: 2rem auto;
    font-family: Avenir, sans-serif;
  }
  
  .page-title {
    font-size: 2rem;
    margin-bottom: 1rem;
  }
  
  .controls {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  
  .control-select {
    flex: 1;
    padding: 0.5rem 0.75rem;
    border-radius: 0.5rem;
    border: 1px solid #ddd;
    background: #f8f8f8;
  }
  
  .panels {
    display: flex;
    background: #f8f8f8;
    border-radius: 0.75rem;
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  }
  
  .panel {
    position: relative;
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .panel-header {
    padding: 0.5rem;
    background: #fff;
    border-bottom: 1px solid #eee;
  }
  
  .panel-header select {
    border: none;
    background: transparent;
    font-weight: bold;
  }
  
  .panel-textarea {
    flex: 1;
    padding: 0.75rem;
    border: none;
    resize: none;
    background: transparent;
    font-size: 1rem;
    outline: none;
  }
  
  .left .mic-btn {
    position: absolute;
    bottom: 0.5rem;
    left: 0.5rem;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.25rem;
  }
  
  .swap {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 3rem;
    background: #f0f0f0;
    font-size: 1.25rem;
    color: #666;
  }
  
  .translate-btn {
    width: 100%;
    padding: 0.75rem;
    font-size: 1rem;
    border: none;
    border-radius: 0.5rem;
    background: #2c3e50;
    color: white;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .translate-btn:disabled {
    background: #aaa;
    cursor: not-allowed;
  }
  </style>
  