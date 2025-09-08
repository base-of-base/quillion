import asyncio
from quillion.components import container, text, button, image, State
from quillion import app, page, Path, css

css(["index.css"])

class AppState(State):
    count: int = 0

@page("/")
async def home():
    return container(
        container(
            container(
                text("COUNTER SYSTEM", class_name="counter-title"),
                text(f"{AppState.count:04d}", class_name="counter-display"),
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
                    class_name="counter-buttons"
                ),
                button(
                    "Go to About",
                    on_click=lambda: Path.navigate("/about"),
                    class_name="nav-btn"
                ),
                class_name="counter-container"
            ),
            class_name="counter-card"
        ),
        class_name="page-container"
    )

@page("/about")
def about():
    return container(
        container(
            container(
                text("ABOUT", class_name="about-title"),
                text("Enterprise Solutions Platform", class_name="about-subtitle"),
                container(
                    image("./s.svg", class_name="about-image"),
                    container(
                        container(
                            text("CORE FEATURES", class_name="features-title"),
                            container(
                                container(
                                    text("Advanced Architecture", class_name="feature-title"),
                                    text("Scalable microservices infrastructure", class_name="feature-desc"),
                                    class_name="feature-card"
                                ),
                                container(
                                    text("Security First", class_name="feature-title"),
                                    text("End-to-end encryption protocols", class_name="feature-desc"),
                                    class_name="feature-card"
                                ),
                                class_name="features-grid"
                            ),
                            button(
                                "Go to Home",
                                on_click=lambda: Path.navigate("/"),
                                class_name="nav-btn"
                            ),
                            class_name="features-content"
                        ),
                        class_name="features-container"
                    ),
                    class_name="about-content"
                ),
                class_name="about-inner"
            ),
            class_name="about-card"
        ),
        class_name="page-container"
    )

@page("/user-id/{id}")
def user_page(id: str):
    return container(
        container(
            text(f"User Profile: {id}", class_name="user-title"),
            button(
                "Go to Home",
                on_click=lambda: Path.navigate("/"),
                class_name="nav-btn"
            ),
            class_name="user-card"
        ),
        class_name="page-container"
    )

@page("*")
def not_found():
    return container(
        container(
            container(
                text("404", class_name="notfound-code"),
                text("PAGE NOT FOUND", class_name="notfound-title"),
                text("The page you are looking for doesn't exist or has been moved", class_name="notfound-desc"),
                button(
                    "Go to Home",
                    on_click=lambda: Path.navigate("/"),
                    class_name="nav-btn"
                ),
                class_name="notfound-content"
            ),
            class_name="notfound-card"
        ),
        class_name="page-container"
    )

app.start(port=1337)