// Example JavaScript file to demonstrate ESLint linting

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