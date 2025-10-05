# Quillion

![Q Logo](assets/q_logo.svg)

**Quillion** is a Python web framework for building fast, reactive, and elegant web applications with minimal effort

-----

### **Getting Started**

1.  **Install via pip:**
    ```bash
    pip install quillion
    ```

2.  **Create main.py**
    ```python
    from quillion import app, page
    from quillion.components import text
    
    @page("/")
    def home():
        return text("Hello, World!")
    
    app.start(port=1337)
    ```

3.  **Run the app:**
    ```bash
    q run
    ```

-----

### **License**

MIT
