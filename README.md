# WebCammerPlus Chrome Extension (Vue.js)

This project is a Chrome Extension rewritten using Vue.js.

## Project Structure

```
WebCammerPlus/
├── vue-extension/          # Vue.js project for the Chrome Extension
│   ├── public/             # Contains manifest.json and other static assets
│   ├── src/                # Vue.js source code
│   ├── .eslintrc.json      # ESLint configuration for JavaScript/Vue
│   ├── .htmlhintrc         # HTMLHint configuration
│   ├── .stylelintrc.json   # Stylelint configuration for CSS
│   ├── package.json        # Node.js dependencies and scripts
│   ├── package-lock.json   # Dependency lock file
│   └── ...                 # Other Vue CLI generated files
├── .github/                # GitHub Actions workflows
├── .gitignore              # Git ignore file
├── README.md               # This file
└── ...                     # Other project files
```

## Setup and Development

### Prerequisites

-   **Node.js**: Version 14 or higher
-   **npm**: Comes with Node.js
-   **Vue CLI**: If you plan to develop directly within `vue-extension` (installed globally: `npm install -g @vue/cli`)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/jovanrlee/webcammerplus.git
    cd webcammerplus
    ```
2.  **Navigate into the Vue.js project**:
    ```bash
    cd vue-extension
    ```
3.  **Install dependencies**:
    ```bash
    npm install
    ```

### Running the Development Server

While in the `vue-extension` directory:
```bash
npm run serve
```
This will start a development server. The extension will not be directly usable in Chrome this way, but it's useful for developing Vue components.

### Building for Production

While in the `vue-extension` directory:
```bash
npm run build
```
This will compile the Vue.js application into the `vue-extension/dist` directory.

### Loading the Extension in Chrome

1.  Open Chrome and navigate to `chrome://extensions/`.
2.  Enable "Developer mode" (top right corner).
3.  Click "Load unpacked" and select the `vue-extension/dist` directory.

### Linting

While in the `vue-extension` directory:
```bash
npm run lint
```
This will run ESLint for JavaScript/Vue, HTMLHint for HTML, and Stylelint for CSS.

### Auto-fix Linting Issues

Some linting issues can be automatically fixed:
```bash
npm run lint -- --fix
```

## Contributing

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'feat: Add some amazing feature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

**Happy coding! 🎉**

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

## ❓ Need Help?

Contact your development lead or open issues in your version control repository if something is broken or needs improvement. 