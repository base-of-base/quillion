from quillion.components import container, text, button, State
from quillion import app, page, Path


@page("/user-id/{user_id}")
def user_page(user_id):
    return container(
        container(
            text(
                f"User Profile: {user_id}",
                size="2rem",
                color="#2c3e50",
                weight="300",
                letter_spacing="0.5px",
                margin_bottom="20px",
            ),
            padding="40px",
            background="white",
            border_radius="12px",
            box_shadow="0 4px 20px rgba(0,0,0,0.08)",
            border="1px solid #f1f3f4",
            align_items="center",
            gap="20px",
            flex_direction="column",
        ),
        padding="40px",
        background="linear-gradient(135deg, #fafbfc 0%, #f4f6f8 100%)",
        min_height="100vh",
        display="flex",
        justify_content="center",
        align_items="center",
        flex_direction="column",
    )


app.start()
