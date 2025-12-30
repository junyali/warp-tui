from textual.screen import ModalScreen
from textual.widgets import OptionList, Footer, Static, Button, Input
from textual.containers import Container, Vertical, VerticalScroll
from textual.binding import Binding
from textual.app import ComposeResult

from ...utils import WarpCLI

class EndpointInput(ModalScreen):
    CSS = """
        EndpointInput {
            align: center middle;
        }

        #endpoint-dialogue {
            height: auto;
            border: solid orange;
            padding: 1;
            margin: 2 8;
        }

        #endpoint-input-title {
            text-align: center;
            text-style: bold;
            color: orange;
            margin-bottom: 1;
        }

        Input {
            margin-bottom: 1;
        }
        """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="endpoint-dialogue"):
            yield Static("Enter Socket Address", id="endpoint-input-title")
            yield Input(placeholder="IP:PORT", id="endpoint-input")
            yield Static("Press Enter to confirm, Escape to cancel")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        sockaddr = event.value.strip()

        if sockaddr:
            success, error_msg = WarpCLI.set_endpoint(sockaddr)
            self.dismiss((success, error_msg))
        else:
            self.dismiss((False, "Endpoint cannot be empty"))

class ResetEndpoint(ModalScreen):
    CSS = """
        ResetEndpoint {
            align: center middle;
        }

        #info-dialogue {
            width: 80%;
            height: auto;
            border: solid orange;
            padding: 1;
            margin: 2 8;
        }

        #info-title {
            text-align: center;
            text-style: bold;
            color: orange;
            margin-bottom: 1;
        }

        #info-content {
            height: auto;
            padding: 1;
            margin-bottom: 1;
        }

        #info-scroll {
            height: auto;
            max-height: 60vh;
        }

        #info-button {
            width: 100%;
            margin-top: 1;
        }
        """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("enter", "dismiss", "Close")
    ]

    def compose(self) -> ComposeResult:
        success, error_msg = WarpCLI.reset_endpoint()

        with Vertical(id="info-dialogue"):
            yield Static("Reset Endpoint", id="info-title")
            with VerticalScroll(id="info-scroll"):
                if success:
                    yield Static("Success!", id="info-content")
                else:
                    yield Static(f"{error_msg}", id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class EndpointTunnel(ModalScreen):
    CSS = """
            EndpointTunnel {
                align: center middle;
            }

            #endpoint-dialogue {
                height: auto;
                border: solid orange;
                padding: 1;
                margin: 2 8;
            }

            #endpoint-title {
                text-align: center;
                text-style: bold;
                color: orange;
                margin-bottom: 1;
            }

            #endpoint-options {
                height: auto;
            }
            """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def __init__(self):
        super().__init__()
        self.endpoints = []

    def compose(self) -> ComposeResult:
        with Container(id="endpoint-dialogue"):
            yield Static("Endpoint Settings", id="endpoint-title")
            yield OptionList(id="endpoint-options")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_endpoint_settings()
        option_list = self.query_one("#endpoint-options", OptionList)
        option_list.highlighted = 0

    def refresh_endpoint_settings(self) -> None:
        try:
            option_list = self.query_one("#endpoint-options", OptionList)
            option_list.clear_options()

            stats, success = WarpCLI.get_stats()
            endpoints_display = "Not connected"

            if success:
                for line in stats.splitlines():
                    if line.startswith("Endpoints: "):
                        endpoints_str = line.split("Endpoints:")[1].strip()
                        self.current_endpoints = [ep.strip() for ep in endpoints_str.split(", ")]
                        endpoints_display = ", ".join(self.current_endpoints)
                        break

            option_list.add_option(f"Set (current: {endpoints_display})")
            option_list.add_option("Reset")
            option_list.add_option(None)
            option_list.add_option("Back")
        except Exception as e:
            option_list = self.query_one("#endpoint-options", OptionList)
            option_list.clear_options()
            option_list.add_option("Set")
            option_list.add_option("Reset")
            option_list.add_option(None)
            option_list.add_option("Back")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()

        if option == "Back":
            self.app.pop_screen()
        elif option.startswith("Set"):
            self.app.push_screen(EndpointInput(), callback=self._on_endpoint_input_closed)
        elif option == "Reset":
            self.app.push_screen(ResetEndpoint())
            self.refresh_endpoint_settings()

    def _on_endpoint_input_closed(self, result=None) -> None:
        self.refresh_endpoint_settings()

class DumpTunnel(ModalScreen):
    CSS = """
    DumpTunnel {
        align: center middle;
    }

    #info-dialogue {
        width: 80%;
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }

    #info-title {
        text-align: center;
        text-style: bold;
        color: orange;
        margin-bottom: 1;
    }

    #info-content {
        height: auto;
        padding: 1;
        margin-bottom: 1;
    }
    
    #info-scroll {
        height: auto;
        max-height: 60vh;
    }

    #info-button {
        width: 100%;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("enter", "dismiss", "Close")
    ]

    def compose(self) -> ComposeResult:
        dump, success = WarpCLI.dump_tunnel()

        with Vertical(id="info-dialogue"):
            yield Static("Split Tunnel Routing Dump", id="info-title")
            with VerticalScroll(id="info-scroll"):
                if success:
                    yield Static(dump, id="info-content")
                else:
                    yield Static(f"{dump}", id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class StatsTunnel(ModalScreen):
    CSS = """
    StatsTunnel {
        align: center middle;
    }

    #info-dialogue {
        width: 80%;
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }

    #info-title {
        text-align: center;
        text-style: bold;
        color: orange;
        margin-bottom: 1;
    }

    #info-content {
        height: auto;
        padding: 1;
        margin-bottom: 1;
    }

    #info-scroll {
        height: auto;
        max-height: 60vh;
    }

    #info-button {
        width: 100%;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("enter", "dismiss", "Close")
    ]

    def compose(self) -> ComposeResult:
        stats, success = WarpCLI.get_stats()

        with Vertical(id="info-dialogue"):
            yield Static("Current Tunnel Connection Stats", id="info-title")
            with VerticalScroll(id="info-scroll"):
                if success:
                    yield Static(stats, id="info-content")
                else:
                    yield Static(f"{stats}", id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class RotateKeysTunnel(ModalScreen):
    CSS = """
    RotateKeysTunnel {
        align: center middle;
    }

    #info-dialogue {
        width: 60%;
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }

    #info-title {
        text-align: center;
        text-style: bold;
        color: orange;
        margin-bottom: 1;
    }

    #info-content {
        height: auto;
        padding: 1;
        margin-bottom: 1;
    }

    #info-button {
        width: 100%;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("enter", "dismiss", "Close")
    ]

    def compose(self) -> ComposeResult:
        success, error_msg = WarpCLI.rotate_keys()

        with Vertical(id="info-dialogue"):
            yield Static("Generate New Key-Pair", id="info-title")
            if success:
                yield Static("Success!", id="info-content")
            else:
                yield Static(error_msg, id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class TunnelSettings(ModalScreen):
    CSS = """
        TunnelSettings {
            align: center middle;
        }

        #tunnel-dialogue {
            height: auto;
            border: solid orange;
            padding: 1;
            margin: 2 8;
        }

        #tunnel-title {
            text-align: center;
            text-style: bold;
            color: orange;
            margin-bottom: 1;
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
        elif option == "Dump":
            self.app.push_screen(DumpTunnel())
        elif option == "Stats":
            self.app.push_screen(StatsTunnel())
        elif option == "Rotate Keys":
            self.app.push_screen(RotateKeysTunnel())
        elif option == "Endpoint":
            self.app.push_screen(EndpointTunnel())
