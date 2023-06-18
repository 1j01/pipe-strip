#!/usr/bin/env python3

import math
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.color import Color
from textual.geometry import Size
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from auto_restart import restart_on_changes

colors: dict[str, Color] = {
    "pen": Color.parse("#000000"),
    "wallpaper": Color.parse("#faa6ad"),
    "carpet": Color.parse("#3c6602"),
    "cat": Color.parse("#faa817"),
    "cat_mouth": Color.parse("#fdff7a"),
    "cat_nose": Color.parse("#ffc2d6"),
    "skin": Color.parse("#fce9bb"),
    "hair": Color.parse("#a94300"),
    "shoe": Color.parse("#a94300"),
    "shirt": Color.parse("#7bffff"),
    "chair": Color.parse("#90a8fe"),
    "chair_shadow": Color.parse("#5c8aed"),
    "table": Color.parse("#b19187"),
    "table_shadow": Color.parse("#9c5f56"),
    "paper": Color.parse("#fdfffd"),
    "sequel_wallpaper": Color.parse("#84feb3"),
    "sequel_carpet": Color.parse("#1492fc"),
    "sequel_smoke": Color.parse("#dde6e4"),
    "pipe": Color.parse("#923dfd"),
}

with open("resources/pipe_strip_v12.ans", "r") as f:
    image_text_lines = [Text.from_ansi(line) for line in f.readlines()]

image_width = image_text_lines[0].__rich_measure__(None, None).maximum  # type: ignore
image_height = len(image_text_lines)

class PipeStrip(Widget):

    time = reactive(0.0)

    def on_mount(self) -> None:
        """Called when the widget is added to a layout."""
        def advance_time() -> None:
            self.time += 0.1
        self.set_interval(0.1, advance_time)

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget."""
        # bg_color = colors["wallpaper"]
        # fg_color = colors["pen"]
        # bg_style = Style(bgcolor=bg_color.rich_color, color=fg_color.rich_color)
        # segments = []
        # x = int(y * 10 * math.sin(self.time) - 15)
        # segments.append(Segment("░" * x, bg_style, None))
        # segments.append(Segment(" " * (self.size.width - x), bg_style, None))
        if y < len(image_text_lines):
            # marquee effect
            x = int(self.time) % image_width
            before, after = image_text_lines[y].divide([x])
            segments = [*after.render(self.app.console, ""), *before.render(self.app.console, "")]
        else:
            segments = []

        return Strip(segments)
    
    def get_content_width(self, container: Size, viewport: Size) -> int:
        return image_width
    
    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return image_height

class PipeStripApp(App):
    # def on_resize(self, event: events.Resize) -> None:
    #     global terminal_width, terminal_height
    #     terminal_width = event.size.width
    #     terminal_height = event.size.height

    DEFAULT_CSS = """
    Screen {
        align: center middle;
    }
    PipeStrip {
        width: auto;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield PipeStrip()

app = PipeStripApp()

# Must be before app.run() which blocks until the app exits.
# Takes the app in order to do some clean up of the app before restarting.
restart_on_changes(app)

if __name__ == "__main__":
    app.run()
