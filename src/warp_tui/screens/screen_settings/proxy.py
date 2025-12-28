from textual.screen import ModalScreen
from textual.widgets import OptionList, Footer, Static, Input
from textual.containers import Container
from textual.binding import Binding
from textual.app import ComposeResult

from ...utils import WarpCLI

class PortInput(ModalScreen):
    CSS = """
        PortInput {
            align: center middle;
        }

        #port-dialogue {
            height: auto;
            border: solid orange;
            padding: 2;
        }

        #port-input-title {
            text-align: center;
            text-style: bold;
            color: orange;
        }

        Input {
            margin-bottom: 1;
        }
        """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="port-dialogue"):
            yield Static("Enter Proxy Port", id="port-input-title")
            yield Input(placeholder="Port Number", id="port-input")
            yield Static("Press Enter to confirm, Escape to cancel")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        port = event.value.strip()

        if port.isdigit() and 1 <= int(port) <= 65535:
            result = WarpCLI.set_proxy_port(str(port))
            self.dismiss(result)
        else:
            pass

class ProxySettings(ModalScreen):
    CSS = """
        ProxySettings {
            align: center middle;
        }

        #proxy-dialogue {
            height: auto;
            border: solid orange;
            padding: 1;
        }

        #proxy-title {
            text-align: center;
            text-style: bold;
            color: orange;
        }

        #proxy-options {
            height: auto;
        }
        """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def __init__(self):
        super().__init__()
        self.current_port = ""

    def compose(self) -> ComposeResult:
        with Container(id="proxy-dialogue"):
            yield Static("Proxy Settings", id="proxy-title")
            yield OptionList(
                "Port",
                None,
                "Back",
                id="proxy-options"
            )
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_proxy_settings()

    def refresh_proxy_settings(self) -> None:
        self.current_port = WarpCLI.get_proxy_port() or ""

        try:
            option_list = self.query_one("#proxy-options", OptionList)
            option_list.clear_options()

            if self.current_port:
                option_list.add_option(f"Port (current: {self.current_port})")
            else:
                option_list.add_option("Port")

            option_list.add_option(None)
            option_list.add_option("Back")
        except Exception as e:
            option_list = self.query_one("#proxy-options", OptionList)
            option_list.clear_options()
            option_list.add_option("Port")
            option_list.add_option(None)
            option_list.add_option("Back")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()

        if option == "Back":
            self.app.pop_screen()
            return
        elif option.startswith("Port"):
            self.app.push_screen(PortInput(), callback=self._on_port_input_closed)

    def _on_port_input_closed(self, result=None) -> None:
        self.refresh_proxy_settings()
