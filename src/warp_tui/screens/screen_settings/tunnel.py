from textual.screen import ModalScreen
from textual.widgets import OptionList, Footer, Static, Button
from textual.containers import Container, Vertical, VerticalScroll
from textual.binding import Binding
from textual.app import ComposeResult

from ...utils import WarpCLI

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
