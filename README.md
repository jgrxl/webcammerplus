<<<<<<< HEAD
# Right Panel Sidebar Chrome Extension

This extension toggles a sidebar on the right side of any webpage, with icons for different tools like replying, translating, admin chat, and help/FAQ. It also modifies parts of the main page (e.g., #main and #base divs) and supports a colored icon indicator to show connection state (green, red, yellow, blue).

---

## 🛠️ Local Development Setup

### 1. Clone or Download the Extension

Unzip the downloaded folder or clone your project locally.

```
right_panel_extension/
├── manifest.json
├── background.js
├── toggle.js
├── sidebar.html
├── sidebar.js
├── sidebar.css
├── icon-green.png
├── icon-yellow.png
├── icon-red.png
├── icon-blue.png
```

---

### 2. Load into Chrome

1. Open Chrome
2. Navigate to `chrome://extensions`
3. Enable **Developer Mode**
4. Click **"Load unpacked"**
5. Select the root folder of the extension (where `manifest.json` is located)

---

### 3. Make Edits

Any changes you make to the files (e.g., `sidebar.html`, `sidebar.js`, `toggle.js`, etc.) will require:
- A manual **refresh of the extension** in `chrome://extensions`
- A refresh of the tab where you're testing it

---

### 4. Test Functionality

- Click the extension icon to toggle the sidebar.
- Use the icon menu (🏠 💬 🌐 🛠️ ❓) to switch between tools.
- Verify that `#main.chat_broadcast` and `#base` resize when the sidebar is active.
- Open the Help tab for setup instructions.

---

## 🎨 Icon Status Indicator

This extension includes 4 dot-style icons:

- `icon-green.png`
- `icon-yellow.png`
- `icon-red.png`
- `icon-blue.png`

You can dynamically change the icon via the background script using:

```js
chrome.action.setIcon({ path: "icon-red.png" });
```

You may integrate this with connection health checks, API ping responses, or status of a third-party app.

---

## 📦 Packaging the Extension

To package the extension for upload:
1. Zip the entire directory (must include `manifest.json`)
2. Upload to the Chrome Web Store Developer Dashboard

---

## 📘 Help Tab

The Help tab in the sidebar shows setup instructions for users:

> Settings → Privacy → Copy the Events API JSON Feed URL and paste it into this tool.

This can be updated in `sidebar.html` as needed.

---

## ❓ Need Help?

Contact your development lead or open issues in your version control repository if something is broken or needs improvement.

=======
# webcammerplus
>>>>>>> 6ee5a9b (Initial commit)
