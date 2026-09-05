from quillion import app, page, text, button, heading, input, div, span, var
import random

# ── Reactive State ──────────────────────────────────────────
counter = var(0)
name = var("Ada")
clicks = var(0)

# ── Reactive Collections ────────────────────────────────────
items = var([])
todos = var([
    {"text": "Learn Quillion", "done": False},
    {"text": "Build awesome app", "done": False},
])
user_data = var({"name": "Alice", "age": 25, "city": "Wonderland"})
tags = var({"react", "python", "quillion"})

# ── User Class ──────────────────────────────────────────────
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
        self._hobbies = []
    
    def birthday(self):
        self.age += 1
    
    def add_hobby(self, hobby: str):
        self._hobbies.append(hobby)
    
    @property
    def hobbies(self):
        return self._hobbies
    
    def __str__(self):
        return f"{self.name} ({self.age})"

person = var(Person("Charlie", 30))

# ── Functions ──────────────────────────────────────────────
def reset():
    counter.set(0)

def add_item():
    items.value.append(f"Item {len(items.value) + 1}")

def remove_item():
    if len(items.value) > 0:
        items.value.pop()

def clear_items():
    items.value.clear()

def add_todo():
    todos.value.append({"text": f"Task {len(todos.value) + 1}", "done": False})

def toggle_todo(index: int):
    if 0 <= index < len(todos.value):
        todos.value[index]["done"] = not todos.value[index]["done"]

def remove_todo(index: int):
    if 0 <= index < len(todos.value):
        todos.value.pop(index)

def update_user_data():
    user_data.value["age"] = user_data.value["age"] + 1
    user_data.value["city"] = "New Wonderland"

def add_tag():
    tags.value.add(f"tag_{len(tags.value) + 1}")

def remove_tag():
    if len(tags.value) > 0:
        tags.value.pop()

def person_birthday():
    person.value.birthday()

def person_add_hobby():
    hobbies = ["reading", "gaming", "coding", "hiking", "painting"]
    person.value.add_hobby(random.choice(hobbies))

def get_hobbies_text():
    hobbies = person.value.hobbies
    if not hobbies:
        return "No hobbies yet"
    return ", ".join(hobbies)

# ── Page ──────────────────────────────────────────────────────
@page("/")
def home():
    # Получаем данные для рендеринга
    items_list = list(items.value)
    todos_list = list(todos.value)
    tags_list = list(tags.value)
    user = dict(user_data.value)
    p = person.value
    
    return div(
        # ── Header ──
        div(
            heading("Quillion", level=1),
        ),

        # ── Stats Grid ──
        div(
            div(
                span(counter),
                text("Counter"),
            ),
            div(
                span(clicks),
                text("Interactions"),
            ),
            div( 
                span(name),
                text("Name"),
            ),
            div(
                span("Active"),
                text("Status"),
            ),
        ),

        # ── Interactive Section ──
        div(
            heading("Controls", level=3),

            div(
                button("− Decrement", on_click=counter - 1),
                button("Reset", on_click=reset),
                button("+ Increment", on_click=counter + 1),
            ),

            div(
                button("×2", on_click=counter * 2),
                button("² Power", on_click=counter ** 2),
                button("÷2", on_click=counter / 2),
            ),
        ),

        # ── Name Input ──
        div(
            text("Your name:"),
            input(bind_var=name, placeholder="Enter your name..."),
        ),

        # ── Click Tracker ──
        div(
            text(
                "Total clicks: ",
                span(clicks),
            ),
        ),

        # ── Reactive List Example ──
        div(
            heading("📋 Reactive List", level=3),
            div(
                button("Add Item", on_click=add_item),
                button("Remove Last", on_click=remove_item),
                button("Clear All", on_click=clear_items),
            ),
            div(
                *[span(f"• {item}") for item in items_list],
                text("(empty)") if not items_list else "",
            ),
        ),

        # ── Todos Example ──
        div(
            heading("✅ Todos", level=3),
            div(
                button("Add Todo", on_click=add_todo),
            ),
            div(
                *[
                    div(
                        # ✅ Фикс: используем functools.partial или создаём функции на месте
                        button("✓" if todo["done"] else "○", 
                               on_click=(lambda idx: lambda: toggle_todo(idx))(i)),
                        text(todo["text"]),
                        button("✕", on_click=(lambda idx: lambda: remove_todo(idx))(i)),
                        style={"display": "flex", "gap": "8px", "margin": "4px 0"}
                    )
                    for i, todo in enumerate(todos_list)
                ],
                text("No todos yet") if not todos_list else "",
            ),
        ),

        # ── User Data (Dict) Example ──
        div(
            heading("👤 User Data (Reactive Dict)", level=3),
            div(
                text(f"Name: {user['name']}"),
                text(f"Age: {user['age']}"),
                text(f"City: {user['city']}"),
                button("Age +1", on_click=update_user_data),
            ),
        ),

        # ── Tags (Set) Example ──
        div(
            heading("🏷️ Tags (Reactive Set)", level=3),
            div(
                button("Add Tag", on_click=add_tag),
                button("Remove Tag", on_click=remove_tag),
            ),
            div(
                *[span(f"#{tag}") for tag in tags_list],
                text("(empty)") if not tags_list else "",
                style={"display": "flex", "gap": "8px", "flex-wrap": "wrap"}
            ),
        ),

        # ── Person (User Class) Example ──
        div(
            heading("🧑 Person (Reactive Class)", level=3),
            div(
                text(f"Name: {p.name}"),
                text(f"Age: {p.age}"),
                text(f"Hobbies: {get_hobbies_text()}"),
                button("🎂 Birthday!", on_click=person_birthday),
                button("➕ Add Hobby", on_click=person_add_hobby),
            ),
        ),

        # ── Footer ──
        div(
            text("Built with Quillion · Reactive Python UI"),
        ),
    )


app.run(http_port=8081)