from textual.screen import ModalScreen
from textual.widgets import OptionList, Footer, Static
from textual.containers import Container
from textual.binding import Binding
from textual.app import ComposeResult

class TunnelSettings(ModalScreen):
    CSS = """
        TunnelSettings {
            align: center middle;
        }

        #tunnel-dialogue {
            height: auto;
            border: solid orange;
            padding: 1;
        }

        #tunnel-title {
            text-align: center;
            text-style: bold;
            color: orange;
        }

        #tunnel-options {
            height: auto;
        }
        """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def compose(self) -> ComposeResult:
        with Container(id="tunnel-dialogue"):
            yield Static("Tunnel Settings", id="tunnel-title")
            yield OptionList(
                "Dump",
                "Stats",
                "IP",
                "Host",
                "Endpoint",
                "Protocol",
                "Masque Options",
                "Rotate Keys",
                None,
                "Back",
                id="tunnels-options"
            )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()

        if option == "Back":
            self.app.pop_screen()
            return
