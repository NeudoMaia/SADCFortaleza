"""
Módulo de Controle de Qualidade (QC) de Telemetria Pluviométrica e Interpolação Espacial (IDW).
Segue rigorosamente as práticas de integridade de dados:
1. Identifica, contabiliza e classifica leituras anômalas (negativas, picos irreais > 60mm/10min) e valores ausentes (estações offline).
2. Substitui leituras corrompidas por NaN antes da interpolação espacial para impedir contaminação da malha.
3. Cria variáveis indicadoras explícitas de falha/ausência de telemetria (missingness features) por ponto crítico.
4. Executa Interpolação Espacial Ponderada pelo Inverso da Distância (IDW, p=2.0) garantindo 100% de cobertura nas áreas de risco.
"""

from typing import Dict, List, Tuple
import math
import numpy as np
import pandas as pd

from sadc_fortaleza.config import ESTACOES_FORTALEZA, PONTOS_CRITICOS, PontoCritico


LIMITE_MAX_FISICO_MM_10M = 60.0  # > 360 mm/h contínuo por 10min é erro de básculo/telemetria


def _distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = (lat2 - lat1) * 110.574
    dlon = (lon2 - lon1) * 111.320 * math.cos(math.radians(-3.75))
    return math.sqrt(dlat * dlat + dlon * dlon)


def executar_controle_qualidade_estacoes(
    df_estacoes_bruto: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """
    Analisa e trata falhas de telemetria nas estações meteorológicas.
    Retorna o DataFrame saneado e o relatório detalhado de auditoria de qualidade (QC).
    """
    df = df_estacoes_bruto.copy()
    total_leituras = len(df)

    mask_ausente = df["chuva_mm_10m_bruta"].isna()
    mask_negativo = (~mask_ausente) & (df["chuva_mm_10m_bruta"] < 0.0)
    mask_spike = (~mask_ausente) & (df["chuva_mm_10m_bruta"] > LIMITE_MAX_FISICO_MM_10M)

    n_ausentes = int(mask_ausente.sum())
    n_negativos = int(mask_negativo.sum())
    n_spikes = int(mask_spike.sum())
    n_validas = int(total_leituras - n_ausentes - n_negativos - n_spikes)

    df["flag_qc_status"] = "VALIDA"
    df.loc[mask_ausente, "flag_qc_status"] = "OFFLINE_NULL"
    df.loc[mask_negativo, "flag_qc_status"] = "REJEITADA_NEGATIVA"
    df.loc[mask_spike, "flag_qc_status"] = "REJEITADA_SPIKE_IRREAL"

    # Leituras inválidas tornam-se NaN para serem imputadas espacialmente pelas estações vizinhas via IDW
    df["chuva_mm_10m_qc"] = df["chuva_mm_10m_bruta"]
    df.loc[mask_negativo | mask_spike, "chuva_mm_10m_qc"] = np.nan

    relatorio_qc = {
        "total_leituras_avaliadas": total_leituras,
        "leituras_validas": n_validas,
        "percentual_validas": round(100.0 * n_validas / max(total_leituras, 1), 3),
        "anomalias_detectadas": {
            "offline_null_count": n_ausentes,
            "offline_null_pct": round(100.0 * n_ausentes / max(total_leituras, 1), 3),
            "valores_negativos_count": n_negativos,
            "picos_irreais_spike_count": n_spikes,
        },
        "decisao_tratamento": (
            "Leituras negativas (< 0 mm) e spikes irreais (> 60 mm/10min) são convertidos em NaN "
            "para não distorcer a malha. Em seguida, a série em cada Ponto Crítico é reconstruída "
            "por interpolação espacial IDW (p=2) usando as estações ativas no mesmo instante, "
            "preservando uma feature binária (estacao_primaria_offline_flag) para informar o modelo de ML."
        ),
    }

    return df, relatorio_qc


def interpolar_chuva_idw_para_pontos_criticos(
    df_estacoes_qc: pd.DataFrame,
    pontos: List[PontoCritico] = PONTOS_CRITICOS,
    potencia_idw: float = 2.0,
) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """
    Executa interpolação espacial IDW das estações ativas para cada Ponto Crítico.
    Calcula também indicadores de cobertura e incerteza espacial.
    """
    # Matriz de leitura: linhas = timestamps, colunas = id_estacao
    tabela_chuva = df_estacoes_qc.pivot(
        index="timestamp", columns="id_estacao", values="chuva_mm_10m_qc"
    ).sort_index()

    estacoes_ordenadas = [est for est in ESTACOES_FORTALEZA if est.id_estacao in tabela_chuva.columns]
    ids_estacoes = [est.id_estacao for est in estacoes_ordenadas]
    matriz_valores = tabela_chuva[ids_estacoes].to_numpy(dtype=float)  # (T, N_est)
    matriz_valida = ~np.isnan(matriz_valores)  # (T, N_est)

    frames_pontos = []
    resumo_cobertura_por_ponto = {}

    for pc in pontos:
        # Distâncias de todas as estações ao ponto crítico (em km, mínimo de 0.15 km para evitar singularidade)
        distancias = np.array(
            [
                max(_distancia_km(pc.latitude, pc.longitude, est.latitude, est.longitude), 0.15)
                for est in estacoes_ordenadas
            ],
            dtype=float,
        )
        idx_mais_proxima = int(np.argmin(distancias))
        pesos_base = 1.0 / (distancias ** potencia_idw)  # (N_est,)

        # Pesos ativos em cada timestamp (zera estações com NaN/Offline no instante t)
        pesos_ativos = np.where(matriz_valida, pesos_base[None, :], 0.0)
        soma_pesos = pesos_ativos.sum(axis=1)

        valores_zerados = np.where(matriz_valida, matriz_valores, 0.0)
        chuva_idw = np.divide(
            (valores_zerados * pesos_ativos).sum(axis=1),
            soma_pesos,
            out=np.zeros_like(soma_pesos),
            where=soma_pesos > 0,
        )

        # Indicadores de incerteza espacial e disponibilidade de telemetria
        estacao_primaria_offline = (~matriz_valida[:, idx_mais_proxima]).astype(int)

        # Distância até a estação ativa mais próxima em cada timestamp
        dist_matriz = np.where(matriz_valida, distancias[None, :], 999.0)
        dist_ativa_min_km = dist_matriz.min(axis=1)

        # Quantidade de estações operantes em um raio de 8 km
        dentro_8km = distancias <= 8.0
        num_ativas_8km = (matriz_valida & dentro_8km[None, :]).sum(axis=1)

        df_pc = pd.DataFrame(
            {
                "timestamp": tabela_chuva.index,
                "id_ponto": pc.id_ponto,
                "chuva_idw_10m_mm": np.round(chuva_idw, 3),
                "estacao_primaria_id": ids_estacoes[idx_mais_proxima],
                "estacao_primaria_offline_flag": estacao_primaria_offline,
                "dist_estacao_ativa_min_km": np.round(dist_ativa_min_km, 3),
                "num_estacoes_ativas_8km": num_ativas_8km.astype(int),
            }
        )
        frames_pontos.append(df_pc)

        cobertura_confiavel_pct = float(np.mean(dist_ativa_min_km <= 8.0) * 100.0)
        resumo_cobertura_por_ponto[pc.id_ponto] = {
            "nome": pc.nome,
            "bairro": pc.bairro,
            "estacao_primaria": ids_estacoes[idx_mais_proxima],
            "distancia_estacao_primaria_km": round(float(distancias[idx_mais_proxima]), 2),
            "cobertura_confiavel_pct": round(cobertura_confiavel_pct, 2),
            "steps_interpolados_por_redundancia": int(estacao_primaria_offline.sum()),
        }

    df_interpolado = pd.concat(frames_pontos, ignore_index=True)
    cobertura_global = all(
        v["cobertura_confiavel_pct"] >= 99.9 for v in resumo_cobertura_por_ponto.values()
    )

    relatorio_espacial = {
        "metodo": f"Inverse Distance Weighting (IDW, p={potencia_idw})",
        "cobertura_100pct_areas_risco": cobertura_global,
        "detalhe_por_ponto": resumo_cobertura_por_ponto,
    }

    return df_interpolado, relatorio_espacial
