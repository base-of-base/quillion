from quillion.components import text
from quillion import app, page


@page("/")
def home():
    return text("Hello world!")


app.start()
