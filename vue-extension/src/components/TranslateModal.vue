<template>
    <div class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal">
        <header class="modal-header">
          <h3>Translation Settings</h3>
          <button class="close-btn" @click="$emit('close')">×</button>
        </header>
  
        <section class="modal-body">
          <!-- Model / creativity -->
          <div class="form-group">
            <label>Model</label>
            <div class="prefs-btn-group">
              <button
                v-for="opt in modelOptions"
                :key="opt.value"
                @click="$emit('update:model', opt.value)"
                :class="['pref-btn', { active: model === opt.value }]"
              >{{ opt.label }}</button>
            </div>
          </div>
  
          <!-- Tone / style -->
          <div class="form-group">
            <label>Tone</label>
            <div class="prefs-btn-group">
              <button
                v-for="opt in toneOptions"
                :key="opt.value"
                @click="$emit('update:tone', opt.value)"
                :class="['pref-btn', { active: tone === opt.value }]"
              >{{ opt.label }}</button>
            </div>
          </div>
          
          <!-- Languages -->
          <div class="form-group">
            <label>Detect From</label>
            <select @change="$emit('update:sourceLang', $event.target.value)" :value="sourceLang">
              <option v-for="lang in languages" :key="lang.code" :value="lang.code">
                {{ lang.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Translate To</label>
            <select @change="$emit('update:targetLang', $event.target.value)" :value="targetLang">
              <option v-for="lang in languages" :key="lang.code" :value="lang.code">
                {{ lang.name }}
              </option>
            </select>
          </div>
        </section>
  
        <footer class="modal-footer">
          <button class="btn-close" @click="$emit('close')">Close</button>
        </footer>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'TranslateModal',
    props: {
      model:       { type: String, required: true },
      tone:        { type: String, required: true },
      sourceLang:  { type: String, required: true },
      targetLang:  { type: String, required: true },
      modelOptions: { type: Array, required: true },
      toneOptions:  { type: Array, required: true },
      languages:    { type: Array, required: true },
    }
  }
  </script>
  
  <style scoped>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .modal {
    background: #fff;
    width: 90%;
    max-width: 400px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  }
  .modal-header,
  .modal-footer {
    padding: 0.75rem 1rem;
    background: #f7f7f7;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .modal-body {
    padding: 1rem;
  }
  .close-btn, .btn-close {
    background: none;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
  }
  .form-group {
    margin-bottom: 1rem;
  }
  .prefs-btn-group {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  .pref-btn {
    padding: 0.4rem 0.8rem;
    border: 1px solid #bbb;
    border-radius: 4px;
    background: #f0f0f0;
    cursor: pointer;
  }
  .pref-btn.active {
    background: #2c3e50;
    color: #fff;
    border-color: #2c3e50;
  }
  select {
    width: 100%;
    padding: 0.4rem;
    border-radius: 4px;
    border: 1px solid #ccc;
  }
  </style>
  