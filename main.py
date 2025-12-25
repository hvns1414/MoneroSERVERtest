from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Button, Static, Input, Label
)
from textual.containers import Vertical
from textual.timer import Timer
from auth import auth_user, create_user
import wallet

# ---------------- LOGIN ---------------- #

class Login(App):
    def compose(self):
        yield Header()
        yield Input(placeholder="Username", id="u")
        yield Input(placeholder="Password", password=True, id="p")
        yield Button("LOGIN", id="login")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "login":
            role = auth_user(
                self.query_one("#u").value,
                self.query_one("#p").value
            )
            if role:
                self.exit()
                Dashboard(role).run()
            else:
                self.notify("Invalid credentials")

# ---------------- DASHBOARD ---------------- #

class Dashboard(App):

    CSS = """
    Screen { background: #0e0e0e; color: #d0d0d0; }
    Button { background: #1e1e1e; border: round #333; }
    """

    def __init__(self, role):
        super().__init__()
        self.role = role
        self.balance_label = Label("")
        self.rpc_led = Label("RPC: ●")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"ROLE: {self.role.upper()}")
        yield self.rpc_led
        yield self.balance_label

        yield Button("Addresses", id="addr")

        if self.role in ("pro", "root"):
            yield Button("New Address", id="newaddr")
            yield Button("History", id="hist")

        if self.role == "root":
            yield Button("Send XMR", id="send")
            yield Button("Create User", id="newuser")

        yield Footer()

    # -------- LIVE BALANCE (ROOT ONLY) -------- #

    def on_mount(self):
        self.update_status()
        if self.role == "root":
            self.set_interval(5, self.update_status)

    def update_status(self):
        if wallet.rpc_status():
            self.rpc_led.update("RPC: 🟢")
            bal, un = wallet.balances()
            self.balance_label.update(f"Balance: {bal} | Unlocked: {un}")
        else:
            self.rpc_led.update("RPC: 🔴")

    # -------- BUTTONS -------- #

    def on_button_pressed(self, e):
        if e.button.id == "addr":
            self.notify("\n".join(map(str, wallet.addresses())))

        elif e.button.id == "newaddr":
            self.notify(wallet.new_address())

        elif e.button.id == "hist":
            self.notify("\n".join(map(str, wallet.history())))

        elif e.button.id == "send" and self.role == "root":
            self.push_screen(TransferModal())

        elif e.button.id == "newuser" and self.role == "root":
            self.push_screen(UserModal())

# ---------------- MODALS ---------------- #

class TransferModal(App):
    def compose(self):
        yield Header()
        yield Input(placeholder="Recipient Address", id="addr")
        yield Input(placeholder="Amount (XMR)", id="amt")
        yield Button("SEND", id="go")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "go":
            tx = wallet.transfer(
                self.query_one("#addr").value,
                float(self.query_one("#amt").value)
            )
            self.notify(f"TX HASH: {tx}")
            self.exit()

class UserModal(App):
    def compose(self):
        yield Header()
        yield Input(placeholder="Username", id="u")
        yield Input(placeholder="Password", id="p")
        yield Input(placeholder="Role (low/pro/root)", id="r")
        yield Button("CREATE", id="c")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "c":
            ok = create_user(
                self.query_one("#u").value,
                self.query_one("#p").value,
                self.query_one("#r").value
            )
            self.notify("User created" if ok else "User exists")
            self.exit()

# ---------------- START ---------------- #

if __name__ == "__main__":
    create_user("root", "toor", "root")
    Login().run()
