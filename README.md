# Quillion

**Quillion** is a Python web framework for building fast, reactive, and elegant web applications with minimal effort. It focuses on a component-based, declarative approach, allowing you to create complex UIs and manage application state using pure Python.

-----

### **Features**

  * **Pythonic Components:** Define your UI using Python functions that return declarative component objects
  * **Reactive State Management:** Seamlessly update your UI when application state changes
  * **Simple Routing:** Create pages and handle dynamic routes with simple decorators
  * **Built-in Styling:** Style your components directly in Python using a simple and intuitive API
  * **Pure Python:** Write your entire application, from backend logic to frontend UI, in a single language

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
