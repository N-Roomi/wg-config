import re
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.prompt import Confirm
from rich.prompt import Prompt
from rich.table import Table
from typing_extensions import Annotated

from .peer import Peer
from .wireguard import wireguard_factory

OptionalArgument = Annotated[Optional[str], typer.Argument()]
WgConfigEnv = Annotated[Path, typer.Argument(envvar="WG_CONFIG")]

WG_KEY_REGEX = re.compile(r"^[A-Za-z0-9+/]{42}[AEIMQUYcgkosw480]=$")
DEFAULT_WG_PATH = Path("/etc/wireguard")

console = Console()
app = typer.Typer(name="wg_config")


@app.command()
def add(
    interface: str,
    public_key: str,
    ip: OptionalArgument = None,
    wg_config: WgConfigEnv = DEFAULT_WG_PATH,
):
    if not WG_KEY_REGEX.match(public_key):
        print("Invalid public key")
        print("Aborting")
        return
    wg = wireguard_factory(wg_config, interface)
    if ip is None:
        ip = str(wg.get_next_peer_interface())
        console.print(f"Next available IP: {ip}")
    new_peer = Peer(PublicKey=public_key, AllowedIPs=ip)
    if wg.peer_exists(new_peer):
        print("Peer exists")
        print("Aborting")
        return
    name = None
    if Confirm.ask("Would you like to name this peer"):
        name = Prompt.ask("Please enter name").strip()
        new_peer.Name = name if name else None
    table = Table("ip", "public key", "name")
    table.add_row(new_peer.AllowedIPs, new_peer.PublicKey, new_peer.Name)
    console.print(table)
    if not (Confirm.ask("Is this correct")):
        print("Aborting")
        return
    print(f"Adding peer with public key {public_key} and ip {ip} to {interface}")
    wg.add_peer(new_peer)
    wg.save()
    console.print("Successfully added peer")


@app.command()
def delete(
    interface: str,
    public_key: Optional[str] = None,
    ip: Optional[str] = None,
    wg_config: WgConfigEnv = DEFAULT_WG_PATH,
):
    print(f"Deleting peer with public key {public_key} from {interface}")
    wg = wireguard_factory(wg_config, interface)
    peer = wg.get_peer(public_key=public_key, ip=ip)
    wg.delete_peer(peer)
    wg.save()


# TODO: add an init command that will create the interface


@app.command()
def list(  # noqa: A001
    interface: str,
    wg_config: WgConfigEnv = DEFAULT_WG_PATH,
):
    wg = wireguard_factory(wg_config, interface)
    peers = [i for i in wg.peers]
    peers.sort(key=lambda x: x.AllowedIPs)
    table = Table("ip", "public key", title=f"{interface} peers")
    for peer in peers:
        table.add_row(peer.AllowedIPs, peer.PublicKey)
    console.print(table)


@app.command()
def next(  # noqa: A001
    interface: str,
    wg_config: WgConfigEnv = DEFAULT_WG_PATH,
):
    print(f"Getting next ip for {interface}")
    wg = wireguard_factory(wg_config, interface)
    next_ip = wg.get_next_peer_interface()
    print(f"next available ip is {next_ip}")


@app.command()
def test(
    number: int,
    name: OptionalArgument = None,
):
    print(f"test {number} {name}")
    greeting = Prompt.ask("What is your greeting")
    print(f"{greeting} {name}")


# TODO: add a command to update the interface

# TODO: add a command to update a peer
