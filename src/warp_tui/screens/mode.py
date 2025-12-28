import asyncio
import subprocess
from textual.screen import ModalScreen
from textual.widgets import OptionList, Footer, Static
from textual.containers import Container
from textual.binding import Binding
from textual.app import ComposeResult

from ..utils import polling_rate

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
            await asyncio.sleep(polling_rate)
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
            option_list = self.query_one("#mode-options", OptionList)
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
