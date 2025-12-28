from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import OptionList, Footer, Static
from textual.containers import Container
from textual.binding import Binding

from .screen_settings import ModeSettings, ProxySettings

class Settings(Screen):
    CSS = """
    Settings {
        align: center middle;
    }

    #settings-title {
        text-align: center;
        text-style: bold;
        color: orange;
    }

    #settings-container {
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }

    #settings-options {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Static("Settings", id="settings-title")
        with Container(id="settings-container"):
            yield OptionList(
                "Mode",
                "Proxy",
                None,
                "Back",
                id="settings-options"
            )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt)

        if option == "Back":
            self.app.pop_screen()
        elif option == "Mode":
            self.app.push_screen(ModeSettings())
        elif option == "Proxy":
            self.app.push_screen(ProxySettings())
