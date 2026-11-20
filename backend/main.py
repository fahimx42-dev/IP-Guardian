import ipaddress, socket
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="IP Guardian API", version="1.0.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"app": "IP Guardian", "status": "online"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/my-ip")
def my_ip():
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(502, str(e))

@app.get("/api/ip/{address}")
def lookup_ip(address: str):
    try:
        ipaddress.ip_address(address)
        r = requests.get(f"https://ipwho.is/{address}", timeout=15)
        r.raise_for_status()
        return r.json()
    except ValueError:
        raise HTTPException(400, "Invalid IP address")
    except Exception as e:
        raise HTTPException(502, str(e))

@app.get("/api/dns/{hostname}")
def dns(hostname: str):
    try:
        return {"hostname": hostname, "addresses": sorted({x[4][0] for x in socket.getaddrinfo(hostname, None)})}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/api/subnet/{cidr:path}")
def subnet(cidr: str):
    try:
        n = ipaddress.ip_network(cidr, strict=False)
        return {"network": str(n), "netmask": str(n.netmask), "broadcast": str(n.broadcast_address), "num_addresses": n.num_addresses}
    except ValueError:
        raise HTTPException(400, "Invalid CIDR")
