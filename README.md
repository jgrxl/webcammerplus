# WebCammerPlus Chrome Extension

This repository contains the WebCammerPlus Chrome Extension.

## 🛠️ Local Development Setup

### 1. Clone or Download the Extension

Clone this project locally or download the zipped folder.

```
webcammerplus/
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
├── .eslintrc.json        # ESLint configuration for JavaScript
├── .htmlhintrc          # HTMLHint configuration for HTML
└── .stylelintrc.json    # Stylelint configuration for CSS
```

### 2. Load into Chrome

1.  Open Chrome
2.  Navigate to `chrome://extensions`
3.  Enable **Developer Mode**
4.  Click **"Load unpacked"**
5.  Select the root folder of the extension (where `manifest.json` is located)

### 3. Make Edits

Any changes you make to the files (e.g., `sidebar.html`, `sidebar.js`, `toggle.js`, etc.) will require:
- A manual **refresh of the extension** in `chrome://extensions`
- A refresh of the tab where you're testing it

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

## 📦 Packaging the Extension

To package the extension for upload:
1.  Zip the entire directory (must include `manifest.json`)
2.  Upload to the Chrome Web Store Developer Dashboard

## 📘 Help Tab

The Help tab in the sidebar shows setup instructions for users:

> Settings → Privacy → Copy the Events API JSON Feed URL and paste it into this tool.

This can be updated in `sidebar.html` as needed.

## ❓ Need Help?

Contact your development lead or open issues in your version control repository if something is broken or needs improvement. 