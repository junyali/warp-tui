from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from textual.app import ComposeResult

from ...utils import WarpCLI

class DeleteConfirmation(ModalScreen):
    CSS = """
    DeleteConfirmation {
        align: center middle;
    }
    
    #confirm-dialogue {
        width: 60%;
        height: auto;
        border: solid red;
        padding: 1;
        margin: 2 8;
    }

    #confirm-title {
        text-align: center;
        text-style: bold;
        color: red;
        margin-bottom: 1;
    }

    #confirm-content {
        height: auto;
        padding: 1;
        margin-bottom: 1;
    }
    
    #button-container {
        align: center middle;
        height: auto;
    }
    
    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("left", "focus_no", "Previous", show=False),
        Binding("right", "focus_yes", "Next", show=False),
        Binding("n", "cancel", "No"),
        Binding("y", "confirm", "Yes"),
        Binding("enter", "select", "Select")
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialogue"):
            yield Static("Delete Registration?", id="confirm-title")
            yield Static(
                "Are you sure you want to delete this registration?\nThis cannot be undone.",
                id="confirm-content"
            )
            with Horizontal(id="button-container"):
                yield Button("No", variant="primary", id="no-button")
                yield Button("Yes", variant="error", id="yes-button")

    def on_mount(self) -> None:
        self.query_one("#no-button", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes-button":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def action_focus_yes(self) -> None:
        self.query_one("#yes-button", Button).focus()

    def action_focus_no(self) -> None:
        self.query_one("#no-button", Button).focus()

class DeleteResult(ModalScreen):
    CSS = """
    DeleteResult {
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

    def __init__(self, success: bool, message: str):
        super().__init__()
        self.success = success
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="info-dialogue"):
            yield Static("Registration Deletion", id="info-title")
            yield Static(self.message, id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class DeleteRegistration(ModalScreen):
    CSS = """
    DeleteRegistration {
        align: center middle;
    }
    """

    def on_mount(self) -> None:
        if not WarpCLI.check_registration():
            self.app.push_screen(
                DeleteResult(False, "Not registered."),
                callback=lambda _: self.dismiss()
            )
        else:
            self.app.push_screen(
                DeleteConfirmation(),
                callback=self._handle_confirmation
            )

    def _handle_confirmation(self, confirmed: bool) -> None:
        if not confirmed:
            self.dismiss()
            return

        success, error_msg = WarpCLI.delete_registration()

        if success:
            self.app.push_screen(
                DeleteResult(True, "Registration deleted."),
                callback=lambda _: self.dismiss()
            )
        else:
            self.app.push_screen(
                DeleteResult(False, f"{error_msg}"),
                callback=lambda _: self.dismiss()
            )

    def compose(self) -> ComposeResult:
        return []
