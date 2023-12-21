import ipaddress
from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Union
from typing import cast

import wgconfig

from .peer import Peer


class Wireguard:
    def __init__(self, config: wgconfig.WGConfig):
        self.config = config

    @property
    def peers(self):
        peers = cast(Dict[str, Dict[str, str]], self.config.get_peers(keys_only=False))
        peers = [Peer.from_wgconfig(peer) for peer in peers.values()]
        return peers

    def save(self):
        self.config.write_file()

    def get_peer(self, ip: Optional[str] = None, public_key: Optional[str] = None):
        if ip:
            matching = [peer for peer in self.peers if ip in peer.AllowedIPs]
            if len(matching) == 0:
                raise ValueError(f"No peer with ip {ip}")
            if len(matching) > 1:
                raise ValueError(f"Multiple peers with ip {ip}")
            return matching[0]
        if public_key:
            peer = self.config.get_peer(public_key)
            if not peer:
                raise ValueError(f"No peer with public key {public_key}")
            return Peer.from_wgconfig(peer)
        raise ValueError("Must provide either ip or public_key")

    def add_peer(self, peer: Peer):
        if self.peer_exists(peer):
            raise ValueError("Peer already exists")
        self.config.add_peer(peer.PublicKey, peer.to_wgconfig().get("Name"))
        self.config.add_attr(peer.PublicKey, "AllowedIPs", peer.AllowedIPs)
        if peer.Endpoint:
            self.config.add_attr(peer.PublicKey, "Endpoint", peer.Endpoint)
        if peer.PersistentKeepalive:
            self.config.add_attr(
                peer.PublicKey,
                "PersistentKeepalive",
                peer.PersistentKeepalive,
            )
        if peer.PresharedKey:
            self.config.add_attr(peer.PublicKey, "PresharedKey", peer.PresharedKey)

    def peer_exists(self, peer: Peer):
        known_public = {p.PublicKey for p in self.peers}
        if peer.PublicKey in known_public:
            return True
        known_ips = {p.AllowedIPs for p in self.peers}
        if peer.AllowedIPs in known_ips:
            return True
        return False

    def delete_peer(self, peer: Peer):
        if not self.peer_exists(peer):
            raise ValueError("Peer does not exist")
        self.config.del_peer(peer.PublicKey)

    def get_next_peer_interface(self):
        server_interface = self.config.get_interface()["Address"]
        server_network = ipaddress.ip_interface(server_interface).network
        max_ip = max({ipaddress.ip_interface(peer.AllowedIPs) for peer in self.peers})
        return get_next_valid_ip(max_ip, server_network)


def wireguard_factory(path: Path, interface: Optional[str] = None):
    if interface is not None:
        if not interface.endswith(".conf"):
            interface = interface + ".conf"
        path = path / interface
    if not path.exists():
        raise ValueError(f"Path {path} does not exist")
    if not path.is_file():
        raise ValueError(f"Path {path} is not a file")
    wg = wgconfig.WGConfig(path)
    wg.read_file()
    return Wireguard(wg)


def get_next_valid_ip(
    interface: Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface],
    network: Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
):
    next_ip = interface + 1
    if isinstance(next_ip, ipaddress.IPv4Interface):
        last_octet = str(next_ip.ip).split(".")[-1]
        while last_octet == "0" or last_octet == "255":
            next_ip = next_ip + 1
            last_octet = str(next_ip.ip).split(".")[-1]
    if next_ip not in network:
        raise ValueError("No more available ips")
    return next_ip
