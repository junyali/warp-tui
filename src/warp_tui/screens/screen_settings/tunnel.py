from textual.screen import ModalScreen
from textual.widgets import OptionList, Footer, Static, Button, Input
from textual.containers import Container, Vertical, VerticalScroll
from textual.binding import Binding
from textual.app import ComposeResult

from ...utils import WarpCLI

class HostInput(ModalScreen):
    CSS = """
    HostInput {
        align: center middle;
    }
    
    #host-dialogue {
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }

    #host-input-title {
        text-align: center;
        text-style: bold;
        color: orange;
        margin-bottom: 1;
    }

    Input {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel")
    ]

    def compose(self) -> ComposeResult:
        with Container(id="host-dialogue"):
            yield Static("Enter Hostname", id="host-input-title")
            yield Input(placeholder="example.com", id="host-input")
            yield Static("Press Enter to confirm, Escape to cancel")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        host = event.value.strip()
        if host:
            success, error_msg = WarpCLI.add_tunnel_host(host)
            self.dismiss((success, error_msg))
        else:
            self.dismiss((False, "Host cannot be empty"))

class ConfirmReset(ModalScreen):
    CSS = """
    ConfirmReset {
        align: center middle;
    }
    
    #confirm-dialogue {
        width: 60%;
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }
    
    #confirm-title {
        text-align: center;
        text-style: bold;
        color: orange;
        margin-bottom: 1;
    }
    
    #confirm-content {
        text-align: center;
        padding: 1;
        margin-bottom: 1;
    }
    
    #confirm-options {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel")
    ]

    def __init__(self, message: str = "Are you sure?"):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(id="confirm-dialogue"):
            yield Static("Reset Confirmation", id="confirm-title")
            yield Static(self.message, id="confirm-content")
            yield OptionList(
                "No",
                "Yes",
                id="confirm-options"
            )

    def on_mount(self) -> None:
        option_list = self.query_one("#confirm-options", OptionList)
        option_list.highlighted = 0

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()
        self.dismiss(option == "Yes")

class HostTunnel(ModalScreen):
    CSS = """
    HostTunnel {
        align: center middle;
    }

    #host-title {
        text-align: center;
        text-style: bold;
        color: orange;
        margin: 1 0;
    }
    
    #host-layout {
        layout: horizontal;
        height: 100%;
        width: 100%;
        border: solid orange;
    }
    
    #host-list-container {
        min-width: 20;
        width: 3fr;
        height: 100%;
        border: solid green;
        padding: 1;
        margin-right: 1;
    }

    #host-list {
        height: 100%;
    }
    
    #host-actions-container {
        min-width: 20;
        width: 1fr;
        height: 30%;
        border: solid blue;
        padding: 1;
    }
    
    #host-actions-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #host-actions {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("tab", "switch_focus", "Switch Focus")
    ]

    def __init__(self):
        super().__init__()
        self.focused_list = "hosts"

    def compose(self) -> ComposeResult:
        yield Static("Host Settings", id="host-title")
        with Container(id="host-layout"):
            with Container(id="host-list-container"):
                yield Static("Excluded Hosts", id="host-list-title")
                yield OptionList(id="host-list")
            with Container(id="host-actions-container"):
                yield Static("Actions", id="host-actions-title")
                yield OptionList(
                    "Add",
                    "Delete",
                    "Reset",
                    None,
                    "Back",
                    id="host-actions"
                    )
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_host_list()
        actions_list = self.query_one("#host-actions", OptionList)
        actions_list.highlighted = 0
        self.update_focus()

    def refresh_host_list(self) -> None:
        try:
            host_list = self.query_one("#host-list", OptionList)
            host_list.clear_options()

            output, success = WarpCLI.list_tunnel_host()
            if success:
                lines = output.splitlines()
                if lines:
                    hosts = [line.split()[0].strip() for line in lines[1:] if line.strip()]
                    if hosts:
                        for host in hosts:
                            host_list.add_option(host)
                    else:
                        host_list.add_option("(No hosts excluded)")
                else:
                    host_list.add_option("(No hosts excluded)")
            else:
                host_list.add_option("(No hosts excluded)")
        except Exception as e:
            host_list = self.query_one("#host-list", OptionList)
            host_list.clear_options()
            host_list.add_option(f"Error: {str(e)}")

    def update_focus(self) -> None:
        host_list = self.query_one("#host-list", OptionList)
        actions_list = self.query_one("#host-actions", OptionList)

        if self.focused_list == "hosts":
            host_list.focus()
            host_list.border_title = "Excluded Hosts"
            actions_list.border_title = None
        else:
            actions_list.focus()
            actions_list.border_title = "Actions"
            host_list.border_title = None

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()
        if event.option_list.id == "host-actions":
            if option == "Back":
                self.app.pop_screen()
            elif option == "Add":
                self.app.push_screen(HostInput(), callback=self._on_host_added)
            elif option == "Delete":
                self._delete_current_host()
            elif option == "Reset":
                self.app.push_screen(
                    ConfirmReset("Reset all excluded hosts?"),
                    callback=self._on_reset_confirmed
                )

    def _delete_current_host(self) -> None:
        host_list = self.query_one("#host-list", OptionList)
        if host_list.highlighted is not None:
            selected_option = host_list.get_option_at_index(host_list.highlighted)
            if selected_option and selected_option.prompt:
                host = str(selected_option.prompt).strip()
                if host and host != "(No hosts excluded)" and not host.startswith("Error:"):
                    success, error_msg = WarpCLI.remove_tunnel_host(host)
                    self.refresh_host_list()

    def _on_host_added(self, result=None) -> None:
        self.refresh_host_list()

    def _on_reset_confirmed(self, confirmed: bool) -> None:
        if confirmed:
            success, error_msg = WarpCLI.reset_tunnel_host()
            self.refresh_host_list()

    def action_switch_focus(self) -> None:
        self.focused_list = "hosts" if self.focused_list == "actions" else "actions"
        self.update_focus()

class MasqueSelect(ModalScreen):
    CSS = """
    MasqueSelect {
        align: center middle;
    }

    #protocol-dialogue {
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }

    #protocol-title {
        text-align: center;
        text-style: bold;
        color: orange;
        margin-bottom: 1;
    }

    #protocol-options {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="protocol-dialogue"):
            yield Static("Select Protocol", id="protocol-input-title")
            yield OptionList(
                "h3-only",
                "h2-only",
                "h3-with-h2-fallback",
                None,
                "Back",
                id="protocol-options"
            )
        yield Footer()

    def on_mount(self) -> None:
        option_list = self.query_one("#protocol-options", OptionList)
        option_list.highlighted = 0

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()

        if option == "Back":
            self.dismiss()
        elif option in ["h3-only", "h2-only", "h3-with-h2-fallback"]:
            success, error_msg = WarpCLI.set_masque(option)
            self.dismiss((success, error_msg))


class ResetMasque(ModalScreen):
    CSS = """
        ResetMasque {
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

        #info-scroll {
            height: auto;
            max-height: 60vh;
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
        success, error_msg = WarpCLI.reset_masque()

        with Vertical(id="info-dialogue"):
            yield Static("Reset MASQUE", id="info-title")
            with VerticalScroll(id="info-scroll"):
                if success:
                    yield Static("Success!", id="info-content")
                else:
                    yield Static(f"{error_msg}", id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()


class MasqueTunnel(ModalScreen):
    CSS = """
    MasqueTunnel {
        align: center middle;
    }

    #masque-dialogue {
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }

    #masque-title {
        text-align: center;
        text-style: bold;
        color: orange;
        margin-bottom: 1;
    }

    #masque-options {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def __init__(self):
        super().__init__()
        self.current_masque = None

    def compose(self) -> ComposeResult:
        with Container(id="masque-dialogue"):
            yield Static("MASQUE Settings", id="masque-title")
            yield OptionList(id="masque-options")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_masque_settings()
        option_list = self.query_one("#masque-options", OptionList)
        option_list.highlighted = 0

    def refresh_masque_settings(self) -> None:
        try:
            option_list = self.query_one("#masque-options", OptionList)
            option_list.clear_options()

            stats, success = WarpCLI.get_stats()
            masque_display = "Not connected"

            if success:
                for line in stats.splitlines():
                    if line.startswith("Tunnel Protocol: "):
                        protocol_info = line.split("Tunnel Protocol:")[1].strip()
                        if "MASQUE" in protocol_info:
                            if "(" in protocol_info and ")" in protocol_info:
                                masque_option = protocol_info.split("(")[1].split(")")[0].strip()
                                masque_display = masque_option
                            else:
                                masque_display = "default"
                        else:
                            masque_display = "N/A"
                        break

            option_list.add_option(f"Set (current: {masque_display})")
            option_list.add_option("Reset")
            option_list.add_option(None)
            option_list.add_option("Back")
        except Exception as e:
            option_list = self.query_one("#masque-options", OptionList)
            option_list.clear_options()
            option_list.add_option("Set")
            option_list.add_option("Reset")
            option_list.add_option(None)
            option_list.add_option("Back")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()

        if option == "Back":
            self.app.pop_screen()
        elif option.startswith("Set"):
            self.app.push_screen(MasqueSelect(), callback=self._on_masque_select_closed)
        elif option == "Reset":
            self.app.push_screen(ResetMasque())
            self.refresh_masque_settings()

    def _on_masque_select_closed(self, result=None) -> None:
        self.refresh_masque_settings()

class ProtocolSelect(ModalScreen):
    CSS = """
    ProtocolSelect {
        align: center middle;
    }

    #protocol-dialogue {
        height: auto;
        border: solid orange;
        padding: 1;
        margin: 2 8;
    }
    
    #protocol-title {
        text-align: center;
        text-style: bold;
        color: orange;
        margin-bottom: 1;
    }

    #protocol-options {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="protocol-dialogue"):
            yield Static("Select Protocol", id="protocol-input-title")
            yield OptionList(
                "MASQUE",
                "WireGuard",
                None,
                "Back",
                id="protocol-options"
            )
        yield Footer()

    def on_mount(self) -> None:
        option_list = self.query_one("#protocol-options", OptionList)
        option_list.highlighted = 0

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()

        if option == "Back":
            self.dismiss()
        elif option in ["MASQUE", "WireGuard"]:
            success, error_msg = WarpCLI.set_protocol(option)
            self.dismiss((success, error_msg))

class ResetProtocol(ModalScreen):
    CSS = """
        ResetProtocol {
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

        #info-scroll {
            height: auto;
            max-height: 60vh;
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
        success, error_msg = WarpCLI.reset_protocol()

        with Vertical(id="info-dialogue"):
            yield Static("Reset Protocol", id="info-title")
            with VerticalScroll(id="info-scroll"):
                if success:
                    yield Static("Success!", id="info-content")
                else:
                    yield Static(f"{error_msg}", id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class ProtocolTunnel(ModalScreen):
    CSS = """
    ProtocolTunnel {
            align: center middle;
        }

        #protocol-dialogue {
            height: auto;
            border: solid orange;
            padding: 1;
            margin: 2 8;
        }

        #protocol-title {
            text-align: center;
            text-style: bold;
            color: orange;
            margin-bottom: 1;
        }

        #protocol-options {
            height: auto;
        }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def __init__(self):
        super().__init__()
        self.current_protocol = None

    def compose(self) -> ComposeResult:
        with Container(id="protocol-dialogue"):
            yield Static("Protocol Settings", id="protocol-title")
            yield OptionList(id="protocol-options")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_protocol_settings()
        option_list = self.query_one("#protocol-options", OptionList)
        option_list.highlighted = 0

    def refresh_protocol_settings(self) -> None:
        try:
            option_list = self.query_one("#protocol-options", OptionList)
            option_list.clear_options()

            stats, success = WarpCLI.get_stats()
            protocol_display = "Not connected"

            if success:
                for line in stats.splitlines():
                    if line.startswith("Tunnel Protocol: "):
                        protocol_info = line.split("Tunnel Protocol:")[1].strip()
                        if "(" in protocol_info:
                            protocol_display = protocol_info.split("(")[0].strip()
                        else:
                            protocol_display = protocol_info
                        break

            option_list.add_option(f"Set (current: {protocol_display})")
            option_list.add_option("Reset")
            option_list.add_option(None)
            option_list.add_option("Back")
        except Exception as e:
            option_list = self.query_one("#protocol-options", OptionList)
            option_list.clear_options()
            option_list.add_option("Set")
            option_list.add_option("Reset")
            option_list.add_option(None)
            option_list.add_option("Back")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()

        if option == "Back":
            self.app.pop_screen()
        elif option.startswith("Set"):
            self.app.push_screen(ProtocolSelect(), callback=self._on_protocol_select_closed)
        elif option == "Reset":
            self.app.push_screen(ResetProtocol())
            self.refresh_protocol_settings()

    def _on_protocol_select_closed(self, result=None) -> None:
        self.refresh_protocol_settings()

class EndpointInput(ModalScreen):
    CSS = """
        EndpointInput {
            align: center middle;
        }

        #endpoint-dialogue {
            height: auto;
            border: solid orange;
            padding: 1;
            margin: 2 8;
        }

        #endpoint-input-title {
            text-align: center;
            text-style: bold;
            color: orange;
            margin-bottom: 1;
        }

        Input {
            margin-bottom: 1;
        }
        """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="endpoint-dialogue"):
            yield Static("Enter Socket Address", id="endpoint-input-title")
            yield Input(placeholder="IP:PORT", id="endpoint-input")
            yield Static("Press Enter to confirm, Escape to cancel")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        sockaddr = event.value.strip()

        if sockaddr:
            success, error_msg = WarpCLI.set_endpoint(sockaddr)
            self.dismiss((success, error_msg))
        else:
            self.dismiss((False, "Endpoint cannot be empty"))

class ResetEndpoint(ModalScreen):
    CSS = """
        ResetEndpoint {
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

        #info-scroll {
            height: auto;
            max-height: 60vh;
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
        success, error_msg = WarpCLI.reset_endpoint()

        with Vertical(id="info-dialogue"):
            yield Static("Reset Endpoint", id="info-title")
            with VerticalScroll(id="info-scroll"):
                if success:
                    yield Static("Success!", id="info-content")
                else:
                    yield Static(f"{error_msg}", id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class EndpointTunnel(ModalScreen):
    CSS = """
            EndpointTunnel {
                align: center middle;
            }

            #endpoint-dialogue {
                height: auto;
                border: solid orange;
                padding: 1;
                margin: 2 8;
            }

            #endpoint-title {
                text-align: center;
                text-style: bold;
                color: orange;
                margin-bottom: 1;
            }

            #endpoint-options {
                height: auto;
            }
            """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def __init__(self):
        super().__init__()
        self.endpoints = []

    def compose(self) -> ComposeResult:
        with Container(id="endpoint-dialogue"):
            yield Static("Endpoint Settings", id="endpoint-title")
            yield OptionList(id="endpoint-options")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_endpoint_settings()
        option_list = self.query_one("#endpoint-options", OptionList)
        option_list.highlighted = 0

    def refresh_endpoint_settings(self) -> None:
        try:
            option_list = self.query_one("#endpoint-options", OptionList)
            option_list.clear_options()

            stats, success = WarpCLI.get_stats()
            endpoints_display = "Not connected"

            if success:
                for line in stats.splitlines():
                    if line.startswith("Endpoints: "):
                        endpoints_str = line.split("Endpoints:")[1].strip()
                        self.current_endpoints = [ep.strip() for ep in endpoints_str.split(", ")]
                        endpoints_display = ", ".join(self.current_endpoints)
                        break

            option_list.add_option(f"Set (current: {endpoints_display})")
            option_list.add_option("Reset")
            option_list.add_option(None)
            option_list.add_option("Back")
        except Exception as e:
            option_list = self.query_one("#endpoint-options", OptionList)
            option_list.clear_options()
            option_list.add_option("Set")
            option_list.add_option("Reset")
            option_list.add_option(None)
            option_list.add_option("Back")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()

        if option == "Back":
            self.app.pop_screen()
        elif option.startswith("Set"):
            self.app.push_screen(EndpointInput(), callback=self._on_endpoint_input_closed)
        elif option == "Reset":
            self.app.push_screen(ResetEndpoint())
            self.refresh_endpoint_settings()

    def _on_endpoint_input_closed(self, result=None) -> None:
        self.refresh_endpoint_settings()

class DumpTunnel(ModalScreen):
    CSS = """
    DumpTunnel {
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
    
    #info-scroll {
        height: auto;
        max-height: 60vh;
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
        dump, success = WarpCLI.dump_tunnel()

        with Vertical(id="info-dialogue"):
            yield Static("Split Tunnel Routing Dump", id="info-title")
            with VerticalScroll(id="info-scroll"):
                if success:
                    yield Static(dump, id="info-content")
                else:
                    yield Static(f"{dump}", id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class StatsTunnel(ModalScreen):
    CSS = """
    StatsTunnel {
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

    #info-scroll {
        height: auto;
        max-height: 60vh;
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
        stats, success = WarpCLI.get_stats()

        with Vertical(id="info-dialogue"):
            yield Static("Current Tunnel Connection Stats", id="info-title")
            with VerticalScroll(id="info-scroll"):
                if success:
                    yield Static(stats, id="info-content")
                else:
                    yield Static(f"{stats}", id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class RotateKeysTunnel(ModalScreen):
    CSS = """
    RotateKeysTunnel {
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

    def compose(self) -> ComposeResult:
        success, error_msg = WarpCLI.rotate_keys()

        with Vertical(id="info-dialogue"):
            yield Static("Generate New Key-Pair", id="info-title")
            if success:
                yield Static("Success!", id="info-content")
            else:
                yield Static(error_msg, id="info-content")
            yield Button("OK", variant="primary", id="info-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class TunnelSettings(ModalScreen):
    CSS = """
        TunnelSettings {
            align: center middle;
        }

        #tunnel-dialogue {
            height: auto;
            border: solid orange;
            padding: 1;
            margin: 2 8;
        }

        #tunnel-title {
            text-align: center;
            text-style: bold;
            color: orange;
            margin-bottom: 1;
        }

        #tunnel-options {
            height: auto;
        }
        """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def compose(self) -> ComposeResult:
        with Container(id="tunnel-dialogue"):
            yield Static("Tunnel Settings", id="tunnel-title")
            yield OptionList(
                "Dump",
                "Stats",
                "IP",
                "Host",
                "Endpoint",
                "Protocol",
                "Masque Options",
                "Rotate Keys",
                None,
                "Back",
                id="tunnels-options"
            )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = str(event.option.prompt).strip()

        if option == "Back":
            self.app.pop_screen()
            return
        elif option == "Dump":
            self.app.push_screen(DumpTunnel())
        elif option == "Stats":
            self.app.push_screen(StatsTunnel())
        elif option == "Rotate Keys":
            self.app.push_screen(RotateKeysTunnel())
        elif option == "Endpoint":
            self.app.push_screen(EndpointTunnel())
        elif option == "Protocol":
            self.app.push_screen(ProtocolTunnel())
        elif option == "Masque Options":
            self.app.push_screen(MasqueTunnel())
        elif option == "Host":
            self.app.push_screen(HostTunnel())
