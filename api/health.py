"""
Endpoint Serverless da Vercel (/api/health) para o SADC-Fortaleza.
"""

from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        raw = json.dumps(
            {
                "status": "online",
                "version": "2.5.0-symmetric-maps-clean-markers",
                "system": "SADC-Fortaleza - Defesa Civil de Fortaleza",
                "stations_count": 11,
                "sme_schools_count": 457,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)
