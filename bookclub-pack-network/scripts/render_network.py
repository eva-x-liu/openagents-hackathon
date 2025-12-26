#!/usr/bin/env python3
import os
from pathlib import Path

TEMPLATE = Path("network/network.template.yaml")
OUT = Path("network/network.yaml")

def main():
    http_port = os.environ.get("PORT") or os.environ.get("HTTP_PORT") or "8700"
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("__HTTP_PORT__", str(http_port))
    OUT.write_text(text, encoding="utf-8")
    print(f"[render_network] wrote {OUT} with http port={http_port}")

if __name__ == "__main__":
    main()