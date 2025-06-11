(() => {
  const existing = document.getElementById('custom-sidebar');
  const mainElement = document.querySelector('#main.chat_broadcast');
  const baseElement = document.getElementById('base');

  if (existing) {
    existing.style.right = "-400px";
    if (mainElement) mainElement.style.width = "";
    if (baseElement) baseElement.style.width = "";
    setTimeout(() => {
      existing.remove();
      document.body.style.marginRight = "0px";
    }, 300);
  } else {
    if (mainElement) mainElement.style.width = "80%";
    if (baseElement) baseElement.style.width = "1000px";
    document.body.style.marginRight = "400px";

    const iframe = document.createElement('iframe');
    iframe.src = chrome.runtime.getURL('sidebar.html');
    iframe.id = 'custom-sidebar';
    iframe.style.cssText = `
      position: fixed;
      top: 0;
      right: -400px;
      width: 400px;
      height: 100vh;
      border: none;
      z-index: 999999;
      background: white;
      box-shadow: -3px 0 10px rgba(0,0,0,0.3);
      transition: right 0.3s ease;
    `;

    document.body.appendChild(iframe);
    requestAnimationFrame(() => {
      iframe.style.right = "0px";
    });
  }
})();