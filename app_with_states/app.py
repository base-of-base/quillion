from quillion.components import container, text, button, State
from quillion import app, page

class AppState(State):
    count: int = 0

@page("/")
def home():
    return container(
        text("Welcome to app_with_states!"),
        text(f"Count: {AppState.count}"),
        button(
            "Increment",
            on_click=lambda: AppState.set(count=AppState.count + 1)
        )
    )

app.start()