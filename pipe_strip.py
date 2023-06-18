#!/usr/bin/env python3

from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.app import App, ComposeResult
from textual.color import Color
from textual.strip import Strip
from textual.widget import Widget

from auto_restart import restart_on_changes

colors = {
    "wallpaper": Color.parse("#faa6ad"),
    "carpet": "#3c6602",
    "cat": "#faa817",
    "cat_mouth": "#fdff7a",
    "cat_nose": "#ffc2d6",
    "pipe": "#923dfd",
    "skin": "#fce9bb",
    "hair": "#a94300",
    "shoe": "#a94300",
    "shirt": "#7bffff",
    "chair": "#90a8fe",
    "chair_shadow": "#5c8aed",
    "table": "#b19187",
    "table_shadow": "#9c5f56",
    "paper": "#fdfffd",
    "sequel_wallpaper": "#84feb3",
    "sequel_carpet": "#1492fc",
    "sequel_smoke": "#dde6e4",
}

class PipeStrip(Widget):

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget."""
        bg_color = colors["wallpaper"]
        bg_style = Style(bgcolor=bg_color.rich_color, color="black")
        segments = []
        x = int(y * 10 - 15)
        segments.append(Segment("░" * x, bg_style, None))
        segments.append(Segment(" " * (self.size.width - x), bg_style, None))
        return Strip(segments)

class PipeStripApp(App):
    def on_resize(self, event: events.Resize) -> None:
        global tank_width, tank_height

    def compose(self) -> ComposeResult:
        yield PipeStrip()

app = PipeStripApp()

# Must be before app.run() which blocks until the app exits.
# Takes the app in order to do some clean up of the app before restarting.
restart_on_changes(app)

if __name__ == "__main__":
    app.run()
