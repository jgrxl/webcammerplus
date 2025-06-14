// External JavaScript for Manifest V3 compliance
document.addEventListener('DOMContentLoaded', function() {
  console.log('Test popup JavaScript loaded');
  
  // Capture all errors
  const errors = [];
  window.onerror = function(msg, url, line, col, error) {
    errors.push(`Error: ${msg} at ${url}:${line}:${col}`);
    updateErrorLog();
  };

  function updateErrorLog() {
    const errorDiv = document.getElementById('errorLog');
    const errorsDiv = document.getElementById('errors');
    if (errorDiv && errorsDiv && errors.length > 0) {
      errorDiv.style.display = 'block';
      errorsDiv.innerHTML = errors.map(e => `<div>${e}</div>`).join('');
    }
  }

  function setResult(testId, message, success = null) {
    const element = document.getElementById(`result${testId}`);
    const container = document.getElementById(`test${testId}`);
    if (!element || !container) return;
    
    element.innerHTML = message;
    if (success === true) {
      container.className = 'test success';
    } else if (success === false) {
      container.className = 'test error';
    } else {
      container.className = 'test info';
    }
  }

  // Test 1: Check if vue.js file exists
  fetch('vue.js')
    .then(response => {
      if (response.ok) {
        setResult(1, `✅ vue.js exists (${response.status} ${response.statusText})`, true);
        // Test file size
        return response.text();
      } else {
        setResult(1, `❌ vue.js not found (${response.status} ${response.statusText})`, false);
        return null;
      }
    })
    .then(content => {
      if (content) {
        const size = Math.round(content.length / 1024);
        setResult(1, `✅ vue.js exists (${size}KB)`, true);
      }
    })
    .catch(error => {
      setResult(1, `❌ Failed to check vue.js: ${error.message}`, false);
    });

  // Test 2: Check if Vue is already loaded
  if (typeof Vue !== 'undefined') {
    setResult(2, '✅ Vue already loaded globally', true);
    testVueUsage();
  } else {
    setResult(2, '❌ Vue not loaded yet', false);
    
    // Test 3: Try to load Vue dynamically
    loadVueScript();
  }

  function loadVueScript() {
    const script = document.createElement('script');
    script.src = 'vue.js';
    
    script.onload = function() {
      setResult(3, '✅ vue.js script loaded successfully', true);
      
      // Check if Vue is now available
      setTimeout(() => {
        if (typeof Vue !== 'undefined') {
          testVueUsage();
        } else {
          setResult(4, '❌ Vue script loaded but Vue global not available', false);
        }
      }, 100);
    };
    
    script.onerror = function(e) {
      setResult(3, `❌ Failed to load vue.js script`, false);
      tryAlternativePaths();
    };
    
    document.head.appendChild(script);
  }

  function testVueUsage() {
    try {
      const { createApp } = Vue;
      setResult(4, `✅ Vue working! Version: ${Vue.version || 'unknown'}`, true);
      
      // Try creating a simple app
      const app = createApp({
        data() {
          return { test: 'Vue is working!' };
        }
      });
      
      setResult(4, `✅ Vue fully functional! Can create apps.`, true);
      
    } catch (e) {
      setResult(4, `❌ Vue loaded but createApp failed: ${e.message}`, false);
    }
  }

  function tryAlternativePaths() {
    const alternatives = [
      'node_modules/vue/dist/vue.global.js',
      './vue.js',
      '/vue.js'
    ];
    
    let altResults = [];
    let completed = 0;
    
    alternatives.forEach((path, index) => {
      fetch(path)
        .then(response => {
          altResults.push(`${path}: ${response.status} ${response.statusText}`);
        })
        .catch(error => {
          altResults.push(`${path}: ${error.message}`);
        })
        .finally(() => {
          completed++;
          if (completed === alternatives.length) {
            setResult(5, altResults.join('<br>'), false);
          }
        });
    });
  }

  // Add debug info after a delay
  setTimeout(() => {
    const debugInfo = [
      `Location: ${window.location.href}`,
      `Base URI: ${document.baseURI}`,
      `Document ready state: ${document.readyState}`,
      `Scripts in head: ${document.head.querySelectorAll('script').length}`,
      `Vue available: ${typeof Vue !== 'undefined' ? 'Yes' : 'No'}`
    ];
    
    const debugDiv = document.createElement('div');
    debugDiv.className = 'test info';
    debugDiv.innerHTML = `<strong>Debug Info:</strong><br>${debugInfo.join('<br>')}`;
    document.body.appendChild(debugDiv);
    
    updateErrorLog();
  }, 1500);
});