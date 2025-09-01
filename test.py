from quillion import (
    app,
    page,
    box,
    text,
    button,
    image,
    State
)


class AppState(State):
    count: int = 0


@page("/")
def home():
    return box(
        text(f"Счёт: {AppState.count}", size="2rem", color="green"),
        box(
            button("+", on_click=lambda: AppState.set(count=AppState.count + 1)),
            button("-", on_click=lambda: AppState.set(count=AppState.count - 1)),
            direction="row",
            gap="10px",
        ),
        padding="20px",
        background="",
        border_radius="10px",
    )


@page("/about")
def about():
    return box(
        text("О нас", weight="bold", size="3xl"),
        text("Мы крутые", color="gray-600"),
        image("/logo.png", width=100),
        gap="10px",
        padding="30px",
        background="white",
        border_radius="lg",
        shadow="md",
    )


app.start(port=1337)
