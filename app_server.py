"""
Servidor Web e API em Tempo Real do SADC-Fortaleza.
- Sincroniza ao vivo com as 11 Estações Automáticas da Defesa Civil de Fortaleza via API Plugfield.
- Executa a interpolação espacial IDW e os 3 Níveis de modelagem preditiva por Ponto Crítico.
- Serve o Painel Operacional Interativo com Login Padrão (admindc), Logo da Defesa Civil e Mapa Leaflet/GeoJSON.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlparse

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
PUBLIC_DIR = ROOT_DIR / "public"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sadc_fortaleza.data_pipeline.plugfield_client import processar_painel_tempo_real


class SADCRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        # Log conciso
        sys.stdout.write(f"[SADC-HTTP] {self.address_string()} - {format % args}\n")

    def _send_json(self, payload: dict, status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def _send_file(self, file_path: Path, content_type: str) -> None:
        if not file_path.exists():
            self.send_error(404, "File not found")
            return
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/api/health":
            self._send_json(
                {
                    "status": "online",
                    "system": "SADC-Fortaleza - Defesa Civil de Fortaleza",
                    "stations_count": 11,
                }
            )
            return

        if route in ("/api/status", "/api/stations"):
            qs = parse_qs(parsed.query)
            chuva_1h = float(qs["chuva_1h"][0]) if "chuva_1h" in qs else None
            mare_m = float(qs["mare"][0]) if "mare" in qs else None
            foco = qs.get("bairro", ["TODOS"])[0]
            payload = processar_painel_tempo_real(
                chuva_simulada_1h_mm=chuva_1h,
                mare_simulada_m=mare_m,
                foco_bairro_simulacao=foco,
            )
            self._send_json(payload)
            return

        if route.endswith("municipio_fortaleza.geojson"):
            self._send_file(PUBLIC_DIR / "municipio_fortaleza.geojson", "application/geo+json; charset=utf-8")
            return

        if route.endswith("bairros_fortaleza.geojson"):
            self._send_file(PUBLIC_DIR / "bairros_fortaleza.geojson", "application/geo+json; charset=utf-8")
            return

        # Default SPA fallback -> public/index.html
        self._send_file(PUBLIC_DIR / "index.html", "text/html; charset=utf-8")


def iniciar_servidor(porta: int = 3005) -> None:
    server = HTTPServer(("0.0.0.0", porta), SADCRequestHandler)
    print("================================================================")
    print("  SADC-FORTALEZA | Defesa Civil de Fortaleza")
    print(f"  Painel Dinâmico & API Plugfield rodando em: http://localhost:{porta}")
    print("  Login padrão: admin.defesacivil | Senha padrão: admindc")
    print("================================================================")
    server.serve_forever()


if __name__ == "__main__":
    porta_env = int(os.environ.get("PORT", "3005"))
    iniciar_servidor(porta_env)
