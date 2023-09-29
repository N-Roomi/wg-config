import dataclasses
from typing import Optional


@dataclasses.dataclass
class Peer:
    PublicKey: str
    AllowedIPs: str
    Endpoint: Optional[str] = None
    PersistentKeepalive: Optional[int] = None
    PresharedKey: Optional[str] = None
    Name: Optional[str] = None

    @classmethod
    def from_wgconfig(cls, data: dict):
        return peer_from_wgconfig(data)

    def to_wgconfig(self, *, as_json: bool = False):
        if as_json:
            import json

            return json.dumps(peer_to_wgconfig(self))
        return peer_to_wgconfig(self)


def parse_peer_name(name: Optional[str]):
    if name is None:
        return
    if name.startswith("# "):
        return name[2:]
    return name


def generate_peer_name(name: Optional[str]):
    if name is None:
        return
    if not name.startswith("# "):
        return f"# {name}"
    return name


def peer_from_wgconfig(data: dict):
    public_key = data["PublicKey"]
    allowed_ips = data["AllowedIPs"]
    endpoint = data.get("Endpoint")
    persistent_keepalive = data.get("PersistentKeepalive")
    preshared_key = data.get("PresharedKey")
    name = parse_peer_name(data.get("Name"))
    return Peer(
        PublicKey=public_key,
        AllowedIPs=allowed_ips,
        Endpoint=endpoint,
        PersistentKeepalive=persistent_keepalive,
        PresharedKey=preshared_key,
        Name=name,
    )


def peer_to_wgconfig(data: Peer):
    peer: dict = {
        "PublicKey": data.PublicKey,
        "AllowedIPs": data.AllowedIPs,
    }
    if data.Endpoint:
        peer["Endpoint"] = data.Endpoint
    if data.PersistentKeepalive:
        peer["PersistentKeepalive"] = data.PersistentKeepalive
    if data.PresharedKey:
        peer["PresharedKey"] = data.PresharedKey
    if data.Name:
        peer["Name"] = generate_peer_name(data.Name)
    return peer
