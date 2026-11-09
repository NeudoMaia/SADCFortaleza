"""
Servidor Web Multi-Thread e API em Tempo Real do SADC-Fortaleza.
- Sincroniza ao vivo (ciclo automático de 5 minutos) com as 11 Estações Automáticas da Defesa Civil de Fortaleza via API Plugfield.
- Integra imagem satelital e climatologia da NASA (EPIC / GIBS VIIRS & MODIS / POWER) cruzada com os pluviômetros.
- Executa a interpolação espacial IDW e os 3 Níveis de modelagem preditiva por Ponto Crítico.
- Serve o Painel Operacional Interativo com Chave Pública CARTO oficial (Padrão DCCALOR), Lista de Bairros com Endereço de Referência, Logo da Defesa Civil e Login Padrão (admindc).
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import threading
from urllib.parse import parse_qs, urlparse

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
PUBLIC_DIR = ROOT_DIR / "public"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sadc_fortaleza.data_pipeline.plugfield_client import processar_painel_tempo_real


class SADCThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True


class SADCRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        sys.stdout.write(f"[SADC-HTTP] {self.address_string()} - {format % args}\n")
        sys.stdout.flush()

    def _send_no_cache_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Access-Control-Allow-Origin", "*")

    def _send_json(self, payload: dict, status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self._send_no_cache_headers()
        self.end_headers()
        self.wfile.write(raw)

    def _send_file(self, file_path: Path, content_type: str, clear_cache: bool = False) -> None:
        if not file_path.exists():
            self.send_error(404, "File not found")
            return
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self._send_no_cache_headers()
        if clear_cache:
            self.send_header("Clear-Site-Data", '"cache"')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/api/health":
            self._send_json(
                {
                    "status": "online",
                    "version": "2.2.0-funceme-radar-rmf",
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
            payload["versao_painel"] = "2.2.0-funceme-radar-rmf"
            self._send_json(payload)
            return

        if route.endswith("legenda_chuva_agora.png"):
            self._send_file(PUBLIC_DIR / "legenda_chuva_agora.png", "image/png")
            return

        if route.endswith("legenda_acumulados.png"):
            self._send_file(PUBLIC_DIR / "legenda_acumulados.png", "image/png")
            return

        if route.endswith("municipio_fortaleza.geojson"):
            self._send_file(
                PUBLIC_DIR / "municipio_fortaleza.geojson",
                "application/geo+json; charset=utf-8",
            )
            return

        if route.endswith("bairros_fortaleza.geojson"):
            self._send_file(
                PUBLIC_DIR / "bairros_fortaleza.geojson",
                "application/geo+json; charset=utf-8",
            )
            return

        # Default SPA fallback -> public/index.html com limpeza de cache do navegador
        self._send_file(PUBLIC_DIR / "index.html", "text/html; charset=utf-8", clear_cache=True)


def iniciar_servidor(porta_principal: int = 3005, porta_espelho: int = 3006) -> None:
    server_main = SADCThreadingHTTPServer(("0.0.0.0", porta_principal), SADCRequestHandler)

    try:
        server_mirror = SADCThreadingHTTPServer(("0.0.0.0", porta_espelho), SADCRequestHandler)
        t_mirror = threading.Thread(target=server_mirror.serve_forever, daemon=True)
        t_mirror.start()
    except OSError:
        pass

    print("================================================================", flush=True)
    print("  SADC-FORTALEZA v2.2 | Defesa Civil de Fortaleza + Radar FUNCEME", flush=True)
    print(f"  Painel Dinâmico (Principal): http://localhost:{porta_principal}/?v=2.2", flush=True)
    print(f"  Painel Dinâmico (Espelho)  : http://localhost:{porta_espelho}/", flush=True)
    print("  Login padrão: admin.defesacivil | Senha padrão: admindc", flush=True)
    print("================================================================", flush=True)
    server_main.serve_forever()


if __name__ == "__main__":
    porta_env = int(os.environ.get("PORT", "3005"))
    iniciar_servidor(porta_env, porta_env + 1)
