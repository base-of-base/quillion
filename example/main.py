from quillion import app, page, text, button, heading, input, div, var

counter = var(0)

def complex_logic():
    print("Doing magic...")
    counter.value = 42

@page("/")
def home():
    return div(
        heading("Quillion App", level=1),
        div(
            text("Counter: ", counter),
            button("Increment", on_click=counter + 1),
            button("Decrement", on_click=counter - 1),
            button("×2",      on_click=counter * 2),
            button("÷2",      on_click=counter / 2),
            button("Power ²",  on_click=counter ** 2),
            button("Mod 3",    on_click=counter % 3),
            button("Reset",    on_click=counter << 0),
        ),
        div(
            text("Positive: ", counter > 0),
            text(" | Even: ", counter % 2 == 0),
            text(" | > 10: ", counter >= 10),
        ),
        div(
            text("Value as string: ", counter),
            text(" | Formatted: ", f"{counter:03d}"),
        ),
        div(
            button("Append '!'", on_click=counter + "!"),
            button("Append '?'", on_click=counter + "?"),
            button("Magic", on_click=complex_logic),
        )
    )

app.run()