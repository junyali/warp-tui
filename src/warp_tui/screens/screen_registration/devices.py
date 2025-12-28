from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Vertical
from textual.binding import Binding
from textual.app import ComposeResult

from ...utils import WarpCLI

class DevicesRegistration(ModalScreen):
    CSS = """
    DevicesRegistration {
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
        devices, success = WarpCLI.get_devices()

        with Vertical(id="info-dialogue"):
            yield Static("Registration Devices", id="info-title")
            if success:
                yield Static(devices, id="info-content")
            else:
                yield Static(f"{devices}", id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()
