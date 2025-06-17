// Component Loader for WebCammer+
// This helps us load and register Vue components in a modular way

class ComponentLoader {
  constructor() {
    this.components = new Map();
  }

  // Register a component
  register(name, component) {
    this.components.set(name, component);
    console.log(`✅ Registered component: ${name}`);
  }

  // Register multiple components at once
  registerAll(components) {
    Object.entries(components).forEach(([name, component]) => {
      this.register(name, component);
    });
  }

  // Get all registered components
  getAll() {
    const result = {};
    this.components.forEach((component, name) => {
      result[name] = component;
    });
    return result;
  }

  // Create a Vue app with all registered components
  createApp(rootComponent) {
    const app = Vue.createApp(rootComponent);
    
    // Register all components globally
    this.components.forEach((component, name) => {
      app.component(name, component);
    });
    
    return app;
  }
}

// Global instance
window.componentLoader = new ComponentLoader();