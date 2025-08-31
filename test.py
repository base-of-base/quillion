import asyncio
import json
import websockets
from typing import Callable, Dict, List, Optional, Any, Type, TypeVar, Tuple
from quillion import *


class CounterState(ReactiveState):
    count: int = 0

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1


class CounterComponent(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def render_component(self) -> Element:
        state = self.use_state(CounterState)
        count_text = Text(
            f"Counter: {state.count}",
            inline_style_properties={"font-size": "20px", "margin-bottom": "10px"},
        )
        inc_button = Button("Increment", on_click=state.increment)
        dec_button = Button("Decrement", on_click=state.decrement)
        canvas = Canvas(
            width=300,
            height=150,
            inline_style_properties={"border": "1px solid #777", "margin-top": "10px"},
        )
        return Container(
            count_text,
            inc_button,
            dec_button,
            canvas,
            DisplayFlex(direction="column", align="center", gap=10),
            inline_style_properties={
                "padding": "15px",
                "border": "1px solid #777",
                "border-radius": "5px",
            },
        )


class HomePage(Page):
    router = "/"

    def render(self) -> Element:
        button = Button("Button")
        about_button = Button("About Us", on_click=self.go_about)
        dashboard_button = Button("Dashboard", on_click=self.go_dashboard)
        return Container(
            button,
            about_button,
            dashboard_button,
            DisplayFlex(direction="column", align="center", gap=20),
        )

    def go_about(self):
        Path.navigate(to="/about/")

    def go_dashboard(self):
        Path.navigate(to="/dashboard/")


class AboutPageStyles(Style):
    def styles(self) -> Container:
        return Container(
            Background(color=Color("#282c34")),
            TextColor("#61dafb"),
            ButtonBase(
                Background(color=Color("#61dafb")),
                TextColor("#282c34"),
                Border("1px", "solid", "#61dafb"),
                BorderRadius("8px"),
                Padding("10px 20px"),
            ),
            ButtonHover(
                Background(color=Color("#282c34")),
                TextColor("#61dafb"),
                BorderColor("#61dafb"),
            ),
            ParagraphBase(FontSize("24px"), TextColor("#61dafb")),
        )


class AboutPage(Page):
    router = "/about/"

    def render(self) -> Element:
        text = Text("Hello, this is the 'About Us' page")
        back_button = Button("Back", on_click=self.go_home)
        return Container(
            text, back_button, DisplayFlex(direction="column", align="center", gap=15)
        )

    def go_home(self):
        Path.navigate(to="/")

    @style
    def styles(self) -> AboutPageStyles:
        return AboutPageStyles()


class DashboardPage(Page):
    router = "/dashboard/"

    def __init__(self):
        super().__init__()
        self.item_count = 3
        self.items_data = self._generate_items(self.item_count)

    def _generate_items(self, count):
        return [{"id": str(i), "text": f"Item {i+1}"} for i in range(count)]

    def add_item(self):
        self.item_count += 1
        new_item = {
            "id": str(self.item_count - 1),
            "text": f"Item {self.item_count}",
        }
        self.items_data.append(new_item)
        print(f"Adding item: {new_item}")
        asyncio.create_task(
            Path._app.render_current_page(Path._app.websocket)
        )

    def remove_last_item(self):
        if self.item_count > 0:
            removed_item = self.items_data.pop()
            self.item_count -= 1
            print(f"Removing item: {removed_item}")
            asyncio.create_task(
                Path._app.render_current_page(Path._app.websocket)
            )

    def render(self) -> Element:
        title = Text(
            "Dashboard",
            inline_style_properties={
                "font-size": "32px",
                "font-weight": "bold",
                "margin-bottom": "30px",
            },
        )

        item_list_elements = []
        for item in self.items_data:
            item_list_elements.append(
                Container(
                    Text(item["text"], inline_style_properties={"font-size": "20px"}),
                    key=item["id"],
                    inline_style_properties={
                        "padding": "10px",
                        "border": "1px solid #777",
                        "margin-bottom": "5px",
                        "background-color": "#555",
                    },
                )
            )

        list_container = Container(
            *item_list_elements,
            DisplayFlex(direction="column", align="stretch", gap=5),
            inline_style_properties={
                "width": "300px",
                "margin-top": "20px",
                "border": "1px dashed #aaa",
                "padding": "10px",
            },
        )

        add_button = Button("Add Item", on_click=self.add_item)
        remove_button = Button("Remove Last", on_click=self.remove_last_item)
        list_controls = Container(
            add_button, remove_button, DisplayFlex(direction="row", gap=10)
        )

        go_home_button = Button("Go Home", on_click=self.go_home)
        go_about_button = Button("About Us", on_click=self.go_about)

        return Container(
            title,
            list_controls,
            list_container,
            CounterComponent(
                key="counter-1",
                inline_style_properties={"margin-top": "20px"},
            ),
            Container(
                go_home_button, go_about_button, DisplayFlex(direction="row", gap=20)
            ),
            DisplayFlex(direction="column", align="center", gap=20),
        )

    def go_home(self):
        Path.navigate(to="/")

    def go_about(self):
        Path.navigate(to="/about/")


class BaseStyle(Style):
    @property
    def is_global(self) -> bool:
        return True

    def styles(self) -> Container:
        return Container(
            FontFamily("Verdana", "Geneva", "sans-serif"),
            Background(color=Color("#000000")),
            Margin("0"),
            Padding("0"),
            MinHeight("100vh"),
            DisplayFlex(direction="column", align="center", justify="center"),
            ParagraphBase(
                FontFamily("Arial", "sans-serif"),
                TextColor("#F0F0F0"),
                Margin("0"),
                LineHeight(1.5),
                FontSize("18px"),
            ),
            ButtonBase(
                Background(color=Color("#FFFFFF")),
                TextColor("#000000"),
                Border("1px", "solid", "#FFFFFF"),
                Padding("12px 25px"),
                Cursor("pointer"),
                Transition("all 0.3s ease"),
                BorderRadius("25px"),
                BoxShadow("0 5px 15px rgba(0, 0, 0, 0.3)"),
            ),
            ButtonHover(
                Background(color=Color("#000000")),
                TextColor("#FFFFFF"),
                Border("1px", "solid", "#FFFFFF"),
                BoxShadow("0 8px 20px rgba(0, 0, 0, 0.4)"),
            ),
            LinkBase(
                TextColor("#ADD8E6"), TextDecoration("underline"), Cursor("pointer")
            ),
            LinkHover(TextColor("#87CEEB")),
        )


if __name__ == "__main__":
    app = Quillion()
    app.start("0.0.0.0", 1337)
