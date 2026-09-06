from quillion import app, button, div, heading, page

counter = 0
items = []

@page("/")
def home():
    return div(
        div(
            heading("Counter: ", counter, level=3),
            div(
                button("+1", on_click=lambda: counter + 1),
                button("-1", on_click=lambda: counter - 1),
                button("×2", on_click=lambda: counter * 2),
                button("Reset", on_click=lambda: counter.set(0)),
            ),
            heading("Items: ", items, level=4),
            button("Add", on_click=lambda: items.append(f"Item {len(items) + 1}")),
            div(items.map(lambda x: div(x))),
        ),
    )

app.run()