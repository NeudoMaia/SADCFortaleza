"""
Endpoint Serverless da Vercel para o SADC-Fortaleza.
- Atende /api/health, /api/status e /api/stations em produção na Vercel.
- Sincroniza ao vivo com as 11 Estações Automáticas da Defesa Civil (API Plugfield) + Radar Meteorológico FUNCEME (GMWR1000SST) + 457 Unidades Escolares SME/ASSEPLAN.
"""

from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sadc_fortaleza.data_pipeline.plugfield_client import processar_painel_tempo_real


class handler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path
        qs = parse_qs(parsed.query)

        if "health" in route or "health" in qs:
            self._send_json(
                {
                    "status": "online",
                    "version": "2.5.0-symmetric-maps-clean-markers",
                    "system": "SADC-Fortaleza - Defesa Civil de Fortaleza",
                    "stations_count": 11,
                    "sme_schools_count": 457,
                }
            )
            return

        chuva_1h = float(qs["chuva_1h"][0]) if "chuva_1h" in qs else None
        mare_m = float(qs["mare"][0]) if "mare" in qs else None
        foco = qs.get("bairro", ["TODOS"])[0]
        payload = processar_painel_tempo_real(
            chuva_simulada_1h_mm=chuva_1h,
            mare_simulada_m=mare_m,
            foco_bairro_simulacao=foco,
        )
        payload["versao_painel"] = "2.5.0-symmetric-maps-clean-markers"
        self._send_json(payload)
