import shutil
import subprocess
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import OptionList, Footer
from textual.containers import Container
from textual.binding import Binding

class WarpApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    
    Container {
        width: 60;
        height: auto;
        border: solid orange;
        padding: 1;
    }
    
    OptionList {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit")
    ]

    def __init__(self):
        super().__init__()
        self.current_status = "Unknown"

    def compose(self) -> ComposeResult:
        with Container(id="menu-container"):
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

                for line in result.stdout.splitlines():
                    if line.startswith("Status update:"):
                        status = line.split("Status update:")[1].strip()
                        self.current_status = status
                        self.refresh_status_display()
                        break
                else:
                    self.current_status = "Unknown"
                    self.refresh_status_display()
            except subprocess.TimeoutExpired:
                self.current_status = "Timeout"
                self.refresh_status_display()
            except Exception as e:
                self.current_status = f"Error: {e}"
                self.refresh_status_display()

            await asyncio.sleep(0.5)

    def refresh_status_display(self) -> None:
        footer = self.query_one(Footer)
        self.sub_title = f"Status: {self.current_status}"

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = event.option.prompt

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
