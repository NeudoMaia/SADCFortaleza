"""
Simulador hidrometeorológico e operacional realista para Fortaleza (resolução de 10 minutos).
Modela:
- Eventos convectivos e estratiformes da Quadra Chuvosa (ZCIT / VCAN / Ondas de Leste) distribuídos
  ao longo de todo o período (Treino, Validação e Teste).
- Maré astronômica semidiurna do Porto do Mucuripe + maré meteorológica (vento/pressão).
- Telemetria das 11 estações da Defesa Civil + postos Funceme/CEMADEN com falhas realistas
  (valores negativos espúrios, picos irreais de interferência elétrica e janelas offline).
- Resposta hidrológica específica de cada Ponto Crítico (Jacarecanga, Padre Andrade,
  Aldeota, Itaoca, Lagamar, Messejana), câmeras PMPU e chamados 40199, incluindo incerteza
  urbana de microdrenagem (obstruções transitórias de bocas de lobo por resíduos sólidos).
"""

from datetime import datetime, timedelta
from typing import Tuple
import math
import numpy as np
import pandas as pd

from sadc_fortaleza.config import (
    ESTACOES_FORTALEZA,
    PONTOS_CRITICOS,
)


def _distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância aproximada em km para a latitude de Fortaleza (-3.75°)."""
    dlat = (lat2 - lat1) * 110.574
    dlon = (lon2 - lon1) * 111.320 * math.cos(math.radians(-3.75))
    return math.sqrt(dlat * dlat + dlon * dlon)


def gerar_dados_brutos_fortaleza(
    inicio: datetime = datetime(2024, 2, 1, 0, 0),
    dias: int = 28,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Gera 3 DataFrames em resolução de 10 minutos:
    1. df_estacoes_bruto: Leituras de todas as estações com anomalias de telemetria injetadas.
    2. df_mare_meteo: Série de maré no Mucuripe, vento, pressão e previsão Nowcast (radar/satélite).
    3. df_observacoes_campo: Câmeras PMPU, chamados 40199, estado de obstrução e desfecho real por Ponto Crítico.
    """
    rng = np.random.default_rng(seed)
    n_steps = dias * 24 * 6  # 4032 passos de 10 minutos
    timestamps = [inicio + timedelta(minutes=10 * k) for k in range(n_steps)]

    # 1. Simular sistemas meteorológicos passando sobre Fortaleza (distribuídos uniformemente nos 28 dias)
    eventos_chuva = []
    n_eventos = 36
    espacamento = (n_steps - 120) // n_eventos
    coordenadas_foco = [
        (-3.7212, -38.5448),  # Jacarecanga
        (-3.7388, -38.5855),  # Padre Andrade
        (-3.7345, -38.5042),  # Aldeota
        (-3.7662, -38.5515),  # Itaoca
        (-3.7675, -38.5115),  # Aerolândia / Lagamar
        (-3.7450, -38.5350),  # Centro-Sul Fortaleza
    ]

    for ev_idx in range(n_eventos):
        base_step = 60 + ev_idx * espacamento + int(rng.integers(-18, 19))
        centro_step = int(np.clip(base_step, 36, n_steps - 48))
        duracao_steps = int(rng.integers(6, 22))  # 1h a 3.5h
        pico_mm_10m = float(
            rng.choice(
                [4.2, 6.0, 7.8, 9.6, 11.4, 13.2, 15.0],
                p=[0.15, 0.18, 0.22, 0.18, 0.14, 0.08, 0.05],
            )
        )
        lat_base, lon_base = coordenadas_foco[ev_idx % len(coordenadas_foco)]
        lat_centro = float(lat_base + rng.uniform(-0.015, 0.015))
        lon_centro = float(lon_base + rng.uniform(-0.015, 0.015))
        raio_km = float(rng.uniform(5.5, 11.5))
        vel_lat = float(rng.uniform(-0.0010, 0.0010))
        vel_lon = float(rng.uniform(-0.0025, -0.0004))
        eventos_chuva.append(
            {
                "inicio": centro_step - duracao_steps // 2,
                "fim": centro_step + duracao_steps // 2,
                "centro": centro_step,
                "duracao": max(duracao_steps, 4),
                "pico_mm_10m": pico_mm_10m,
                "lat0": lat_centro,
                "lon0": lon_centro,
                "raio_km": raio_km,
                "vel_lat": vel_lat,
                "vel_lon": vel_lon,
            }
        )

    # 2. Série de Maré do Porto do Mucuripe (semidiurna M2 + S2 + efeito meteorológico)
    horas = np.arange(n_steps) / 6.0
    mare_astronomica = (
        1.65
        + 1.05 * np.sin(2 * np.pi * horas / 12.4206 + 0.4)
        + 0.35 * np.cos(2 * np.pi * horas / 12.0000 - 0.8)
    )
    pressao_hpa = 1011.5 - 2.2 * np.sin(2 * np.pi * horas / 24.0) + rng.normal(0, 0.4, n_steps)
    vento_kmh = np.clip(
        18.0 + 6.0 * np.sin(2 * np.pi * horas / 24.0 - 1.0) + rng.normal(0, 2.5, n_steps),
        3.0,
        55.0,
    )
    mare_total = np.clip(
        mare_astronomica + 0.08 * (1012.0 - pressao_hpa) + 0.005 * vento_kmh,
        0.1,
        3.35,
    )
    gradiente_mare_m_h = np.gradient(mare_total) * 6.0

    df_mare_meteo = pd.DataFrame(
        {
            "timestamp": timestamps,
            "altura_mare_m": np.round(mare_total, 3),
            "gradiente_mare_m_h": np.round(gradiente_mare_m_h, 3),
            "fase_mare": np.where(gradiente_mare_m_h >= 0, "ENCHENTE", "VAZANTE"),
            "pressao_hpa": np.round(pressao_hpa, 2),
            "vento_kmh": np.round(vento_kmh, 2),
        }
    )

    def calcular_chuva_campo_verdadeiro(lat: float, lon: float) -> np.ndarray:
        serie = np.zeros(n_steps, dtype=float)
        for ev in eventos_chuva:
            s_ini = max(0, ev["inicio"])
            s_fim = min(n_steps - 1, ev["fim"])
            for t in range(s_ini, s_fim + 1):
                dt_c = t - ev["centro"]
                sigma_t = ev["duracao"] / 3.0 if dt_c < 0 else ev["duracao"] / 2.2
                fator_t = math.exp(-0.5 * (dt_c / max(sigma_t, 1.0)) ** 2)
                lat_t = ev["lat0"] + ev["vel_lat"] * dt_c
                lon_t = ev["lon0"] + ev["vel_lon"] * dt_c
                dist = _distancia_km(lat, lon, lat_t, lon_t)
                fator_espacial = math.exp(-0.5 * (dist / ev["raio_km"]) ** 2)
                serie[t] += ev["pico_mm_10m"] * fator_t * fator_espacial
        ruido = rng.normal(0.0, 0.12, n_steps)
        serie = np.where(serie > 0.15, np.clip(serie + ruido, 0.0, None), 0.0)
        return np.round(serie, 2)

    # 3. Gerar leituras das estações meteorológicas com falhas realistas de telemetria
    registros_estacoes = []
    for est in ESTACOES_FORTALEZA:
        chuva_real = calcular_chuva_campo_verdadeiro(est.latitude, est.longitude)
        chuva_lida = chuva_real.copy()
        status_telemetria = np.array(["OK"] * n_steps, dtype=object)

        idx_neg = rng.choice(n_steps, size=4, replace=False)
        chuva_lida[idx_neg] = -1.5
        status_telemetria[idx_neg] = "ERRO_NEGATIVO"

        idx_spike = rng.choice(n_steps, size=3, replace=False)
        chuva_lida[idx_spike] = 98.4
        status_telemetria[idx_spike] = "ERRO_SPIKE"

        inicio_offline = int(rng.integers(100, n_steps - 50))
        chuva_lida[inicio_offline : inicio_offline + 12] = np.nan
        status_telemetria[inicio_offline : inicio_offline + 12] = "OFFLINE"

        for t_idx in range(n_steps):
            registros_estacoes.append(
                {
                    "timestamp": timestamps[t_idx],
                    "id_estacao": est.id_estacao,
                    "orgao": est.orgao,
                    "bairro": est.bairro,
                    "latitude": est.latitude,
                    "longitude": est.longitude,
                    "chuva_mm_10m_bruta": chuva_lida[t_idx],
                    "chuva_mm_10m_real_referencia": chuva_real[t_idx],
                    "status_sensor_origem": status_telemetria[t_idx],
                }
            )

    df_estacoes_bruto = pd.DataFrame(registros_estacoes)

    # 4. Simular a resposta física real de cada Ponto Crítico (Ground Truth, Câmeras PMPU e 40199)
    registros_campo = []
    for pc in PONTOS_CRITICOS:
        chuva_pc = calcular_chuva_campo_verdadeiro(pc.latitude, pc.longitude)
        s_chuva = pd.Series(chuva_pc)

        chuva_30m = s_chuva.rolling(3, min_periods=1).sum().to_numpy()
        chuva_1h = s_chuva.rolling(6, min_periods=1).sum().to_numpy()
        chuva_3h = s_chuva.rolling(18, min_periods=1).sum().to_numpy()
        chuva_24h = s_chuva.rolling(144, min_periods=1).sum().to_numpy()

        chuva_futura_30m_real = s_chuva.shift(-3, fill_value=0.0).rolling(3, min_periods=1).sum().to_numpy()
        chuva_futura_60m_real = s_chuva.shift(-6, fill_value=0.0).rolling(6, min_periods=1).sum().to_numpy()
        chuva_futura_180m_real = s_chuva.shift(-18, fill_value=0.0).rolling(18, min_periods=1).sum().to_numpy()

        nowcast_30m = np.clip(chuva_futura_30m_real * rng.normal(1.0, 0.14, n_steps) + rng.normal(0, 0.35, n_steps), 0.0, None)
        nowcast_60m = np.clip(chuva_futura_60m_real * rng.normal(1.0, 0.15, n_steps) + rng.normal(0, 0.55, n_steps), 0.0, None)
        nowcast_180m = np.clip(chuva_futura_180m_real * rng.normal(1.0, 0.18, n_steps) + rng.normal(0, 0.90, n_steps), 0.0, None)

        obstrucao_observada = np.clip(
            pc.obstrucao_base_frac + 0.05 * np.sin(2 * np.pi * horas / (24.0 * 7.0)) + rng.normal(0, 0.015, n_steps),
            0.05,
            0.60,
        )
        choque_obstrucao_oculto = rng.normal(0.0, 0.06, n_steps)
        obstrucao_real_efetiva = np.clip(obstrucao_observada + choque_obstrucao_oculto, 0.05, 0.72)

        capacidade_efetiva_1h = pc.capacidade_drenagem_mm_h * (1.0 - obstrucao_real_efetiva)

        fator_bloqueio_mare = (
            pc.influencia_mare
            * np.clip((mare_total - 1.75) / 1.30, 0.0, 1.0)
            * np.where(gradiente_mare_m_h > 0, 1.30, 0.85)
        )
        capacidade_ajustada_mare = capacidade_efetiva_1h * np.clip(1.0 - 0.50 * fator_bloqueio_mare, 0.32, 1.0)

        chuva_ativa_fator = np.clip(chuva_1h / 6.0, 0.0, 1.0)
        excesso_curto = np.maximum(0.0, (chuva_30m * 1.95) - 0.78 * capacidade_ajustada_mare)
        excesso_1h = np.maximum(0.0, chuva_1h - 0.82 * capacidade_ajustada_mare)
        excesso_bacia = chuva_ativa_fator * np.maximum(
            0.0, (chuva_3h * 0.48 + chuva_24h * 0.10) - 0.88 * capacidade_ajustada_mare
        )

        fator_topo = (1.18 / (0.38 + pc.declividade_pct)) * (0.65 + 0.52 * pc.impermeabilizacao_frac)
        ruido_hidraulico = rng.normal(0.0, 2.2, n_steps) * chuva_ativa_fator

        lamina_instantanea = np.maximum(
            0.0,
            fator_topo * (0.80 * excesso_curto + 0.90 * excesso_1h + 0.55 * excesso_bacia) + ruido_hidraulico,
        )

        lamina_agua_cm = np.zeros(n_steps, dtype=float)
        recessao = 0.58 if pc.declividade_pct < 0.7 else 0.42
        for t_idx in range(n_steps):
            anterior = lamina_agua_cm[t_idx - 1] if t_idx > 0 else 0.0
            lamina_agua_cm[t_idx] = max(0.0, recessao * anterior + 0.65 * lamina_instantanea[t_idx])

        alagamento_real = (lamina_agua_cm >= 15.0).astype(int)
        confirmacao_camera_pmpu = (lamina_agua_cm >= 15.0).astype(int)

        chamados_40199 = np.where(
            alagamento_real == 1,
            rng.poisson(lam=3.2, size=n_steps) + 1,
            rng.choice([0, 1], size=n_steps, p=[0.975, 0.025]),
        )

        for t_idx in range(n_steps):
            registros_campo.append(
                {
                    "timestamp": timestamps[t_idx],
                    "id_ponto": pc.id_ponto,
                    "bairro": pc.bairro,
                    "eh_piloto": pc.eh_piloto,
                    "obstrucao_drenagem_frac": round(float(obstrucao_observada[t_idx]), 3),
                    "nowcast_radar_30m_mm": round(float(nowcast_30m[t_idx]), 2),
                    "nowcast_radar_60m_mm": round(float(nowcast_60m[t_idx]), 2),
                    "nowcast_radar_180m_mm": round(float(nowcast_180m[t_idx]), 2),
                    "lamina_agua_cm": round(float(lamina_agua_cm[t_idx]), 2),
                    "confirmacao_camera_pmpu": int(confirmacao_camera_pmpu[t_idx]),
                    "chamados_40199_1h": int(chamados_40199[t_idx]),
                    "alagamento_confirmado": int(alagamento_real[t_idx]),
                }
            )

    df_observacoes_campo = pd.DataFrame(registros_campo)
    return df_estacoes_bruto, df_mare_meteo, df_observacoes_campo
