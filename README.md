# Quillion

**Quillion** is a Python web framework for building fast, reactive, and elegant web applications with minimal effort. It focuses on a component-based, declarative approach, allowing you to create complex UIs and manage application state using pure Python.

-----

### **Getting Started**

1.  **Installation:**
    `pip install quillion`

2.  **A Simple "Hello, World!" App:**
    ```python
    from quillion import app, page
    from quillion.components import text
    
    @page("/")
    def home():
        return text("Hello, World!")
    
    app.start(port=1337)
    ```

3.  **Run the app:**
    `python main.py`

-----

### **License**

MIT
