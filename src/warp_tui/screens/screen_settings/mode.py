import asyncio
from textual.screen import ModalScreen
from textual.widgets import OptionList, Footer, Static
from textual.containers import Container
from textual.binding import Binding
from textual.app import ComposeResult

from ...utils import polling_rate, WarpCLI

class ModeSettings(ModalScreen):
    CSS = """
    ModeSettings {
        align: center middle;
    }

    #mode-dialogue {
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }

    #mode-title {
        text-align: center;
        text-style: bold;
        color: orange;
        margin-bottom: 1;
    }

    #mode-options {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
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

    MODES = [
        "warp",
        "doh",
        "warp+doh",
        "dot", "dot",
        "warp+dot",
        "proxy",
        "tunnel_only",
    ]

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
        while self.is_mounted:
            await asyncio.sleep(polling_rate)
            if self.is_mounted:
                self.refresh_mode_list()

    def refresh_mode_list(self) -> None:
        self.current_mode = WarpCLI.get_mode()

        try:
            option_list = self.query_one("#mode-options", OptionList)
            current_options = [str(opt.prompt) for opt in option_list.options]
            new_options = []

            for mode in self.MODES:
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
                for mode in self.MODES:
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
        for mode in self.MODES:
            if option_clean == mode:
                selected_mode = mode
                break

        if selected_mode:
            self.run_worker(self._change_mode_worker(selected_mode))

    async def _change_mode_worker(self, mode: str) -> None:
        result = WarpCLI.set_mode(mode)
        if result != 0:
            await asyncio.sleep(0.5)
            self.refresh_mode_list()
