"""
Nível 1 — Modelo de Suscetibilidade Estrutural Estática e Limiares Históricos por Ponto Crítico.
Combina geomorfologia, drenagem, impermeabilização, distância a canais/lagoas, exposição costeira
e recorrência histórica (2021-2024) para classificar cada setor em:
BAIXO (1), MEDIO (2), ALTO (3) ou MUITO_ALTO (4).
"""

from typing import Dict, List
import math
from sadc_fortaleza.config import PONTOS_CRITICOS, PontoCritico


def calcular_suscetibilidade_estatica(
    pontos: List[PontoCritico] = PONTOS_CRITICOS,
) -> Dict[str, Dict[str, object]]:
    """
    Calcula o score composto de suscetibilidade estrutural [0, 100], a classe de risco
    e os limiares pluviométricos de referência por duração (15m, 1h, 3h, 24h) para cada Ponto Crítico.
    """
    resultados: Dict[str, Dict[str, object]] = {}

    for pc in pontos:
        # 1. Sub-score Topográfico (cota baixa e baixa declividade retêm lâmina d'água)
        score_cota = math.exp(-pc.cota_m / 18.0)  # [0, 1]
        score_declividade = 1.0 / (1.0 + 0.85 * pc.declividade_pct)  # [0, 1]
        sub_topografia = 0.55 * score_cota + 0.45 * score_declividade

        # 2. Sub-score de Drenagem e Impermeabilização
        deficit_drenagem = max(0.0, min(1.0, (45.0 - pc.capacidade_drenagem_mm_h) / 30.0))
        sub_drenagem = (
            0.45 * deficit_drenagem
            + 0.30 * pc.impermeabilizacao_frac
            + 0.25 * min(1.0, pc.obstrucao_base_frac / 0.40)
        )

        # 3. Sub-score Hidrológico e Costeiro (proximidade a canal/rio/lagoa e maré)
        score_proximidade_hidrica = math.exp(-pc.dist_corpo_hidrico_m / 120.0)
        sub_hidrico_mare = 0.70 * score_proximidade_hidrica + 0.30 * pc.influencia_mare

        # 4. Sub-score Histórico Crônico (Defesa Civil 2021-2024 + recorrência anual)
        score_ocorrencias = min(1.0, pc.ocorrencias_2021_2024 / 150.0)
        score_recorrencia = min(1.0, pc.anos_recorrencia_consecutivos / 4.0)
        sub_historico = 0.65 * score_ocorrencias + 0.35 * score_recorrencia

        # Combinação multicritério auditável (0 a 100)
        score_total = 100.0 * (
            0.25 * sub_topografia
            + 0.30 * sub_drenagem
            + 0.20 * sub_hidrico_mare
            + 0.25 * sub_historico
        )

        if score_total >= 75.0:
            classe_risco = "MUITO_ALTO"
            classe_ordinal = 4
        elif score_total >= 55.0:
            classe_risco = "ALTO"
            classe_ordinal = 3
        elif score_total >= 35.0:
            classe_risco = "MEDIO"
            classe_ordinal = 2
        else:
            classe_risco = "BAIXO"
            classe_ordinal = 1

        # Derivação de limiares pluviométricos críticos específicos do ponto por duração (mm)
        # Pontos mais vulneráveis e obstruídos atingem saturação com menor volume de chuva
        cap_efetiva = pc.capacidade_drenagem_mm_h * (1.0 - pc.obstrucao_base_frac)
        fator_vulnerabilidade = max(0.55, 1.15 - 0.006 * score_total)

        limiar_15m_mm = round(max(6.5, 0.38 * cap_efetiva * fator_vulnerabilidade), 1)
        limiar_1h_mm = round(max(15.0, 0.92 * cap_efetiva * fator_vulnerabilidade), 1)
        limiar_3h_mm = round(max(26.0, 1.55 * cap_efetiva * fator_vulnerabilidade), 1)
        limiar_24h_mm = round(max(48.0, 2.85 * cap_efetiva * fator_vulnerabilidade), 1)

        resultados[pc.id_ponto] = {
            "id_ponto": pc.id_ponto,
            "nome": pc.nome,
            "bairro": pc.bairro,
            "bacia_hidrografica": pc.bacia_hidrografica,
            "eh_piloto": pc.eh_piloto,
            "score_suscetibilidade": round(score_total, 2),
            "classe_risco": classe_risco,
            "classe_ordinal": classe_ordinal,
            "componentes": {
                "topografia": round(sub_topografia * 100, 1),
                "drenagem_impermeabilizacao": round(sub_drenagem * 100, 1),
                "hidrico_mare": round(sub_hidrico_mare * 100, 1),
                "historico_2021_2024": round(sub_historico * 100, 1),
            },
            "limiares_chuva_mm": {
                "15m": limiar_15m_mm,
                "1h": limiar_1h_mm,
                "3h": limiar_3h_mm,
                "24h": limiar_24h_mm,
            },
            "cameras_pmpu": pc.cameras_pmpu,
            "populacao_exposta_estimada": pc.populacao_exposta_estimada,
        }

    return resultados
