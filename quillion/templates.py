"""Templates for Quillion project files."""

INDEX_HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>{app_name}</title>
    <meta name="tcp-gateway" content="ws://localhost:8765">
</head>
<body>
    <div id="app"></div>
    <script>
const appContainer = document.getElementById("app");
const componentCache = new Map();

const gatewayAddress = (() => {{
    const meta = document.querySelector('meta[name="tcp-gateway"]');
    return meta ? meta.content : 'ws://localhost:8765';
}})();

let ws = null;
let currentFullPath = window.location.pathname + window.location.search + window.location.hash;

function injectGlobalCss(cssArray) {{
    if (!cssArray || !cssArray.length) return;
    const existing = document.querySelectorAll('style[data-quillion-css]');
    existing.forEach(style => style.remove());
    for (const cssContent of cssArray) {{
        const styleTag = document.createElement('style');
        styleTag.setAttribute('data-quillion-css', 'true');
        styleTag.textContent = cssContent;
        document.head.appendChild(styleTag);
    }}
}}

function connect() {{
    ws = new WebSocket(gatewayAddress);
    
    ws.onopen = () => {{
        ws.send(JSON.stringify({{
            type: "navigate",
            path: currentFullPath
        }}));
    }};
    
    ws.onmessage = (event) => {{
        const data = JSON.parse(event.data);
        requestAnimationFrame(() => {{
            if (data.global_css) {{
                injectGlobalCss(data.global_css);
            }}
            if (data.tree) {{
                componentCache.clear();
                const rootEl = createElement(data.tree);
                appContainer.replaceChildren(rootEl);
            }} 
            if (data.updates) {{
                for (let i = 0; i < data.updates.length; i++) {{
                    const update = data.updates[i];
                    const el = componentCache.get(update.id);
                    if (el) {{
                        if (update.props) {{
                            setProps(el, update.props);
                        }}
                        if (update.children && update.children.length > 0) {{
                            const fragment = document.createDocumentFragment();
                            for (const childNode of update.children) {{
                                fragment.appendChild(createElement(childNode));
                            }}
                            el.replaceChildren(fragment);
                        }}
                    }}
                }}
            }}
        }});
    }};
    
    ws.onclose = () => {{
        setTimeout(connect, 1000);
    }};
}}

function setProps(el, props) {{
    for (const key in props) {{
        if (el[key] !== props[key]) {{
            el[key] = props[key];
        }}
    }}
}}

function createElement(node) {{
    const el = document.createElement(node.tag);
    
    if (node.props) setProps(el, node.props);

    if (node.events) {{
        for (const eventName in node.events) {{
            const eventId = node.events[eventName];
            el.addEventListener(eventName, (e) => {{
                if (eventName === 'click' && el.tagName === 'A') {{
                    e.preventDefault();
                    const href = el.getAttribute('href');
                    if (href && href !== '#') {{
                        navigateTo(href);
                        return;
                    }}
                }}
                ws.send(JSON.stringify({{
                    type: "event",
                    event_id: eventId,
                    data: {{ value: e.target.value }}
                }}));
            }});
        }}
    }}

    if (node.children && node.children.length > 0) {{
        const fragment = document.createDocumentFragment();
        for (let i = 0; i < node.children.length; i++) {{
            fragment.appendChild(createElement(node.children[i]));
        }}
        el.appendChild(fragment);
    }}

    componentCache.set(node.id, el);
    return el;
}}

function navigateTo(path) {{
    if (path === currentFullPath) return;
    currentFullPath = path;
    window.history.pushState(null, '', path);
    if (ws && ws.readyState === WebSocket.OPEN) {{
        ws.send(JSON.stringify({{
            type: "navigate",
            path: path
        }}));
    }}
}}

window.addEventListener('popstate', () => {{
    currentFullPath = window.location.pathname + window.location.search + window.location.hash;
    if (ws && ws.readyState === WebSocket.OPEN) {{
        ws.send(JSON.stringify({{
            type: "navigate",
            path: currentFullPath
        }}));
    }}
}});

connect();
    </script>
</body>
</html>'''

MAIN_PY_TEMPLATE = '''from quillion import app, page, container, text, button, heading, div, var

counter = var(0)


@page("/")
def home():
    return container(
        heading("{app_name}", level=1),
        div(
            text("Counter: ", counter),
            button("Increment", on_click=lambda: counter + 1),
            button("Decrement", on_click=lambda: counter - 1),
        ),
    )


app.run()
'''