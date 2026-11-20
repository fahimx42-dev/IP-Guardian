import os, ipaddress, socket
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests, dns.resolver

app = FastAPI(title="IP Guardian API", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
TIMEOUT = 12

def valid_ip(value):
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError:
        raise HTTPException(400, "Invalid IPv4 or IPv6 address")

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/api/health")
def health():
    return {"status": "online", "service": "IP Guardian"}

@app.get("/api/ip/{address}")
def ip_lookup(address: str):
    ip = valid_ip(address)
    try:
        r = requests.get(f"https://ipwho.is/{ip}", timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if not data.get("success", False):
            raise HTTPException(404, data.get("message", "IP lookup failed"))
        return {
            "ip": ip, "type": data.get("type"),
            "continent": data.get("continent"), "country": data.get("country"),
            "region": data.get("region"), "city": data.get("city"),
            "latitude": data.get("latitude"), "longitude": data.get("longitude"),
            "isp": (data.get("connection") or {}).get("isp"),
            "org": (data.get("connection") or {}).get("org"),
            "asn": (data.get("connection") or {}).get("asn"),
            "timezone": (data.get("timezone") or {}).get("id")
        }
    except requests.RequestException as e:
        raise HTTPException(502, f"IP data provider unavailable: {e}")

@app.get("/api/dns/{domain}")
def dns_lookup(domain: str):
    domain = domain.strip().rstrip(".")
    if not domain or len(domain) > 253 or any(c.isspace() for c in domain):
        raise HTTPException(400, "Invalid domain")
    output = {}
    for kind in ("A", "AAAA", "MX", "NS", "TXT", "CNAME"):
        try:
            answers = dns.resolver.resolve(domain, kind, lifetime=5)
            output[kind] = [str(x) for x in answers]
        except Exception:
            output[kind] = []
    return {"domain": domain, "records": output}

@app.get("/api/rdap/{address}")
def rdap_lookup(address: str):
    ip = valid_ip(address)
    try:
        r = requests.get(f"https://rdap.org/ip/{ip}", timeout=TIMEOUT,
                         headers={"Accept": "application/rdap+json"})
        r.raise_for_status()
        d = r.json()
        return {"ip": ip, "name": d.get("name"), "handle": d.get("handle"),
                "country": d.get("country"), "startAddress": d.get("startAddress"),
                "endAddress": d.get("endAddress"), "type": d.get("type"),
                "remarks": d.get("remarks", [])}
    except requests.RequestException as e:
        raise HTTPException(502, f"RDAP provider unavailable: {e}")

@app.get("/api/subnet/{cidr}")
def subnet(cidr: str):
    try:
        n = ipaddress.ip_network(cidr.strip(), strict=False)
        return {"network": str(n), "version": n.version, "netmask": str(n.netmask),
                "broadcast": str(n.broadcast_address), "first": str(n.network_address),
                "last": str(n.broadcast_address), "total_addresses": n.num_addresses,
                "usable_hosts": max(0, n.num_addresses - (2 if n.version == 4 and n.prefixlen < 31 else 0))}
    except ValueError:
        raise HTTPException(400, "Invalid network. Example: 192.168.1.0/24")

@app.get("/api/threat/{address}")
def threat(address: str):
    ip = valid_ip(address)
    key = os.getenv("SHODAN_API_KEY", "").strip()
    if not key:
        return {"ip": ip, "provider": "Shodan", "configured": False,
                "message": "Add SHODAN_API_KEY to your hosting environment to enable this lookup."}
    try:
        r = requests.get("https://api.shodan.io/shodan/host/" + ip,
                         params={"key": key}, timeout=TIMEOUT)
        if r.status_code == 404:
            return {"ip": ip, "provider": "Shodan", "configured": True,
                    "found": False, "message": "No Shodan host record found."}
        r.raise_for_status()
        d = r.json()
        return {"ip": ip, "provider": "Shodan", "configured": True,
                "found": True, "organization": d.get("org"), "isp": d.get("isp"),
                "country": d.get("country_name"), "ports": d.get("ports", []),
                "last_update": d.get("last_update"), "hostnames": d.get("hostnames", [])}
    except requests.RequestException as e:
        raise HTTPException(502, f"Shodan request failed: {e}")

@app.get("/api/bulk")
def bulk_lookup(ips: str):
    values = [x.strip() for x in ips.replace("\\n", ",").split(",") if x.strip()]
    if not values or len(values) > 20:
        raise HTTPException(400, "Provide 1 to 20 comma-separated IP addresses")
    results = []
    for value in values:
        try:
            ip = valid_ip(value)
            r = requests.get(f"https://ipwho.is/{ip}", timeout=TIMEOUT)
            d = r.json()
            results.append({"ip": ip, "success": d.get("success", False),
                            "country": d.get("country"), "city": d.get("city"),
                            "isp": (d.get("connection") or {}).get("isp")})
        except Exception as e:
            results.append({"ip": value, "success": False, "error": str(e)})
    return {"count": len(results), "results": results}
