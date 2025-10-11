import pytest
import uuid
from unittest.mock import Mock, patch

from quillion.components.ui.element import Element, MediaElement, StyleProperty


class TestStyleProperty:
    def test_style_property_initialization(self):
        prop = StyleProperty("backgroundColor", "red")
        assert prop._key == "backgroundColor"
        assert prop._value == "red"

    def test_to_css_properties_dict_camel_case(self):
        prop = StyleProperty("backgroundColor", "red")
        result = prop.to_css_properties_dict()
        assert result == {"background-color": "red"}

    def test_to_css_properties_dict_snake_case(self):
        prop = StyleProperty("font_size", "16px")
        result = prop.to_css_properties_dict()
        assert result == {"font-size": "16px"}

    def test_to_css_properties_dict_mixed_case(self):
        prop = StyleProperty("borderLeftWidth", "2px")
        result = prop.to_css_properties_dict()
        assert result == {"border-left-width": "2px"}

    def test_to_css_properties_dict_already_kebab(self):
        prop = StyleProperty("font-size", "16px")
        result = prop.to_css_properties_dict()
        assert result == {"font-size": "16px"}

    def test_to_css_properties_dict_numeric_value(self):
        prop = StyleProperty("opacity", 0.5)
        result = prop.to_css_properties_dict()
        assert result == {"opacity": "0.5"}

    def test_to_css_properties_dict_boolean_value(self):
        prop = StyleProperty("display", True)
        result = prop.to_css_properties_dict()
        assert result == {"display": "True"}


class TestElement:
    def test_element_initialization_basic(self):
        element = Element("div")
        assert element.tag == "div"
        assert element.text is None
        assert element.event_handlers == {}
        assert element.children == []
        assert element.attributes == {}
        assert element.styles == {}
        assert element.css_classes == []
        assert element.key is None
        assert element.style_properties == []

    def test_element_initialization_with_text(self):
        element = Element("p", text="Hello World")
        assert element.tag == "p"
        assert element.text == "Hello World"

    def test_element_initialization_with_class_name(self):
        element = Element("div", class_name="container")
        assert "container" in element.css_classes

    def test_element_initialization_with_classes_list(self):
        element = Element("div", classes=["class1", "class2"])
        assert "class1" in element.css_classes
        assert "class2" in element.css_classes

    def test_element_initialization_with_both_class_name_and_classes(self):
        element = Element("div", class_name="main", classes=["class1", "class2"])
        assert "main" in element.css_classes
        assert "class1" in element.css_classes
        assert "class2" in element.css_classes

    def test_element_initialization_with_key(self):
        element = Element("div", key="unique-key")
        assert element.key == "unique-key"

    def test_element_initialization_with_event_handlers(self):
        def click_handler():
            pass

        def mouseover_handler():
            pass

        element = Element(
            "button",
            event_handlers={"click": click_handler, "mouseover": mouseover_handler},
        )
        assert element.event_handlers["click"] == click_handler
        assert element.event_handlers["mouseover"] == mouseover_handler

    def test_element_initialization_with_inline_styles(self):
        element = Element("div", styles={"color": "red", "font-size": "16px"})
        assert element.styles["color"] == "red"
        assert element.styles["font-size"] == "16px"

    def test_element_initialization_with_on_prefix_handlers(self):
        def click_handler():
            pass

        def mouseover_handler():
            pass

        element = Element(
            "button", on_click=click_handler, on_mouseover=mouseover_handler
        )
        assert element.event_handlers["click"] == click_handler
        assert element.event_handlers["mouseover"] == mouseover_handler

    def test_element_initialization_with_style_string(self):
        element = Element("div", style="color: red; font-size: 16px;")
        assert element.styles["color"] == "red"
        assert element.styles["font-size"] == "16px"

    def test_element_initialization_with_regular_attributes(self):
        element = Element("input", type="text", id="name", name="username")

        assert len(element.style_properties) == 3
        style_keys = [prop._key for prop in element.style_properties]
        assert "type" in style_keys
        assert "id" in style_keys
        assert "name" in style_keys

    def test_append_single_child(self):
        parent = Element("div")
        child = Element("span")

        result = parent.append(child)

        assert len(parent.children) == 1
        assert parent.children[0] == child
        assert result == parent

    def test_append_multiple_children(self):
        parent = Element("div")
        child1 = Element("span")
        child2 = Element("p")
        child3 = Element("div")

        result = parent.append(child1, child2, child3)

        assert len(parent.children) == 3
        assert parent.children == [child1, child2, child3]
        assert result == parent

    def test_add_class(self):
        element = Element("div")
        element.add_class("container")

        assert "container" in element.css_classes

    def test_add_class_duplicate(self):
        element = Element("div", classes=["container"])
        element.add_class("container")

        assert element.css_classes == ["container"]

    def test_add_event_handler(self):
        element = Element("button")

        def click_handler():
            pass

        element.add_event_handler("click", click_handler)

        assert element.event_handlers["click"] == click_handler

    def test_add_event_handler_overwrite(self):
        element = Element("button")

        def old_handler():
            pass

        def new_handler():
            pass

        element.add_event_handler("click", old_handler)
        element.add_event_handler("click", new_handler)

        assert element.event_handlers["click"] == new_handler

    def test_set_attribute(self):
        element = Element("div")
        element.set_attribute("data-test", "value")

        assert element.attributes["data-test"] == "value"

    def test_set_attribute_overwrite(self):
        element = Element("div")
        element.set_attribute("id", "old")
        element.set_attribute("id", "new")

        assert element.attributes["id"] == "new"

    @patch("uuid.uuid4")
    def test_to_dict_basic(self, mock_uuid):
        mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")

        element = Element("div", text="Hello")
        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)

        expected = {"tag": "div", "attributes": {}, "text": "Hello", "children": []}
        assert result == expected

    @patch("uuid.uuid4")
    def test_to_dict_with_event_handlers(self, mock_uuid):
        mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")

        def click_handler():
            pass

        element = Element("button", event_handlers={"click": click_handler})
        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)

        assert result["attributes"]["onclick"] == "12345678-1234-5678-1234-567812345678"
        assert (
            mock_app.callbacks["12345678-1234-5678-1234-567812345678"] == click_handler
        )

    def test_to_dict_with_inline_styles(self):
        element = Element("div", styles={"color": "red", "font-size": "16px"})
        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)

        assert "style" in result["attributes"]
        style_attr = result["attributes"]["style"]
        assert "color: red;" in style_attr
        assert "font-size: 16px;" in style_attr

    def test_to_dict_with_style_properties(self):
        element = Element("div", backgroundColor="red", fontSize="16px")
        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)

        assert "style" in result["attributes"]
        style_attr = result["attributes"]["style"]
        assert "background-color: red;" in style_attr
        assert "font-size: 16px;" in style_attr

    def test_to_dict_with_mixed_styles(self):
        element = Element("div", styles={"color": "red"}, backgroundColor="blue")
        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)

        assert "style" in result["attributes"]
        style_attr = result["attributes"]["style"]
        assert "color: red;" in style_attr
        assert "background-color: blue;" in style_attr

    def test_to_dict_with_css_classes(self):
        element = Element("div", classes=["container", "main"])
        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)

        assert result["attributes"]["class"] == "container main"

    def test_to_dict_with_existing_class_attribute(self):
        element = Element("div", classes=["container", "main"])
        element.attributes["class"] = "existing"
        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)

        assert result["attributes"]["class"] == "existing container main"

    def test_to_dict_with_key(self):
        element = Element("div", key="unique-key")
        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)

        assert result["key"] == "unique-key"

    def test_to_dict_with_children(self):
        parent = Element("div")
        child1 = Element("span", text="Child 1")
        child2 = Element("p", text="Child 2")
        parent.append(child1, child2)

        mock_app = Mock()
        mock_app.callbacks = {}

        result = parent.to_dict(mock_app)

        assert len(result["children"]) == 2
        assert result["children"][0]["tag"] == "span"
        assert result["children"][0]["text"] == "Child 1"
        assert result["children"][1]["tag"] == "p"
        assert result["children"][1]["text"] == "Child 2"

    def test_to_dict_with_css_child(self):
        from quillion.components import CSS

        css = CSS(["styles.css"])
        element = Element("div")
        element.append(css)

        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)

        assert len(result["children"]) == 1
        assert result["children"][0]["tag"] == "link"

    def test_to_dict_with_non_element_child(self):
        element = Element("div")
        element.append("raw text")

        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)

        assert len(result["children"]) == 1
        assert result["children"][0] == "raw text"


class TestMediaElement:
    def test_media_element_initialization(self):
        media = MediaElement("img", src="image.jpg")
        assert media.tag == "img"
        assert media.src == "image.jpg"

    def test_media_element_inherits_from_element(self):
        assert issubclass(MediaElement, Element)

    def test_media_element_initialization_with_all_properties(self):
        def load_handler():
            pass

        media = MediaElement(
            "video",
            src="video.mp4",
            event_handlers={"load": load_handler},
            styles={"width": "100%"},
            classes=["video-player"],
            key="video-1",
            class_name="media",
            controls=True,
        )

        assert media.tag == "video"
        assert media.src == "video.mp4"
        assert media.event_handlers["load"] == load_handler
        assert media.styles["width"] == "100%"
        assert "video-player" in media.css_classes
        assert "media" in media.css_classes
        assert media.key == "video-1"
        control_props = [
            prop for prop in media.style_properties if prop._key == "controls"
        ]
        assert len(control_props) == 1

    def test_media_element_to_dict_external_url(self):
        media = MediaElement("img", src="https://example.com/image.jpg")
        mock_app = Mock()
        mock_app.callbacks = {}

        result = media.to_dict(mock_app)

        assert result["attributes"]["src"] == "https://example.com/image.jpg"

    def test_media_element_to_dict_local_asset(self):
        media = MediaElement("img", src="/assets/images/photo.jpg")
        mock_app = Mock()
        mock_app.callbacks = {}
        mock_app.asset_server_url = "http://localhost:8000/assets"
        mock_app.assets_path = "/assets"

        result = media.to_dict(mock_app)

        expected_src = "http://localhost:8000/assets/images/photo.jpg"
        assert result["attributes"]["src"] == expected_src

    def test_media_element_to_dict_inherits_parent_behavior(self):
        def load_handler():
            pass

        media = MediaElement(
            "img",
            src="image.jpg",
            event_handlers={"load": load_handler},
            classes=["thumbnail"],
            key="img-1",
        )

        mock_app = Mock()
        mock_app.callbacks = {}
        mock_app.asset_server_url = "http://localhost:8000/assets"
        mock_app.assets_path = "/assets"

        with patch("uuid.uuid4") as mock_uuid:
            mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
            result = media.to_dict(mock_app)

        assert result["attributes"]["src"].startswith("http://localhost:8000/assets")

        assert result["attributes"]["class"] == "thumbnail"
        assert result["key"] == "img-1"
        assert "onload" in result["attributes"]


class TestElementEdgeCases:
    def test_element_empty_style_string(self):
        element = Element("div", style="")
        assert element.styles == {}

    def test_element_malformed_style_string(self):
        element = Element("div", style="color:red;invalid;font-size:16px;")
        assert "color" in element.styles
        assert "font-size" in element.styles
        assert element.styles["color"] == "red"
        assert element.styles["font-size"] == "16px"

    def test_element_style_string_with_spaces(self):
        element = Element("div", style="  color :  red  ;  font-size  :  16px  ;  ")
        assert element.styles["color"] == "red"
        assert element.styles["font-size"] == "16px"

    def test_element_special_characters_in_text(self):
        element = Element("div", text='Hello "World" <with> & special chars')
        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)
        assert result["text"] == 'Hello "World" <with> & special chars'

    def test_element_none_values(self):
        element = Element("div", text=None, key=None)
        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)
        assert result["text"] is None
        assert "key" not in result

    def test_element_empty_children(self):
        element = Element("div")
        element.children = []

        mock_app = Mock()
        mock_app.callbacks = {}

        result = element.to_dict(mock_app)
        assert result["children"] == []

    def test_element_duplicate_event_handlers(self):
        def handler1():
            pass

        def handler2():
            pass

        element = Element("button", event_handlers={"click": handler1})
        element.add_event_handler("click", handler2)

        mock_app = Mock()
        mock_app.callbacks = {}

        with patch("uuid.uuid4") as mock_uuid:
            mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
            result = element.to_dict(mock_app)

        assert mock_app.callbacks["12345678-1234-5678-1234-567812345678"] == handler2


class TestElementIntegration:
    def test_complex_element_structure(self):
        page = Element("div", class_name="page")

        header = Element("header", class_name="header")
        title = Element("h1", text="Welcome")
        header.append(title)

        content = Element("main", class_name="content")
        paragraph = Element("p", text="This is a paragraph.")
        button = Element("button", text="Click me", on_click=lambda: None)
        content.append(paragraph, button)

        footer = Element("footer", class_name="footer")
        copyright = Element("span", text="© 2024")
        footer.append(copyright)

        page.append(header, content, footer)

        mock_app = Mock()
        mock_app.callbacks = {}

        result = page.to_dict(mock_app)

        assert result["tag"] == "div"
        assert "page" in result["attributes"]["class"]
        assert len(result["children"]) == 3

        header_dict = result["children"][0]
        assert header_dict["tag"] == "header"
        assert "header" in header_dict["attributes"]["class"]

        content_dict = result["children"][1]
        assert content_dict["tag"] == "main"
        assert "content" in content_dict["attributes"]["class"]

        footer_dict = result["children"][2]
        assert footer_dict["tag"] == "footer"
        assert "footer" in footer_dict["attributes"]["class"]

    def test_element_with_all_features(self):
        def click_handler():
            pass

        def mouseover_handler():
            pass

        element = Element(
            "button",
            text="Click me",
            event_handlers={"click": click_handler},
            styles={"border": "1px solid black"},
            classes=["btn", "primary"],
            key="submit-btn",
            class_name="custom-btn",
            on_mouseover=mouseover_handler,
            style="padding: 10px;",
            id="button-id",
            disabled=True,
        )

        mock_app = Mock()
        mock_app.callbacks = {}

        with patch("uuid.uuid4") as mock_uuid:
            mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
            result = element.to_dict(mock_app)

        assert result["tag"] == "button"
        assert result["text"] == "Click me"
        assert result["key"] == "submit-btn"

        assert "onclick" in result["attributes"]
        assert "onmouseover" in result["attributes"]

        class_attr = result["attributes"]["class"]
        assert "btn" in class_attr
        assert "primary" in class_attr
        assert "custom-btn" in class_attr

        style_attr = result["attributes"]["style"]
        assert "border: 1px solid black;" in style_attr
        assert "padding: 10px;" in style_attr

        assert "disabled" not in result["attributes"]  # became style property


class TestElementPerformance:
    def test_to_dict_performance_large_structure(self):
        import time

        root = Element("div")

        for i in range(100):
            child = Element("div", text=f"Child {i}")
            for j in range(10):
                grandchild = Element("span", text=f"Grandchild {j}")
                child.append(grandchild)
            root.append(child)

        mock_app = Mock()
        mock_app.callbacks = {}

        start_time = time.time()
        result = root.to_dict(mock_app)
        end_time = time.time()

        assert (end_time - start_time) < 1.0, "to_dict too slow for large structure"

        assert len(result["children"]) == 100

    def test_append_performance_many_children(self):
        import time

        parent = Element("div")

        start_time = time.time()

        for i in range(1000):
            child = Element("span", text=str(i))
            parent.append(child)

        end_time = time.time()

        assert (end_time - start_time) < 0.1, "append too slow for many children"
        assert len(parent.children) == 1000
