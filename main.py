from textual.app import App, ComposeResult
from textual.widgets import OptionList
from textual.binding import Binding

class WarpApp(App):
    BINDINGS = [
        Binding("q", "quit", "Quit")
    ]
    def compose(self) -> ComposeResult:
        yield OptionList(
            "Connect",
            "Disconnect",
            "Settings",
            "Exit"
        )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = event.option.prompt

        if option == "Exit":
            self.exit()

if __name__ == "__main__":
    app = WarpApp()
    app.run()
