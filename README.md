# WebCammerPlus Linter Suite

A comprehensive linter setup for JavaScript, HTML, and CSS projects using industry-standard tools.

## 🛠️ Tools Used

- **JavaScript**: [ESLint](https://eslint.org/) - Enforces coding standards and best practices
- **HTML**: [HTMLHint](https://htmlhint.com/) - Validates HTML syntax and accessibility
- **CSS**: [Stylelint](https://stylelint.io/) - Enforces CSS coding standards

## 📋 Prerequisites

- **Node.js**: Version 14 or higher
- **npm**: Comes with Node.js

## 🚀 Quick Setup

1. **Clone or download this project**
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Make the lint script executable**:
   ```bash
   chmod +x lint.sh
   ```

## 📁 Project Structure

```
WebCammerPlus/
├── .eslintrc.json        # ESLint configuration for JavaScript
├── .htmlhintrc          # HTMLHint configuration for HTML
├── .stylelintrc.json    # Stylelint configuration for CSS
├── package.json         # Node.js dependencies and scripts
├── lint.sh             # Main linting script
├── README.md           # This file
└── src/                # Your source code directory
    ├── *.js            # JavaScript files
    ├── *.html          # HTML files
    └── *.css           # CSS files
```

## 🎯 Usage

### Run All Linters
```bash
./lint.sh
```

### Run Individual Linters

#### JavaScript (ESLint)
```bash
npm run lint:js
```

#### HTML (HTMLHint)
```bash
npm run lint:html
```

#### CSS (Stylelint)
```bash
npm run lint:css
```

### Auto-fix Issues

#### JavaScript (ESLint)
```bash
npm run lint:fix:js
```

#### CSS (Stylelint)
```bash
npm run lint:fix:css
```

#### HTML (HTMLHint)
```bash
npm run lint:fix:html
```

## ⚙️ Configuration

### JavaScript (ESLint)
The `.eslintrc.json` file is configured with:
- Standard JavaScript Style Guide
- Modern ES6+ features support
- Best practices enforcement
- Code formatting rules
- Common error prevention

### HTML (HTMLHint)
The `.htmlhintrc` file includes:
- HTML5 validation
- Accessibility checks
- Semantic HTML requirements
- Attribute ordering
- Code formatting

### CSS (Stylelint)
The `.stylelintrc.json` file enforces:
- Standard CSS formatting
- Best practices
- Consistent naming conventions
- Accessibility considerations
- Modern CSS standards

## 🔧 Customization

### Modify JavaScript Rules
Edit `.eslintrc.json` to adjust JavaScript linting rules. Refer to the [ESLint documentation](https://eslint.org/docs/rules/) for available rules.

### Modify HTML Rules
Edit `.htmlhintrc` to customize HTML validation. See [HTMLHint rules](https://htmlhint.com/docs/user-guide/rules) for options.

### Modify CSS Rules
Edit `.stylelintrc.json` to adjust CSS linting. Check [Stylelint rules](https://stylelint.io/user-guide/rules) for available options.

## 📝 Example Usage

### Sample JavaScript File
```javascript
// src/example.js
const exampleFunction = (param) => {
  const result = param * 2;
  return result;
};

class ExampleClass {
  constructor(name) {
    this.name = name;
    this.count = 0;
  }

  increment() {
    this.count += 1;
    return this.count;
  }

  getName() {
    return this.name;
  }
}

// Array methods
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(num => num * 2);
const sum = numbers.reduce((acc, num) => acc + num, 0);

// Object destructuring
const user = {
  firstName: 'John',
  lastName: 'Doe',
  age: 30
};

const { firstName, lastName } = user;

// Template literals
const greeting = `Hello, ${firstName} ${lastName}!`;

// Export for module usage
export { exampleFunction, ExampleClass, greeting };
```

### Sample HTML File
```html
<!-- src/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Example Page</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <main>
        <h1>Hello World</h1>
        <p>This is a sample HTML file.</p>
    </main>
</body>
</html>
```

### Sample CSS File
```css
/* src/styles.css */
.example {
    color: #333;
    font-size: 16px;
    margin: 0;
    padding: 1rem;
}

.example:hover {
    color: #666;
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Node.js not found**: Install Node.js from [nodejs.org](https://nodejs.org/)
2. **Permission denied**: Make sure `lint.sh` is executable: `chmod +x lint.sh`
3. **ESLint not found**: Run `npm install` to install dependencies

### Getting Help

- [ESLint Documentation](https://eslint.org/)
- [HTMLHint Documentation](https://htmlhint.com/)
- [Stylelint Documentation](https://stylelint.io/)

## 📄 License

MIT License - feel free to use and modify as needed.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the linters
5. Submit a pull request

---

**Happy coding! 🎉**
