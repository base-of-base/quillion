from quillion import app, page, text, button, heading, input, div, span, var

items = var([])

def add_item():
    items.value.append(f"Item {len(items) + 1}")

@page("/")
def home():
    return div(
        div(
            heading("Reactive List", level=3),
            button("Add Item", on_click=add_item),
            div(items),
        ),
    )

app.run()