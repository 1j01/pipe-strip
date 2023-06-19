#!/usr/bin/env python3

import argparse
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

parser = argparse.ArgumentParser() #prog="pipe-strip")

parser.add_argument("--cyclic", action="store_true", help="allows for infinite viewing")
parser.add_argument("--smoke-test", action="store_true", help="runs smoke test")
# parser.add_argument("-2", "--sql", "--sequel", action="store_true", help="Part II")
parser.add_argument("--sql", "--take-pipe", action="store_true", help="retrieves pipe and takes command")

args = parser.parse_args()

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

colors_css = "\n".join([f"${name}: {color.css};" for name, color in colors.items()])

file_path = "resources/pipe_strip_v12.ans"
if args.sql:
    file_path = "resources/pipe_strip_sequel_v6.ans"
with open(file_path, "r") as f:
    image_text_lines = [Text.from_ansi(line) for line in f.readlines()]

if args.cyclic:
    border = Text.from_markup("▌▐", style=Style(bgcolor=colors["paper"].rich_color, color=colors["pen"].rich_color))
    image_text_lines = [line + border for line in image_text_lines]

image_width = image_text_lines[0].__rich_measure__(None, None).maximum  # type: ignore
image_height = len(image_text_lines)

class PipeStrip(Widget):

    time = reactive(0.0)

    def on_mount(self) -> None:
        """Called when the widget is added to a layout."""
        if not args.cyclic:
            return
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

class SmokeTest(Widget):

    time = reactive(0.0)

    if args.sql:
        smoke_style = Style(bgcolor=colors["sequel_smoke"].rich_color)
        bg_style = Style(bgcolor=colors["sequel_wallpaper"].rich_color)
    else:
        smoke_style = Style(bgcolor=colors["paper"].rich_color)
        bg_style = Style(bgcolor=colors["wallpaper"].rich_color)
    outline_style = Style(bgcolor=colors["pen"].rich_color)

    def on_mount(self) -> None:
        """Called when the widget is added to a layout."""
        def advance_time() -> None:
            self.time += 0.1
        self.set_interval(0.1, advance_time)

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget."""
        segments = []
        x = int(self.size.width * 0.2 * math.sin(self.time + y / 5) + self.size.width * 0.5)
        x_above = int(self.size.width * 0.2 * math.sin(self.time + (y - 1) / 5) + self.size.width * 0.5)
        width = int(self.size.width * 0.2)
        left = x - width
        right = x + width
        outline_length = int(math.fabs(x - x_above) + 1)
        segments.append(Segment(" " * left, self.bg_style, None))
        segments.append(Segment(" " * outline_length, self.outline_style, None))
        segments.append(Segment(" " * (right - left - outline_length * 2), self.smoke_style, None))
        segments.append(Segment(" " * outline_length, self.outline_style, None))
        segments.append(Segment(" " * (self.size.width - right), self.bg_style, None))
        return Strip(segments)


class PipeStripApp(App):
    # def on_resize(self, event: events.Resize) -> None:
    #     global terminal_width, terminal_height
    #     terminal_width = event.size.width
    #     terminal_height = event.size.height

    DEFAULT_CSS = colors_css + """
    Screen {
        align: center middle;
        background: $wallpaper !important;
    }
    .sequel Screen {
        background: $sequel_wallpaper !important;
    }
    PipeStrip {
        width: auto;
        height: auto;
    }
    SmokeTest {
        width: 100%;
        height: 100%;
    }
    """

    def on_mount(self) -> None:
        if args.sql:
            self.add_class("sequel")

    def compose(self) -> ComposeResult:
        if args.smoke_test:
            yield SmokeTest()
        else:
            yield PipeStrip()

app = PipeStripApp()

# Must be called before app.run() which blocks until the app exits.
# Takes the app in order to do some clean up of the app before restarting.
restart_on_changes(app)

def main():
    app.run()

if __name__ == "__main__":
    main()
