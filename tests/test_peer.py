import json

import pytest

from wg_config.peer import Peer
from wg_config.peer import generate_peer_name
from wg_config.peer import parse_peer_name
from wg_config.peer import peer_from_wgconfig
from wg_config.peer import peer_to_wgconfig


@pytest.fixture(scope="function")
def peer_full():
    return Peer(
        PublicKey="abc123",
        AllowedIPs="192.168.1.1/24",
        Endpoint="example.com:51820",
        PersistentKeepalive=25,
        PresharedKey="def456",
        Name="peer1",
    )


@pytest.fixture(scope="function")
def peer_partial():
    return Peer(
        PublicKey="abc123",
        AllowedIPs="192.168.1.1/24",
    )


@pytest.fixture(scope="function")
def wg_peer_full():
    return {
        "PublicKey": "abc123",
        "AllowedIPs": "192.168.1.1/24",
        "Endpoint": "example.com:51820",
        "PersistentKeepalive": 25,
        "PresharedKey": "def456",
        "Name": "# peer1",
    }


@pytest.fixture(scope="function")
def wg_peer_partial():
    return {
        "PublicKey": "abc123",
        "AllowedIPs": "192.168.1.1/24",
    }


def test_peer_peer_from_wgconfig(wg_peer_full, wg_peer_partial):
    peer = Peer.from_wgconfig(wg_peer_full)
    assert peer.PublicKey == "abc123"
    assert peer.AllowedIPs == "192.168.1.1/24"
    assert peer.Endpoint == "example.com:51820"
    assert peer.PersistentKeepalive == 25
    assert peer.PresharedKey == "def456"
    assert peer.Name == "peer1"

    peer = Peer.from_wgconfig(wg_peer_partial)
    assert peer.PublicKey == "abc123"
    assert peer.AllowedIPs == "192.168.1.1/24"
    assert peer.Endpoint is None
    assert peer.PersistentKeepalive is None
    assert peer.PresharedKey is None
    assert peer.Name is None


def test_peer_peer_to_wgconfig(peer_full, peer_partial):
    expected = {
        "PublicKey": "abc123",
        "AllowedIPs": "192.168.1.1/24",
        "Endpoint": "example.com:51820",
        "PersistentKeepalive": 25,
        "PresharedKey": "def456",
        "Name": "# peer1",
    }
    assert peer_full.to_wgconfig() == expected

    expected = {
        "PublicKey": "abc123",
        "AllowedIPs": "192.168.1.1/24",
    }
    assert peer_partial.to_wgconfig() == expected


def test_peer_peer_to_wgconfig_as_json(peer_full, peer_partial):
    expected = {
        "PublicKey": "abc123",
        "AllowedIPs": "192.168.1.1/24",
        "Endpoint": "example.com:51820",
        "PersistentKeepalive": 25,
        "PresharedKey": "def456",
        "Name": "# peer1",
    }
    assert json.loads(peer_full.to_wgconfig(as_json=True)) == expected

    expected = {
        "PublicKey": "abc123",
        "AllowedIPs": "192.168.1.1/24",
    }
    assert json.loads(peer_partial.to_wgconfig(as_json=True)) == expected


def test_parse_peer_name():
    assert parse_peer_name(None) is None
    assert parse_peer_name("peer_name") == "peer_name"
    assert parse_peer_name("# peer_name") == "peer_name"
    assert parse_peer_name("#peer_name") == "#peer_name"
    assert parse_peer_name("# #peer_name") == "#peer_name"
    assert parse_peer_name("peer_name # test") == "peer_name # test"


def test_generate_peer_name():
    assert generate_peer_name(None) is None
    assert generate_peer_name("peer_name") == "# peer_name"
    assert generate_peer_name("# peer_name") == "# peer_name"
    assert generate_peer_name("# #peer_name") == "# #peer_name"
    assert generate_peer_name("# # peer_name") == "# # peer_name"
    assert generate_peer_name("peer_name # test") == "# peer_name # test"


def test_peer_from_wgconfig(wg_peer_full, wg_peer_partial):
    peer = peer_from_wgconfig(wg_peer_full)
    assert peer.PublicKey == "abc123"
    assert peer.AllowedIPs == "192.168.1.1/24"
    assert peer.Endpoint == "example.com:51820"
    assert peer.PersistentKeepalive == 25
    assert peer.PresharedKey == "def456"
    assert peer.Name == "peer1"

    peer = peer_from_wgconfig(wg_peer_partial)
    assert peer.PublicKey == "abc123"
    assert peer.AllowedIPs == "192.168.1.1/24"
    assert peer.Endpoint is None
    assert peer.PersistentKeepalive is None
    assert peer.PresharedKey is None
    assert peer.Name is None


def test_peer_to_wgconfig(peer_full, peer_partial):
    expected = {
        "PublicKey": "abc123",
        "AllowedIPs": "192.168.1.1/24",
        "Endpoint": "example.com:51820",
        "PersistentKeepalive": 25,
        "PresharedKey": "def456",
        "Name": "# peer1",
    }
    assert peer_to_wgconfig(peer_full) == expected

    expected = {
        "PublicKey": "abc123",
        "AllowedIPs": "192.168.1.1/24",
    }
    assert peer_to_wgconfig(peer_partial) == expected
