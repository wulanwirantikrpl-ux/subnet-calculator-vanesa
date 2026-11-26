from __future__ import annotations

import ipaddress
import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(
    title="SubnetEDU — Kalkulator Subnet & VLSM",
    description="Alat pembelajaran subnetting IPv4 dan alokasi VLSM.",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": "Format data tidak valid."})


def _parse_ipv4(ip: str) -> ipaddress.IPv4Address:
    """Validasi IPv4 secara ketat, termasuk larangan nol di depan."""
    if not isinstance(ip, str) or not re.fullmatch(
        r"(0|[1-9][0-9]{0,2})\.(0|[1-9][0-9]{0,2})\.(0|[1-9][0-9]{0,2})\.(0|[1-9][0-9]{0,2})",
        ip,
    ):
        raise ValueError("Alamat IPv4 harus terdiri dari empat oktet tanpa spasi atau angka nol di depan.")
    try:
        return ipaddress.IPv4Address(ip)
    except ipaddress.AddressValueError as exc:
        raise ValueError("Setiap oktet IPv4 harus berada pada rentang 0 sampai 255.") from exc


def hitung_subnet(ip: str, prefix: int) -> dict[str, Any]:
    """Menghitung detail subnet IPv4 sesuai aturan pada SPEC.md."""
    address = _parse_ipv4(ip)
    if isinstance(prefix, bool) or not isinstance(prefix, int) or not 0 <= prefix <= 32:
        raise ValueError("Prefix harus berupa bilangan bulat dari 0 sampai 32.")

    mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF if prefix else 0
    ip_int = int(address)
    network_int = ip_int & mask_int
    wildcard_int = 0xFFFFFFFF ^ mask_int
    broadcast_int = network_int | wildcard_int
    network = ipaddress.IPv4Address(network_int)
    mask = ipaddress.IPv4Address(mask_int)

    if prefix <= 30:
        first_host = ipaddress.IPv4Address(network_int + 1)
        last_host = ipaddress.IPv4Address(broadcast_int - 1)
        usable_hosts = (1 << (32 - prefix)) - 2
        broadcast = str(ipaddress.IPv4Address(broadcast_int))
    elif prefix == 31:
        # RFC 3021: kedua alamat pada link point-to-point dapat digunakan.
        first_host = ipaddress.IPv4Address(network_int)
        last_host = ipaddress.IPv4Address(network_int + 1)
        usable_hosts = 2
        broadcast = None
    else:
        first_host = last_host = address
        usable_hosts = 1
        broadcast = None

    return {
        "mask": str(mask),
        "network": str(network),
        "broadcast": broadcast,
        "first_host": str(first_host),
        "last_host": str(last_host),
        "usable_hosts": usable_hosts,
    }


class VLSMRequest(BaseModel):
    network: str
    kebutuhan_host: list[int] = Field(min_length=1)


def alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict[str, Any]]:
    """Mengalokasikan subnet dari kebutuhan host terbesar ke terkecil."""
    if not isinstance(network_cidr, str) or "/" not in network_cidr:
        raise ValueError("Network harus menggunakan format CIDR, contoh 192.168.1.0/24.")
    try:
        network = ipaddress.IPv4Network(network_cidr, strict=True)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError) as exc:
        raise ValueError("Network CIDR tidak valid atau alamat yang diberikan bukan alamat network.") from exc

    if not isinstance(kebutuhan_host, list) or not kebutuhan_host:
        raise ValueError("Daftar kebutuhan host tidak boleh kosong.")
    if any(isinstance(n, bool) or not isinstance(n, int) or n < 1 for n in kebutuhan_host):
        raise ValueError("Setiap kebutuhan host harus berupa bilangan bulat minimal 1.")

    current = int(network.network_address)
    end = int(network.broadcast_address)
    hasil = []

    for need in sorted(kebutuhan_host, reverse=True):
        # Sesuai spesifikasi: blok terkecil yang menampung kebutuhan + network/broadcast,
        # dengan ukuran minimum /30.
        block_size = max(4, 1 << (need + 2 - 1).bit_length())
        prefix = 32 - (block_size.bit_length() - 1)
        aligned = ((current + block_size - 1) // block_size) * block_size
        block_end = aligned + block_size - 1
        if aligned > end or block_end > end:
            raise ValueError("Blok alamat pada network tidak cukup untuk menampung seluruh kebutuhan host.")

        subnet_ip = str(ipaddress.IPv4Address(aligned))
        detail = hitung_subnet(subnet_ip, prefix)
        hasil.append({
            "kebutuhan": need,
            "network_cidr": f"{subnet_ip}/{prefix}",
            **detail,
        })
        current = block_end + 1

    return hasil


@app.get("/", response_class=HTMLResponse)
async def halaman_utama():
    return (BASE_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/subnet")
async def api_subnet(ip: str = Query(...), prefix: str = Query(...)):
    try:
        if not re.fullmatch(r"(0|[1-9][0-9]*)", prefix):
            raise ValueError("Prefix harus berupa bilangan bulat dari 0 sampai 32.")
        return hitung_subnet(ip, int(prefix))
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.post("/api/vlsm")
async def api_vlsm(data: VLSMRequest):
    try:
        return alokasi_vlsm(data.network, data.kebutuhan_host)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
