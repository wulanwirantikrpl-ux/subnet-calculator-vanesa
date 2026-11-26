import pytest
from fastapi.testclient import TestClient
from main import app, hitung_subnet, alokasi_vlsm

client = TestClient(app)


@pytest.mark.parametrize(
    "ip,prefix,expected",
    [
        ("172.16.5.130", 25, {"mask": "255.255.255.128", "network": "172.16.5.128", "broadcast": "172.16.5.255", "first_host": "172.16.5.129", "last_host": "172.16.5.254", "usable_hosts": 126}),
        ("10.0.0.0", 30, {"mask": "255.255.255.252", "network": "10.0.0.0", "broadcast": "10.0.0.3", "first_host": "10.0.0.1", "last_host": "10.0.0.2", "usable_hosts": 2}),
        ("192.168.1.0", 31, {"mask": "255.255.255.254", "network": "192.168.1.0", "broadcast": None, "first_host": "192.168.1.0", "last_host": "192.168.1.1", "usable_hosts": 2}),
        ("192.168.1.5", 32, {"mask": "255.255.255.255", "network": "192.168.1.5", "broadcast": None, "first_host": "192.168.1.5", "last_host": "192.168.1.5", "usable_hosts": 1}),
        ("0.0.0.1", 0, {"mask": "0.0.0.0", "network": "0.0.0.0", "broadcast": "255.255.255.255", "first_host": "0.0.0.1", "last_host": "255.255.255.254", "usable_hosts": 4294967294}),
    ],
)
def test_hitung_subnet(ip, prefix, expected):
    assert hitung_subnet(ip, prefix) == expected


@pytest.mark.parametrize("ip", ["256.1.1.1", "192.168.01.1", "192.168.1", "abc", "", " 192.168.1.1", "192.168.1.1 "])
def test_ip_invalid(ip):
    with pytest.raises(ValueError):
        hitung_subnet(ip, 24)


@pytest.mark.parametrize("prefix", [-1, 33, 2.5, True])
def test_prefix_invalid(prefix):
    with pytest.raises(ValueError):
        hitung_subnet("192.168.1.1", prefix)


def test_api_subnet_success():
    response = client.get("/api/subnet?ip=172.16.5.130&prefix=25")
    assert response.status_code == 200
    assert response.json()["network"] == "172.16.5.128"
    assert response.json()["usable_hosts"] == 126


@pytest.mark.parametrize("url", [
    "/api/subnet?ip=256.1.1.1&prefix=24",
    "/api/subnet?ip=192.168.01.1&prefix=24",
    "/api/subnet?ip=192.168.1.1&prefix=33",
    "/api/subnet?ip=192.168.1.1&prefix=-1",
])
def test_api_subnet_invalid_returns_400(url):
    assert client.get(url).status_code == 400


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "<html" in response.text.lower()


def test_vlsm_expected_allocation():
    result = alokasi_vlsm("192.168.1.0/24", [100, 50, 20, 2])
    assert [item["network_cidr"] for item in result] == [
        "192.168.1.0/25", "192.168.1.128/26",
        "192.168.1.192/27", "192.168.1.224/30"
    ]


def test_vlsm_api():
    response = client.post("/api/vlsm", json={"network": "192.168.1.0/24", "kebutuhan_host": [100, 50, 20, 2]})
    assert response.status_code == 200
    assert len(response.json()) == 4


@pytest.mark.parametrize("network,needs", [
    ("192.168.1.1/24", [10]),
    ("192.168.1.0/24", []),
    ("192.168.1.0/24", [0]),
    ("192.168.1.0/24", [-2]),
    ("192.168.1.0/24", [200, 100]),
    ("bad-cidr", [10]),
])
def test_vlsm_invalid(network, needs):
    with pytest.raises(ValueError):
        alokasi_vlsm(network, needs)


def test_vlsm_api_invalid_returns_400():
    response = client.post("/api/vlsm", json={"network": "192.168.1.0/24", "kebutuhan_host": [200, 100]})
    assert response.status_code == 400
