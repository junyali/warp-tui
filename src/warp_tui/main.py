import shutil
import asyncio
import webbrowser
from textual.app import App, ComposeResult
from textual.widgets import OptionList, Footer, Static
from textual.containers import Container
from textual.binding import Binding
from textual.theme import Theme

from .__version__ import __version__
from .utils import polling_rate, State, WarpCLI
from .screens import Settings, Registration

class WarpApp(App):
    CSS = """
    Screen {
        align: center middle;
        margin: 2 8;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        color: orange;
    }
    
    Container {
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }
    
    #menu-options {
        height: auto;
    }
    
    #status-display {
        border: solid gray;
        padding: 1;
        margin: 2 8;
    }
    
    .status-connected {
        color: $success;
    }
    
    .status-connecting {
        color: $warning;
    }
    
    .status-disconnected {
        color: $error;
    }
    
    #version-display {
        text-align: center;
        color: gray;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit")
    ]

    def __init__(self):
        super().__init__()
        self.current_status = State.UNKNOWN.value
        self.status_reason = ""
        self.is_closed = False

        self.register_theme(Theme(
            name="warp_tui",
            primary = "#f48120",
            secondary = "#faad3f",
            accent = "#ffa62b",
            warning = "#ffa62b",
            error = "#ba3c5b",
            success = "#4ebf71",
            foreground = "#e0e0e0",
        ))
        self.theme = "warp_tui"

    def compose(self) -> ComposeResult:
        yield Static("Warp-TUI", id="title")
        with Container(id="menu-container"):
            yield OptionList(
                "Connect",
                "Disconnect",
                "Settings",
                "Registration",
                "Exit",
                id="menu-options"
            )
        yield Static("Status: Initialising", id="status-display")
        yield Static(
            f"v{__version__} | [@click=app.open_github]https://github.com/junyali/warp-tui[/]",
            id="version-display"
        )
        yield Footer()

    def on_mount(self) -> None:
        if not shutil.which("warp-cli"):
            self.exit(message="Error: warp-cli is not installed\nFor more information, visit https://developers.cloudflare.com/warp-client/get-started/linux/")
            return
        self.call_after_refresh(self.refresh_status_display)
        self.poll_status()

    def on_unmount(self) -> None:
        self.is_closed = True

    def poll_status(self) -> None:
        self.run_worker(self._status_worker, exclusive=True)

    async def _status_worker(self) -> None:
        while not self.is_closed:
            status, reason = WarpCLI.get_status()

            if status:
                self.current_status = status
                self.status_reason = reason or ""
                self.update_menu_options()
                self.refresh_status_display()

            await asyncio.sleep(polling_rate)

    def refresh_status_display(self) -> None:
        try:
            status_widget = self.query_one("#status-display", Static)
        except:
            return

        if self.status_reason:
            status_text = f"Status: {self.current_status} \n{self.status_reason}"
        else:
            status_text = f"Status: {self.current_status}"

        status_widget.remove_class("status-connected", "status-connecting", "status-disconnected")

        if self.current_status == "Connected":
            status_widget.add_class("status-connected")
        elif self.current_status == "Connecting":
            status_widget.add_class("status-connecting")
        elif self.current_status == "Disconnected":
            status_widget.add_class("status-disconnected")

        status_widget.update(status_text)

    def update_menu_options(self) -> None:
        try:
            option_list = self.query_one("#menu-options", OptionList)
        except:
            return

        if self.current_status in ["Connected", "Connecting"]:
            new_options = ["Disconnect", "Settings", "Registration", "Exit"]
        else:
            new_options = ["Connect", "Settings", "Registration", "Exit"]

        current_options = [str(option.prompt) for option in option_list.options]

        if current_options!= new_options:
            current_index = option_list.highlighted
            option_list.clear_options()
            for option in new_options:
                option_list.add_option(option)

            if current_index is not None:
                max_index = len(new_options) - 1
                restored_index = min(current_index, max_index)
                option_list.highlighted = restored_index

    def action_open_github(self) -> None:
        webbrowser.open("https://github.com/junyali/warp-tui")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt)

        if option == "Exit":
            self.exit()
        elif option == "Connect":
            self.run_worker(self._connect_worker)
        elif option == "Disconnect":
            self.run_worker(self._disconnect_worker)
        elif option == "Settings":
            self.push_screen(Settings())
        elif option == "Registration":
            self.push_screen(Registration())

    async def _connect_worker(self) -> None:
        result = WarpCLI.connect()
        if result != 0:
            self.current_status = "Connection failed"
            self.status_reason = "Failed to connect"
            self.refresh_status_display()

    async def _disconnect_worker(self) -> None:
        result = WarpCLI.disconnect()
        if result != 0:
            self.current_status = f"Disconnect failed"
            self.status_reason = "Failed to disconnect"
            self.refresh_status_display()

def main():
    app = WarpApp()
    app.run()

if __name__ == "__main__":
    main()
