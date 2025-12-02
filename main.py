import shutil
import subprocess
import asyncio
from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import OptionList, Footer, Static
from textual.containers import Container
from textual.binding import Binding

class ModeSettings(ModalScreen):
    CSS = """
    ModeSettings {
        align: center middle;
    }
    
    #mode-dialogue {
        height: auto;
        border: solid orange;
        padding: 1;
    }
    
    #mode-title {
        text-align: center;
        text-style: bold;
        color: orange;
    }
    
    #mode-options {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "quit", "Quit")
    ]

    MODE_MAP = {
        "Warp": "warp",
        "DnsOverHttps": "doh",
        "WarpWithDnsOverHttps": "warp+doh",
        "DnsOverTls": "dot",
        "WarpWithDnsOverTls": "warp+dot",
        "WarpProxy": "proxy",
        "TunnelOnly": "tunnel_only",
    }

    def __init__(self):
        super().__init__()
        self.current_mode = None

    def compose(self) -> ComposeResult:
        with Container(id="mode-dialogue"):
            yield Static("Mode Settings", id="mode-title")
            yield OptionList(id="mode-options")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_mode_list()
        self.poll_mode()

    def poll_mode(self) -> None:
        self.run_worker(self._mode_poll_worker, exclusive=True)

    async def _mode_poll_worker(self) -> None:
        while True:
            await asyncio.sleep(1)
            self.refresh_mode_list()

    def refresh_mode_list(self) -> None:
        try:
            result = subprocess.run(
                ["warp-cli", "settings", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.splitlines():
                if "Mode:" in line:
                    mode_text = line.split("Mode:")[1].strip()

                    if mode_text.startswith("WarpProxy"):
                        self.current_mode = self.MODE_MAP.get("WarpProxy")
                    else:
                        self.current_mode = self.MODE_MAP.get(mode_text)
                    break

            option_list = self.query_one("#mode-options", OptionList)
            current_options = [str(opt.prompt) for opt in option_list.options]
            new_options = []

            for _, mode in self.MODE_MAP.items():
                if mode == self.current_mode:
                    new_options.append(f"* {mode}")
                else:
                    new_options.append(f"  {mode}")

            new_options.append(None)
            new_options.append("Back")

            if current_options != new_options:
                current_index = option_list.highlighted
                option_list.clear_options()
                for option in new_options:
                    option_list.add_option(option)

                if current_index is not None:
                    max_index = len(new_options) - 1
                    restored_index = min(current_index, max_index)
                    option_list.highlighted = restored_index

        except Exception as e:
            option_list = self.query_one("mode-options", OptionList)
            if len(option_list.options) == 0:
                option_list.clear_options()
                for _, mode in self.MODE_MAP.items():
                    option_list.add_option(f"  {mode}")
                option_list.add_option(None)
                option_list.add_option("Back")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()

        if option == "Back":
            self.app.pop_screen()
            return

        option_clean = option.lstrip("* ")

        selected_mode = None
        for _, mode in self.MODE_MAP.items():
            if option_clean == mode:
                selected_mode = mode
                break

        if selected_mode:
            self.run_worker(self._change_mode_worker(selected_mode))

    async def _change_mode_worker(self, mode: str) -> None:
        try:
            subprocess.run(
                ["warp-cli", "mode", mode],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            pass


class Settings(Screen):
    CSS = """
    Settings {
        align: center middle;
    }
    
    #settings-title {
        text-align: center;
        text-style: bold;
        color: orange;
    }
    
    #settings-container {
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }
    
    #settings-options {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Static("Settings", id="settings-title")
        with Container(id="settings-container"):
            yield OptionList(
                "Mode",
                "Back",
                id="settings-options"
            )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt)

        if option == "Back":
            self.app.pop_screen()
        elif option == "Mode":
            self.app.push_screen(ModeSettings())

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
    """

    BINDINGS = [
        Binding("q", "quit", "Quit")
    ]

    def __init__(self):
        super().__init__()
        self.current_status = "Unknown"
        self.status_reason = ""

    def compose(self) -> ComposeResult:
        yield Static("Warp-TUI", id="title")
        with Container(id="menu-container"):
            yield OptionList(
                "Connect",
                "Disconnect",
                "Settings",
                "Exit",
                id="menu-options"
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
        elif option == "Settings":
            self.push_screen(Settings())

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
