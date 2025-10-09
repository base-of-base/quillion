from quillion.components import container, text, button, State
from quillion import app, page


class AppState(State):
    count: int = 0


@page("/")
def home():
    return container(
        container(
            container(
                text(
                    "Styled counter",
                    size="0.85rem",
                    color="#666",
                    weight="600",
                    letter_spacing="2px",
                    text_transform="uppercase",
                    margin_bottom="5px",
                ),
                text(
                    f"{AppState.count:04d}",
                    size="3.5rem",
                    color="#2c3e50",
                    weight="300",
                    font_family="'SF Mono', 'Monaco', monospace",
                    letter_spacing="1px",
                    background="#f8f9fa",
                    padding="25px 40px",
                    border_radius="8px",
                    border="1px solid #e9ecef",
                    box_shadow="inset 0 1px 3px rgba(0,0,0,0.03)",
                ),
                container(
                    button(
                        "+",
                        on_click=lambda: AppState.set(count=AppState.count + 1),
                        background="none",
                        color="#2c3e50",
                        border="1px solid #e9ecef",
                        padding="12px 24px",
                        border_radius="6px",
                        font_weight="400",
                        font_size="1.1rem",
                        cursor="pointer",
                        transition="all 0.2s ease",
                        hover_background="#2c3e50",
                        hover_color="white",
                        hover_border_color="#2c3e50",
                    ),
                    button(
                        "−",
                        on_click=lambda: AppState.set(count=AppState.count - 1),
                        background="none",
                        color="#2c3e50",
                        border="1px solid #e9ecef",
                        padding="12px 24px",
                        border_radius="6px",
                        font_weight="400",
                        font_size="1.1rem",
                        cursor="pointer",
                        transition="all 0.2s ease",
                        hover_background="#2c3e50",
                        hover_color="white",
                        hover_border_color="#2c3e50",
                    ),
                    flex_direction="row",
                    gap="15px",
                    margin_top="25px",
                ),
                align_items="center",
                gap="20px",
                flex_direction="column",
            ),
            padding="40px",
            background="white",
            border_radius="12px",
            box_shadow="0 4px 20px rgba(0,0,0,0.08)",
            border="1px solid #f1f3f4",
            min_width="320px",
            align_items="center",
        ),
        padding="40px",
        background="linear-gradient(135deg, #fafbfc 0%, #f4f6f8 100%)",
        min_height="100vh",
        display="flex",
        justify_content="center",
        align_items="center",
        flex_direction="column",
    )


app.start(port=1337)
