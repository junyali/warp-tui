from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import OptionList, Footer, Static
from textual.containers import Container
from textual.binding import Binding

from .screen_registration import ShowRegistration, NewRegistration, DeleteRegistration

class Registration(Screen):
    CSS = """
    Registration {
        align: center middle;
    }

    #registration-title {
        text-align: center;
        text-style: bold;
        color: orange;
    }

    #registration-container {
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }

    #registration-options {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Static("Registration", id="registration-title")
        with Container(id="registration-container"):
            yield OptionList(
                "Show",
                "New",
                "Devices",
                "Delete",
                None,
                "Back",
                id="registration-options"
            )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt)

        if option == "Back":
            self.app.pop_screen()
        elif option == "Show":
            self.app.push_screen(ShowRegistration())
        elif option == "New":
            self.app.push_screen(NewRegistration())
        elif option == "Devices":
            pass
        elif option == "Delete":
            self.app.push_screen(DeleteRegistration())
