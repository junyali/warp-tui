import shutil
import subprocess
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import OptionList, Footer, Static
from textual.containers import Container
from textual.binding import Binding

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
    
    OptionList {
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
    """

    BINDINGS = [
        Binding("q", "quit", "Quit")
    ]

    def __init__(self):
        super().__init__()
        self.current_status = "Unknown"

    def compose(self) -> ComposeResult:
        yield Static("Warp-TUI", id="title")
        with Container(id="menu-container"):
            yield OptionList(
                "Connect",
                "Disconnect",
                "Settings",
                "Exit"
            )
        yield Static("Status: Initialising", id="status-display")
        yield Footer()

    def on_mount(self) -> None:
        if not shutil.which("warp-cli"):
            self.exit(message="Error: warp-cli is not installed")
            return
        self.call_after_refresh(self.refresh_status_display)
        self.poll_status()

    def poll_status(self) -> None:
        self.run_worker(self._status_worker, exclusive=True)

    async def _status_worker(self) -> None:
        while True:
            try:
                result = subprocess.run(
                    ["warp-cli", "status"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                status = None
                reason = None

                for line in result.stdout.splitlines():
                    if line.startswith("Status update:"):
                        status = line.split("Status update:")[1].strip()
                    elif line.startswith("Reason:"):
                        reason = line.split("Reason:")[1].strip()
                if status:
                    self.current_status = status
                    self.status_reason = reason or ""
                    self.update_menu_options()
                    self.refresh_status_display()
                else:
                    self.current_status = "Unknown"
                    self.status_reason = ""
                    self.refresh_status_display()
            except subprocess.TimeoutExpired:
                self.current_status = "Timeout"
                self.refresh_status_display()
            except Exception as e:
                self.current_status = f"Error: {e}"
                self.refresh_status_display()

            await asyncio.sleep(0.5)

    def refresh_status_display(self) -> None:
        status_widget = self.query_one("#status-display", Static)

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
        option_list = self.query_one(OptionList)

        if self.current_status in ["Connected", "Connecting"]:
            new_options = ["Disconnect", "Settings", "Exit"]
        else:
            new_options = ["Connect", "Settings", "Exit"]

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

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt)

        if option == "Exit":
            self.exit()
        elif option == "Connect":
            self.run_worker(self._connect_worker)
        elif option == "Disconnect":
            self.run_worker(self._disconnect_worker)

    async def _connect_worker(self) -> None:
        try:
            subprocess.run(
                ["warp-cli", "connect"],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            self.current_status = f"Connection failed: {e}"
            self.refresh_status_display()

    async def _disconnect_worker(self) -> None:
        try:
            subprocess.run(
                ["warp-cli", "disconnect"],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            self.current_status = f"Disconnect failed: {e}"
            self.refresh_status_display()

if __name__ == "__main__":
    app = WarpApp()
    app.run()
