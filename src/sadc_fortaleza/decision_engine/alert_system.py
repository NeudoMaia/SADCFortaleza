"""
Motor Operacional de Decisão, Despacho Multi-Órgãos e Retroalimentação Obrigatória (Feedback Loop).
Classifica cada Ponto Crítico nos níveis:
NORMAL -> VIGILANCIA -> ATENCAO -> ALERTA -> ALARME
e registra obrigatoriamente o desfecho operacional para melhoria contínua dos modelos.
"""

from typing import Dict, List
import pandas as pd

from sadc_fortaleza.config import PONTOS_CRITICOS, PROTOCOLOS_OPERACIONAIS


def determinar_nivel_operacional_linha(
    row: pd.Series,
    limiar_ponto_nivel2: float,
    limiar_nivel3_60m: float,
    limiar_chuva_1h_historico: float,
) -> str:
    """
    Aplica a árvore de decisão operacional combinando Nível 1 (Suscetibilidade),
    Nível 2 (Probabilidade em Tempo Real), Nível 3 (Antecipação 60m) e Confirmação (Câmeras PMPU / 40199).
    """
    prob_rt = float(row["prob_alagamento_tempo_real"])
    prob_60m = float(row["prob_alagamento_proximos_60m"])
    chuva_1h = float(row["chuva_1h_mm"])
    nowcast_60m = float(row["nowcast_radar_60m_mm"])
    nowcast_180m = float(row["nowcast_radar_180m_mm"])
    cam_conf = int(row["confirmacao_camera_pmpu"])
    chamados = int(row["chamados_40199_1h"])
    susc_ord = int(row["classe_suscetibilidade_ord"])

    # 1. ALARME: Limiar crítico atingido E confirmação visual PMPU ou múltiplos relatos 40199
    if (prob_rt >= limiar_ponto_nivel2 or chuva_1h >= limiar_chuva_1h_historico) and (
        cam_conf == 1 or chamados >= 2
    ):
        return "ALARME"

    # 2. ALERTA: Probabilidade em tempo real ou de curto prazo (60m) acima do limiar calibrado
    if prob_rt >= limiar_ponto_nivel2 or prob_60m >= limiar_nivel3_60m:
        return "ALERTA"

    # 3. ATENCAO: Chuva acumulada aproximando-se (>= 65%) do limiar histórico do ponto ou prob moderada
    if (
        chuva_1h >= 0.65 * limiar_chuva_1h_historico
        or prob_rt >= 0.55 * limiar_ponto_nivel2
        or prob_60m >= 0.65 * limiar_nivel3_60m
    ):
        return "ATENCAO"

    # 4. VIGILANCIA: Previsão de chuva significativa em área de suscetibilidade Alta ou Muito Alta
    if susc_ord >= 3 and (nowcast_60m >= 8.0 or nowcast_180m >= 15.0 or chuva_1h >= 5.0):
        return "VIGILANCIA"

    return "NORMAL"


def aplicar_motor_decisao_e_retroalimentacao(
    df_predito: pd.DataFrame,
    mapa_suscetibilidade: Dict[str, Dict[str, object]],
    limiares_nivel2: Dict[str, float],
    limiar_nivel3_60m: float,
) -> Dict[str, object]:
    """
    Aplica a classificação operacional a toda a série temporal e gera o Livro de Auditoria
    e Retroalimentação Obrigatória (Feedback Loop) exigido pelas diretrizes do SADC-Fortaleza.
    """
    df = df_predito.copy()
    niveis = []

    for _, row in df.iterrows():
        id_p = str(row["id_ponto"])
        lim_n2 = float(limiares_nivel2.get(id_p, limiares_nivel2.get("GLOBAL", 0.45)))
        lim_1h = float(mapa_suscetibilidade[id_p]["limiares_chuva_mm"]["1h"])
        nivel = determinar_nivel_operacional_linha(
            row=row,
            limiar_ponto_nivel2=lim_n2,
            limiar_nivel3_60m=limiar_nivel3_60m,
            limiar_chuva_1h_historico=lim_1h,
        )
        niveis.append(nivel)

    df["nivel_alerta_operacional"] = niveis

    # Gerar registros de Retroalimentação Obrigatória para todos os alertas emitidos (ALERTA e ALARME)
    df_alertas = df[df["nivel_alerta_operacional"].isin(["ALERTA", "ALARME"])].copy()

    registros_feedback: List[Dict[str, object]] = []
    for _, row in df_alertas.iterrows():
        id_p = str(row["id_ponto"])
        real_pos = int(row["target_alagamento_presente"]) == 1
        prox_60m_pos = int(row["target_alagamento_proximos_60m"]) == 1
        cam_ok = int(row["confirmacao_camera_pmpu"]) == 1
        chamados = int(row["chamados_40199_1h"])

        if real_pos or cam_ok:
            status_retro = "CONFIRMADO_POSITIVO_EM_CAMPO"
            acao_pos_evento = "Manter calibração do ponto; registrar mancha de inundação no Observatório."
        elif prox_60m_pos:
            status_retro = "CONFIRMADO_ANTECIPACAO_PREVENTIVA"
            acao_pos_evento = "Alerta preventivo validado dentro da janela de Lead Time (30-60 min)."
        else:
            status_retro = "FALSO_POSITIVO_ENCAMINHADO_VISTORIA"
            acao_pos_evento = (
                "Câmera sem lâmina crítica; verificar se houve limpeza recente de boca de lobo "
                "e atualizar fator de obstrução da microbacia."
            )

        proto = PROTOCOLOS_OPERACIONAIS[str(row["nivel_alerta_operacional"])]
        registros_feedback.append(
            {
                "timestamp": str(row["timestamp"]),
                "id_ponto": id_p,
                "bairro": str(row["bairro"]),
                "nivel_emitido": str(row["nivel_alerta_operacional"]),
                "prob_tempo_real": round(float(row["prob_alagamento_tempo_real"]), 3),
                "prob_antecipacao_60m": round(float(row["prob_alagamento_proximos_60m"]), 3),
                "chuva_1h_mm": round(float(row["chuva_1h_mm"]), 1),
                "altura_mare_m": round(float(row["altura_mare_m"]), 2),
                "cameras_acionadas": mapa_suscetibilidade[id_p]["cameras_pmpu"],
                "confirmacao_camera_pmpu": cam_ok,
                "chamados_40199_1h": chamados,
                "orgaos_notificados": proto.orgaos_acionados,
                "status_retroalimentacao_obrigatoria": status_retro,
                "encaminhamento_engenharia_modelo": acao_pos_evento,
            }
        )

    contagem_niveis = df["nivel_alerta_operacional"].value_counts().to_dict()
    contagem_feedback = (
        pd.Series([r["status_retroalimentacao_obrigatoria"] for r in registros_feedback])
        .value_counts()
        .to_dict()
        if registros_feedback
        else {}
    )

    return {
        "df_operacional": df,
        "distribuicao_niveis_operacionais": {k: int(v) for k, v in contagem_niveis.items()},
        "total_alertas_auditados_feedback": len(registros_feedback),
        "resumo_retroalimentacao": {k: int(v) for k, v in contagem_feedback.items()},
        "amostra_logs_retroalimentacao": registros_feedback[-25:],  # últimos 25 eventos auditados
    }
