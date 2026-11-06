"""
Engenharia de Atributos Hidrológicos, Oceanográficos e Fusão de Rótulos (Ground Truth)
para o SADC-Fortaleza.
Implementa as melhorias propostas sobre o planejamento inicial:
- Acumulados multi-escala (10m, 30m, 1h, 3h, 6h, 12h, 24h) e Intensidade Máxima Equivalente (15m/30m).
- Antecedent Precipitation Index (API) com fator de decaimento específico da microbacia.
- Índice de Bloqueio Hidráulico de Maré (Remanso Costeiro = Maré x Gradiente x Cota x Chuva 1h).
- Razão de Sobrecarga da Rede de Drenagem (Intensidade vs Capacidade Efetiva Desobstruída).
- Fusão de Rótulos (Câmera PMPU + Consenso de Chamados 40199) para mitigar falsos rótulos.
"""

from typing import Dict, List
import numpy as np
import pandas as pd

from sadc_fortaleza.config import PONTOS_CRITICOS, PontoCritico


def construir_base_unificada_ponto_critico(
    df_chuva_idw: pd.DataFrame,
    df_mare_meteo: pd.DataFrame,
    df_observacoes_campo: pd.DataFrame,
    mapa_suscetibilidade: Dict[str, Dict[str, object]],
    pontos: List[PontoCritico] = PONTOS_CRITICOS,
) -> pd.DataFrame:
    """
    Une todas as camadas por (id_ponto, timestamp) e calcula as features físicas e estatísticas.
    """
    catalogo_pc = {pc.id_ponto: pc for pc in pontos}

    df = (
        df_chuva_idw.merge(df_mare_meteo, on="timestamp", how="left")
        .merge(
            df_observacoes_campo,
            on=["timestamp", "id_ponto"],
            how="left",
        )
        .sort_values(["id_ponto", "timestamp"])
        .reset_index(drop=True)
    )

    grupos_processados = []

    for id_ponto, grp in df.groupby("id_ponto", sort=False):
        pc = catalogo_pc[id_ponto]
        g = grp.sort_values("timestamp").copy()
        s_chuva = g["chuva_idw_10m_mm"]

        # 1. Variáveis de Chuva Observada (múltiplas durações críticas para Fortaleza)
        g["chuva_10m_mm"] = s_chuva
        g["chuva_30m_mm"] = s_chuva.rolling(3, min_periods=1).sum()
        g["chuva_1h_mm"] = s_chuva.rolling(6, min_periods=1).sum()
        g["chuva_3h_mm"] = s_chuva.rolling(18, min_periods=1).sum()
        g["chuva_6h_mm"] = s_chuva.rolling(36, min_periods=1).sum()
        g["chuva_12h_mm"] = s_chuva.rolling(72, min_periods=1).sum()
        g["chuva_24h_mm"] = s_chuva.rolling(144, min_periods=1).sum()

        # Intensidade máxima recente em 10-20 min convertida para taxa horária equivalente (mm/h)
        pico_20m = s_chuva.rolling(2, min_periods=1).sum()
        g["intensidade_pico_15m_mm_h"] = pico_20m * 3.0
        g["aceleracao_chuva_mm"] = g["chuva_30m_mm"] - g["chuva_30m_mm"].shift(3, fill_value=0.0)

        # 2. Índice de Chuva Antecedente (API - Antecedent Precipitation Index) contínuo
        # Modela a saturação prévia do solo/lagoas/canais na microbacia
        valores_10m = s_chuva.to_numpy(dtype=float)
        api_vals = np.zeros_like(valores_10m)
        # Fator por passo de 10 min derivado do fator horário da microbacia
        k_step = pc.fator_decaimento_api ** (1.0 / 6.0)
        for idx in range(len(valores_10m)):
            prev = api_vals[idx - 1] if idx > 0 else 0.0
            api_vals[idx] = prev * k_step + valores_10m[idx]
        g["indice_chuva_antecedente_api"] = np.round(api_vals, 3)

        # 3. Atributos Estruturais do Território e Nível 1 (Suscetibilidade Estática)
        info_susc = mapa_suscetibilidade[id_ponto]
        g["cota_m"] = pc.cota_m
        g["declividade_pct"] = pc.declividade_pct
        g["impermeabilizacao_frac"] = pc.impermeabilizacao_frac
        g["dist_corpo_hidrico_m"] = pc.dist_corpo_hidrico_m
        g["capacidade_drenagem_mm_h"] = pc.capacidade_drenagem_mm_h
        g["influencia_mare_estrutural"] = pc.influencia_mare
        g["score_suscetibilidade_estatica"] = float(info_susc["score_suscetibilidade"])
        g["classe_suscetibilidade_ord"] = int(info_susc["classe_ordinal"])
        g["classe_suscetibilidade_nome"] = str(info_susc["classe_risco"])

        # 4. Hidráulica de Drenagem e Razão de Sobrecarga (IDF Local vs Rede Desobstruída)
        capacidade_efetiva = pc.capacidade_drenagem_mm_h * (1.0 - g["obstrucao_drenagem_frac"])
        g["capacidade_efetiva_drenagem_mm_h"] = np.round(capacidade_efetiva, 3)
        g["razao_sobrecarga_drenagem_1h"] = np.round(
            g["chuva_1h_mm"] / np.maximum(capacidade_efetiva, 5.0), 3
        )
        g["razao_sobrecarga_pico_15m"] = np.round(
            g["intensidade_pico_15m_mm_h"] / np.maximum(capacidade_efetiva * 1.35, 5.0), 3
        )

        # 5. Física Costeira: Índice de Bloqueio Hidráulico por Maré (Backwater / Remanso)
        # Maré acima de 1.85m em maré enchente reduz escoamento das galerias em cotas baixas
        excesso_mare = np.clip((g["altura_mare_m"] - 1.80) / 1.40, 0.0, 1.0)
        amplificador_enchente = np.where(g["gradiente_mare_m_h"] > 0, 1.25, 0.85)
        fator_cota = np.exp(-pc.cota_m / 8.0)
        g["indice_bloqueio_mare_remanso"] = np.round(
            pc.influencia_mare * excesso_mare * amplificador_enchente * fator_cota * (g["chuva_1h_mm"] / 15.0),
            4,
        )

        # 6. Fusão de Rótulos (Ground Truth Auditável: Câmeras PMPU + Chamados 40199)
        # Evita que um único chamado isolado de ruído contamine o alvo de treinamento
        consenso_confirmado = (
            (g["confirmacao_camera_pmpu"] == 1)
            | ((g["chamados_40199_1h"] >= 2) & (g["chuva_1h_mm"] >= 8.0))
            | (g["alagamento_confirmado"] == 1)
        ).astype(int)
        g["target_alagamento_presente"] = consenso_confirmado

        # 7. Rótulos de Antecipação (Nível 3 - Nowcasting: ocorrerá alagamento nos próximos 30 a 60 min?)
        # Usamos janela reversa futura apenas para criar o target supervisionado de treinamento/avaliação
        s_target_rev = g["target_alagamento_presente"].iloc[::-1]
        alagamento_prox_60m = s_target_rev.rolling(6, min_periods=1).max().iloc[::-1].astype(int)
        g["target_alagamento_proximos_60m"] = alagamento_prox_60m

        s_lamina_rev = g["lamina_agua_cm"].iloc[::-1]
        g["target_lamina_max_proximos_60m_cm"] = s_lamina_rev.rolling(6, min_periods=1).max().iloc[::-1]

        grupos_processados.append(g)

    df_unificado = pd.concat(grupos_processados, ignore_index=True)
    return df_unificado
