(() => {
  // Shift the main page content to the left
  document.body.style.marginRight = "400px";

  // Prevent double injection
  if (document.getElementById('custom-sidebar')) return;

  // Create iframe for the sidebar
  const iframe = document.createElement('iframe');
  iframe.src = chrome.runtime.getURL('sidebar.html');
  iframe.id = 'custom-sidebar';
  iframe.style.cssText = `
    position: fixed;
    top: 0;
    right: 0;
    width: 400px;
    height: 100vh;
    border: none;
    z-index: 999999;
    background: white;
    box-shadow: -3px 0 10px rgba(0,0,0,0.3);
  `;

  document.body.appendChild(iframe);
})();