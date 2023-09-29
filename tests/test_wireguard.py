import tempfile
from ipaddress import IPv4Interface
from ipaddress import IPv4Network
from pathlib import Path

import pytest

from wg_config.wireguard import Peer
from wg_config.wireguard import get_next_valid_ip
from wg_config.wireguard import wireguard_factory

TEST_CONFIG = """[Interface]
# This is a second comment
PrivateKey = T0n35r75nfWyaScP/JpNSAFdZMQiP6coiTDq8Zm4TVE=
# PublicKey = +1v8fSkAW7SJFHNrkHlTrnt10dKNu2E727H3OhrSNQk=
ListenPort = 51820
Address = 10.0.0.0/18

[Peer]
PublicKey = d2Ry6fqdWjBfLtgGhD5ABi4JxnRGEfyw6OMNkXLcE0Q=
AllowedIPs = 10.0.0.2/32
Endpoint = 1.2.3.4:51820
PersistentKeepalive = 25
PresharedKey = preshared_key

[Peer]
PublicKey = ll40MSH9pD6ljd++PBcyUGWv/C/wCTbotsD+c0W42gM=
AllowedIPs = 10.0.0.3/32
"""


@pytest.fixture(scope="function")
def test_config():
    with tempfile.NamedTemporaryFile("w+") as f:
        f.write(TEST_CONFIG)
        f.seek(0)
        yield Path(f.name)


def test_add_peer(test_config):
    wg = wireguard_factory(test_config)
    peer = Peer(
        PublicKey="eBvBVLo6wH0XkBfIjeLPf8ydBTfU/gMqJOH4nmVXcDD=",
        AllowedIPs="10.0.0.4/32",
    )
    wg.add_peer(peer)
    wg.save()
    wg = wireguard_factory(test_config)
    assert len(wg.peers) == 3
    assert any(p.to_wgconfig() == peer.to_wgconfig() for p in wg.peers)


def test_delete_peer(test_config):
    wg = wireguard_factory(test_config)
    peer = Peer(
        PublicKey="d2Ry6fqdWjBfLtgGhD5ABi4JxnRGEfyw6OMNkXLcE0Q=",
        AllowedIPs="10.0.0.2/32",
    )
    wg.delete_peer(peer)
    wg.save()
    wg = wireguard_factory(test_config)
    assert len(wg.peers) == 1


def test_get_peer_by_ip(test_config):
    expected = {
        "PublicKey": "d2Ry6fqdWjBfLtgGhD5ABi4JxnRGEfyw6OMNkXLcE0Q=",
        "AllowedIPs": "10.0.0.2/32",
    }
    wg = wireguard_factory(test_config)
    peer = wg.get_peer(ip=expected["AllowedIPs"])
    assert peer.PublicKey == expected["PublicKey"]
    assert peer.AllowedIPs == expected["AllowedIPs"]


def test_get_peer_by_public_key(test_config):
    expected = {
        "PublicKey": "d2Ry6fqdWjBfLtgGhD5ABi4JxnRGEfyw6OMNkXLcE0Q=",
        "AllowedIPs": "10.0.0.2/32",
    }
    wg = wireguard_factory(test_config)
    peer = wg.get_peer(public_key=expected["PublicKey"])
    assert peer.PublicKey == expected["PublicKey"]
    assert peer.AllowedIPs == expected["AllowedIPs"]


def test_get_next_peer_interface(test_config):
    wg = wireguard_factory(test_config)
    next_ip = wg.get_next_peer_interface()
    assert next_ip == IPv4Interface("10.0.0.4/32")


def test_wireguard_factory(test_config):
    wg = wireguard_factory(test_config)
    assert len(wg.peers) == 2

    with tempfile.TemporaryDirectory() as parent:
        path = Path(parent)
        with tempfile.NamedTemporaryFile("w+", suffix=".conf", dir=path) as f:
            f.write(TEST_CONFIG)
            f.seek(0)
            wg = wireguard_factory(path, f.name)
            assert len(wg.peers) == 2


def test_get_next_valid_ip():
    ipv4_net = IPv4Network("10.0.64.0/18")
    ipv4_interface = IPv4Interface("10.0.64.1/32")
    expected = IPv4Interface("10.0.64.2/32")
    next_ip = get_next_valid_ip(ipv4_interface, ipv4_net)
    assert next_ip == expected

    ipv4_net = IPv4Network("10.0.64.0/18")
    ipv4_interface = IPv4Interface("10.0.64.254/32")
    expected = IPv4Interface("10.0.65.1/32")
    next_ip = get_next_valid_ip(ipv4_interface, ipv4_net)
    assert next_ip == expected

    ipv4_net = IPv4Network("10.0.64.0/18")
    ipv4_interface = IPv4Interface("10.0.64.255/32")
    expected = IPv4Interface("10.0.65.1/32")
    next_ip = get_next_valid_ip(ipv4_interface, ipv4_net)
    assert next_ip == expected
