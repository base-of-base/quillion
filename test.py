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
        text("О нас", weight="bold", size="4xl", color="indigo-700"),
        text("Ok", size="lg", color="gray-600"),
        image("/logo.png", width=120),
        button("На главную", on_click=lambda: app.redirect("/"),
               background="indigo-600", color="white", padding="15px 30px", border_radius="xl"),
        gap="20px",
        align="center",
        padding="50px",
        background="white",
        border_radius="2xl",
        shadow="2xl",
        height="100vh",
        justify="center"
    )


app.start(port=1337)
