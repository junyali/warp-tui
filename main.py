import shutil
from textual.app import App, ComposeResult
from textual.widgets import OptionList, Footer
from textual.binding import Binding

class WarpApp(App):
    BINDINGS = [
        Binding("q", "quit", "Quit")
    ]

    def __init__(self):
        super().__init__()
        self.current_status = "Unknown"

    def compose(self) -> ComposeResult:
        yield OptionList(
            "Connect",
            "Disconnect",
            "Settings",
            "Exit"
        )
        yield Footer()

    def on_mount(self) -> None:
        if not shutil.which("warp-cli"):
            self.exit(message="Error: warp-cli is not installed")
            return

    def refresh_status_display(self) -> None:
        footer = self.query_one(Footer)
        self.sub_title = f"Status: {self.current_status}"

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = event.option.prompt

        if option == "Exit":
            self.exit()

if __name__ == "__main__":
    app = WarpApp()
    app.run()
