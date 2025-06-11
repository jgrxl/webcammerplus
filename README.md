# WebCammerPlus Linter Suite

A comprehensive linter setup for Java, HTML, and CSS projects using industry-standard tools.

## 🛠️ Tools Used

- **Java**: [Checkstyle](https://checkstyle.org/) - Enforces coding standards and best practices
- **HTML**: [HTMLHint](https://htmlhint.com/) - Validates HTML syntax and accessibility
- **CSS**: [Stylelint](https://stylelint.io/) - Enforces CSS coding standards

## 📋 Prerequisites

- **Java**: JDK 8 or higher
- **Node.js**: Version 14 or higher (for HTML and CSS linting)
- **npm**: Comes with Node.js

## 🚀 Quick Setup

1. **Clone or download this project**
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Download Checkstyle**:
   ```bash
   npm run install:checkstyle
   ```
4. **Make the lint script executable**:
   ```bash
   chmod +x lint.sh
   ```

## 📁 Project Structure

```
WebCammerPlus/
├── checkstyle.xml          # Checkstyle configuration for Java
├── .htmlhintrc            # HTMLHint configuration for HTML
├── .stylelintrc.json      # Stylelint configuration for CSS
├── package.json           # Node.js dependencies and scripts
├── lint.sh               # Main linting script
├── README.md             # This file
└── src/                  # Your source code directory
    ├── *.java            # Java files
    ├── *.html            # HTML files
    └── *.css             # CSS files
```

## 🎯 Usage

### Run All Linters
```bash
./lint.sh
```

### Run Individual Linters

#### Java (Checkstyle)
```bash
npm run lint:java
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

#### CSS (Stylelint)
```bash
npm run lint:fix:css
```

#### HTML (HTMLHint)
```bash
npm run lint:fix:html
```

## ⚙️ Configuration

### Java (Checkstyle)
The `checkstyle.xml` file is configured with:
- Google Java Style Guide compliance
- Naming conventions
- Import organization
- Code formatting rules
- Best practices enforcement

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

### Modify Java Rules
Edit `checkstyle.xml` to adjust Java linting rules. Refer to the [Checkstyle documentation](https://checkstyle.org/checks.html) for available rules.

### Modify HTML Rules
Edit `.htmlhintrc` to customize HTML validation. See [HTMLHint rules](https://htmlhint.com/docs/user-guide/rules) for options.

### Modify CSS Rules
Edit `.stylelintrc.json` to adjust CSS linting. Check [Stylelint rules](https://stylelint.io/user-guide/rules) for available options.

## 📝 Example Usage

### Sample Java File
```java
// src/Example.java
package com.example;

import java.util.List;
import java.util.ArrayList;

public class Example {
    private static final String CONSTANT = "value";
    
    public void method() {
        List<String> list = new ArrayList<>();
        // Your code here
    }
}
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

1. **Java not found**: Ensure Java is installed and in your PATH
2. **Node.js not found**: Install Node.js from [nodejs.org](https://nodejs.org/)
3. **Permission denied**: Make sure `lint.sh` is executable: `chmod +x lint.sh`
4. **Checkstyle JAR missing**: Run `npm run install:checkstyle`

### Getting Help

- [Checkstyle Documentation](https://checkstyle.org/)
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
