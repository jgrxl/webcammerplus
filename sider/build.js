const fs = require('fs');
const path = require('path');

// Simple build script to copy Vue from node_modules
function copyVue() {
  const vueSource = path.join(__dirname, 'node_modules', 'vue', 'dist', 'vue.global.js');
  const vueTarget = path.join(__dirname, 'vue.js');
  
  if (fs.existsSync(vueSource)) {
    fs.copyFileSync(vueSource, vueTarget);
    console.log('✅ Vue copied to local directory');
  } else {
    console.log('❌ Vue not found. Run: npm install');
  }
}

copyVue();