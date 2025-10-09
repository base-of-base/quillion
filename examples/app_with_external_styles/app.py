from quillion.components import container, text, button, State
from quillion import app, page, css

css(['index.css'])

class AppState(State):
    count: int = 0

@page("/")
def home():
    return container(
        container(
            container(
                text(
                    "Styled counter",
                    class_name="styled-label"
                ),
                text(
                    f"{AppState.count:04d}",
                    class_name="counter-display"
                ),
                container(
                    button(
                        "+",
                        on_click=lambda: AppState.set(count=AppState.count + 1),
                        class_name="counter-btn"
                    ),
                    button(
                        "−",
                        on_click=lambda: AppState.set(count=AppState.count - 1),
                        class_name="counter-btn"
                    ),
                    class_name="buttons-container"
                ),
                class_name="inner-container"
            ),
            class_name="content-card"
        ),
        class_name="page-container",
    )

app.start(port=1337)
