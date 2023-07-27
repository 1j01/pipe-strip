#!/usr/bin/env python3

import argparse
from functools import cache
import math
import os
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.color import Color
from textual.geometry import Size
from textual.reactive import reactive, var
from textual.strip import Strip
from textual.widget import Widget

parser = argparse.ArgumentParser() #prog="pipe-strip")

parser.add_argument("--cyclic", action="count", default=0, help="allows for infinite viewing; can be specified 1-3 times to increase verbosity")
parser.add_argument("--smoke-test", action="store_true", help="runs smoke test")
parser.add_argument("--sql", "--take-pipe", action="store_true", help="retrieves pipe and takes command, in sequel")
parser.add_argument("--dev", action="store_true", help="enables auto-restart on file changes")

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

original_file_paths = [
    "resources/pipe_strip_v12.ans",
    "resources/pipe_strip_mini_v2.ans",
    "resources/pipe_strip_micro_v1.ans",
]
sequel_file_paths = [
    "resources/pipe_strip_sequel_v7.ans",
    "resources/pipe_strip_sequel_mini_v1.ans",
    "resources/pipe_strip_sequel_micro_v4.ans",
]
original_file_paths = [os.path.join(os.path.dirname(__file__), path) for path in original_file_paths]
sequel_file_paths = [os.path.join(os.path.dirname(__file__), path) for path in sequel_file_paths]

class PipeStrip(Widget):

    time = reactive(0.0)

    image_text_lines = var[list[Text]]([])
    image_width = reactive[int](0, layout=True)
    image_height = reactive[int](0, layout=True)

    def on_mount(self) -> None:
        """Called when the widget is added to a layout."""
        self.update_image()
        if not args.cyclic:
            return
        def advance_time() -> None:
            self.time += 0.1
        self.set_interval(0.1, advance_time)

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget."""
        if y < len(self.image_text_lines):
            # marquee effect
            x = int(self.time) % self.image_width
            before, after = self.image_text_lines[y].divide([x])
            segments = [*after.render(self.app.console, ""), *before.render(self.app.console, "")]
        else:
            segments = []

        return Strip(segments)

    @cache
    def load_image_lines(self, file_path: str) -> list[Text]:
        """Load the image from a file and split into lines of Text for rendering."""
        with open(file_path, "r") as f:
            return [Text.from_ansi(line) for line in f.readlines()]

    def update_image(self) -> None:
        """Load the appropriate image given the terminal size (and CLI arguments)."""
        # print("update_image", self.size, self.parent.size, self.screen.size, self.app.size)
        # self.size will not be set until later, based on this method's decision
        # self.parent.size will fail to shrink (in the current layout)
        # self.screen.size will not work in arbitrary layouts and is not updated yet
        # self.app.size will not work in arbitrary layouts
        size = self.app.size

        file_paths = sequel_file_paths if args.sql else original_file_paths

        # Ignore width if --cyclic is passed twice, since
        file_path = file_paths[0]
        if (size.width < 80 and args.cyclic < 2) or size.height < 12:
            file_path = file_paths[1]
        if (size.width < 40 and args.cyclic < 2) or size.height < 6:
            file_path = file_paths[2]

        # NOTE: Make sure not to mutate this object, since it's cached,
        # and as such, the mutations would be persisted!
        self.image_text_lines = self.load_image_lines(file_path)

        if args.cyclic:
            border = Text.from_markup("▌▐", style=Style(bgcolor=colors["paper"].rich_color, color=colors["pen"].rich_color))
            self.image_text_lines = [line + border for line in self.image_text_lines]

        self.image_width = self.image_text_lines[0].__rich_measure__(None, None).maximum  # type: ignore
        self.image_height = len(self.image_text_lines)

        if args.cyclic > 1:
            # repeat horizontally to fill the screen
            new_text_lines = []
            for original_line in self.image_text_lines:
                line = original_line
                # `image_width` must be calculated after the border is added, and before its used here
                reps_needed = math.ceil(size.width / self.image_width)
                for _ in range(reps_needed):
                    line += original_line
                new_text_lines.append(line)
            self.image_text_lines = new_text_lines

        if args.cyclic > 2:
            # repeat vertically to fill the screen
            reps_needed = math.ceil(size.height / self.image_height)
            self.image_text_lines *= reps_needed
            # prevent scrollbar
            self.image_text_lines = self.image_text_lines[:size.height]

        # These need to be re-calculated, so the widget can expand if needed
        self.image_width = self.image_text_lines[0].__rich_measure__(None, None).maximum  # type: ignore
        self.image_height = len(self.image_text_lines)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return self.image_width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return self.image_height

class SmokeTest(Widget):
    """A widget that renders a smoke effect."""

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
    """The Textual application."""

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
        """Called when the app is mounted."""
        if args.sql:
            self.add_class("sequel")

    def on_resize(self, event: events.Resize) -> None:
        """Called when the widget is resized."""
        if not args.smoke_test:
            self.query_one(PipeStrip).update_image()

    def compose(self) -> ComposeResult:
        """Compose the layout."""
        if args.smoke_test:
            yield SmokeTest()
        else:
            yield PipeStrip()

app = PipeStripApp()

# Must be called before app.run() which blocks until the app exits.
# Takes the app in order to do some clean up of the app before restarting.
if args.dev:
    from .auto_restart import restart_on_changes
    restart_on_changes(app)

def main():
    app.run()

if __name__ == "__main__":
    main()
