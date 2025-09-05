# Quillion

**Quillion** is a Python web framework for building fast, reactive, and elegant web applications with minimal effort

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