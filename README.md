# Right Panel Sidebar Chrome Extension

This extension toggles a sidebar on the right side of any webpage, with icons for different tools like replying, translating, admin chat, and help/FAQ. It also modifies parts of the main page (e.g., #main and #base divs) and supports a colored icon indicator to show connection state (green, red, yellow, blue).

---

## 🛠️ Local Development Setup

### 1. Clone or Download the Extension

Unzip the downloaded folder or clone your project locally.

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
├── vue-extension/           # Vue.js project for the extension UI
│   ├── public/             # Public assets, including manifest.json
│   │   └── manifest.json
│   ├── src/                # Vue.js source code
│   ├── .eslintrc.js        # ESLint configuration for JavaScript/Vue
│   ├── .htmlhintrc         # HTMLHint configuration
│   ├── .stylelintrc.json   # Stylelint configuration
│   └── package.json        # Node.js dependencies and scripts
└── ... other extension files
```

### 2. Install Dependencies (for Vue.js development)

Navigate into the `vue-extension` directory and install the Node.js dependencies:

```bash
cd vue-extension
npm install
```

### 3. Load into Chrome

1. Open Chrome
2. Navigate to `chrome://extensions`
3. Enable **Developer Mode**
4. Click **"Load unpacked"**
5. Select the **`vue-extension/dist`** folder (this folder will be created after you run `npm run build` in the vue-extension directory, which is the next step to run your vue project) of the extension.

### 4. Make Edits and Develop

To develop with Vue.js, navigate to the `vue-extension` directory and run the development server:

```bash
cd vue-extension
npm run serve
```

Any changes you make to the files will require:
- A manual **refresh of the extension** in `chrome://extensions` (after building for production)
- A refresh of the tab where you're testing it

### 5. Linting

Navigate to the `vue-extension` directory and use the following commands:

```bash
# Run all linters
npm run lint

# Lint JavaScript and Vue files
npm run lint:js

# Lint HTML files
npm run lint:html

# Lint CSS files
npm run lint:css

# Fix linting issues (where possible)
npm run lint:fix
```

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

To package the extension for upload, you'll typically build your Vue.js project first:

```bash
cd vue-extension
npm run build
```

Then, zip the `dist` folder created within `vue-extension` (which contains the bundled extension code) and upload to the Chrome Web Store Developer Dashboard.

---

## 📘 Help Tab

The Help tab in the sidebar shows setup instructions for users:

> Settings → Privacy → Copy the Events API JSON Feed URL and paste it into this tool.

This can be updated in `sidebar.html` as needed.

---

## ❓ Need Help?

Contact your development lead or open issues in your version control repository if something is broken or needs improvement.

