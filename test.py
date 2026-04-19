from quillion import app, page, container, text, button, heading, div, var

counter = var(0)


@page("/")
def home():
    return container(
        heading("Demo", level=1),
        div(
            text("Counter: ", counter),
            button("Increment", on_click=lambda: counter + 1),
            button("Decrement", on_click=lambda: counter - 1),
        ),
    )


app.run()
