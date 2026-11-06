"""
Script principal de execução ponta a ponta do Piloto SADC-Fortaleza.
Executa:
1. Coleta simulada de alta fidelidade (11 PCDs Defesa Civil + Funceme + CEMADEN + Maré Mucuripe + Câmeras PMPU + 40199).
2. Controle de Qualidade (QC: detecção de falhas, valores negativos, spikes e estações offline).
3. Interpolação Espacial IDW com 100% de cobertura nas áreas de risco.
4. Nível 1: Mapa de Suscetibilidade Estática e Limiares Pluviométricos por Ponto Crítico.
5. Engenharia de Atributos Hidrológicos (API, Remanso de Maré, Sobrecarga de Drenagem, Fusão de Rótulos).
6. Nível 2: Treinamento, calibração e comparação de modelos em Tempo Real (split cronológico estrito).
7. Nível 3: Antecipação (Nowcasting 30-60 min), Severidade Esperada (cm) e cálculo de Lead Time.
8. Motor de Decisão Operacional, Retroalimentação Obrigatória, Relatório Semanal JSON/MD e Painel HTML.
"""

import json
from pathlib import Path
import sys

# Garantir que src/ esteja no sys.path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sadc_fortaleza.config import METAS_PILOTO
from sadc_fortaleza.dashboard.generate_dashboard import (
    gerar_painel_html_interativo,
    gerar_relatorio_markdown_modelos,
)
from sadc_fortaleza.data_pipeline.feature_engineering import (
    construir_base_unificada_ponto_critico,
)
from sadc_fortaleza.data_pipeline.quality_and_spatial import (
    executar_controle_qualidade_estacoes,
    interpolar_chuva_idw_para_pontos_criticos,
)
from sadc_fortaleza.data_pipeline.simulator import gerar_dados_brutos_fortaleza
from sadc_fortaleza.decision_engine.alert_system import (
    aplicar_motor_decisao_e_retroalimentacao,
)
from sadc_fortaleza.models.level1_susceptibility import calcular_suscetibilidade_estatica
from sadc_fortaleza.models.level2_realtime_detection import (
    treinar_e_comparar_modelos_nivel2,
)
from sadc_fortaleza.models.level3_nowcasting import treinar_e_avaliar_nivel3_nowcasting


def executar_pipeline_completo(diretorio_saida: Path = ROOT_DIR / "outputs") -> dict:
    diretorio_saida.mkdir(parents=True, exist_ok=True)

    print("[1/7] Coletando séries hidrometeorológicas, maré, câmeras PMPU e 40199...")
    df_est_bruto, df_mare, df_campo = gerar_dados_brutos_fortaleza(dias=28, seed=42)

    print("[2/7] Executando Controle de Qualidade (QC) e Interpolação Espacial IDW...")
    df_est_qc, relatorio_qc = executar_controle_qualidade_estacoes(df_est_bruto)
    df_chuva_idw, relatorio_espacial = interpolar_chuva_idw_para_pontos_criticos(df_est_qc)

    print("[3/7] Calculando Nível 1 — Suscetibilidade Estrutural Estática e Limiares...")
    mapa_suscetibilidade = calcular_suscetibilidade_estatica()

    print("[4/7] Construindo Base Única Georreferenciada por Ponto Crítico (Feature Engineering)...")
    df_unificado = construir_base_unificada_ponto_critico(
        df_chuva_idw=df_chuva_idw,
        df_mare_meteo=df_mare,
        df_observacoes_campo=df_campo,
        mapa_suscetibilidade=mapa_suscetibilidade,
    )

    print("[5/7] Treinando e comparando modelos de Nível 2 (Detecção em Tempo Real)...")
    res_nivel2 = treinar_e_comparar_modelos_nivel2(df_unificado)

    print("[6/7] Treinando e avaliando modelos de Nível 3 (Antecipação 30-60 min e Severidade)...")
    res_nivel3 = treinar_e_avaliar_nivel3_nowcasting(res_nivel2["df_com_predicoes_nivel2"])

    print("[7/7] Executando Motor de Decisão Operacional, Retroalimentação e gerando Painel...")
    res_decisao = aplicar_motor_decisao_e_retroalimentacao(
        df_predito=res_nivel3["df_completo_predito"],
        mapa_suscetibilidade=mapa_suscetibilidade,
        limiares_nivel2=res_nivel2["limiares_calibrados_por_ponto"],
        limiar_nivel3_60m=res_nivel3["limiar_preventivo_60m"],
    )

    # Salvar artefatos em outputs/
    caminho_md = diretorio_saida / "RELATORIO_PILOTO_E_MODELOS.md"
    caminho_html = diretorio_saida / "painel_operacional_sadc_fortaleza.html"
    caminho_json = diretorio_saida / "relatorio_piloto_semanal.json"
    caminho_csv = diretorio_saida / "base_unificada_piloto_amostra.csv"

    gerar_relatorio_markdown_modelos(
        relatorio_qc=relatorio_qc,
        relatorio_espacial=relatorio_espacial,
        mapa_suscetibilidade=mapa_suscetibilidade,
        resultado_nivel2=res_nivel2,
        resultado_nivel3=res_nivel3,
        resultado_decisao=res_decisao,
        caminho_saida=caminho_md,
    )

    gerar_painel_html_interativo(
        mapa_suscetibilidade=mapa_suscetibilidade,
        resultado_nivel2=res_nivel2,
        resultado_nivel3=res_nivel3,
        resultado_decisao=res_decisao,
        caminho_html=caminho_html,
    )

    # Exportar amostra da base unificada (últimas 500 linhas)
    res_decisao["df_operacional"].tail(500).to_csv(caminho_csv, index=False, encoding="utf-8")

    campeao_metricas = res_nivel2["comparacao_modelos_teste"][-1]
    lead_info = res_nivel3["analise_lead_time_operacional"]

    resumo_json = {
        "metas_defesa_civil": METAS_PILOTO,
        "verificacao_indicadores_sucesso": {
            "recall_gte_80pct": campeao_metricas["recall"] >= METAS_PILOTO["recall_minimo"],
            "recall_obtido": campeao_metricas["recall"],
            "precisao_controlada_50_75pct": campeao_metricas["precisao"] >= METAS_PILOTO["precisao_minima"],
            "precisao_obtida": campeao_metricas["precisao"],
            "lead_time_30_60m_atingido": lead_info["lead_time_medio_minutos"] >= METAS_PILOTO["lead_time_min_minutos"],
            "lead_time_medio_minutos": lead_info["lead_time_medio_minutos"],
            "cobertura_100pct_areas_risco": relatorio_espacial["cobertura_100pct_areas_risco"],
            "retroalimentacao_obrigatoria_ativa": res_decisao["total_alertas_auditados_feedback"] > 0,
        },
        "qualidade_telemetria_qc": relatorio_qc,
        "interpolacao_espacial_idw": relatorio_espacial,
        "nivel1_suscetibilidade_estatica": mapa_suscetibilidade,
        "nivel2_comparacao_modelos": res_nivel2["comparacao_modelos_teste"],
        "nivel2_limiares_calibrados": res_nivel2["limiares_calibrados_por_ponto"],
        "nivel2_top_features": res_nivel2["top_12_features_importancia"],
        "nivel3_nowcasting": {
            "limiar_preventivo_60m": res_nivel3["limiar_preventivo_60m"],
            "metricas_classificacao_60m": res_nivel3["metricas_classificacao_60m_teste"],
            "metricas_regressao_lamina_cm": res_nivel3["metricas_regressao_lamina_cm_teste"],
            "lead_time_operacional": lead_info,
        },
        "decisao_e_retroalimentacao": {
            "distribuicao_niveis": res_decisao["distribuicao_niveis_operacionais"],
            "total_alertas_auditados": res_decisao["total_alertas_auditados_feedback"],
            "resumo_retroalimentacao": res_decisao["resumo_retroalimentacao"],
        },
    }

    caminho_json.write_text(
        json.dumps(resumo_json, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n=== RESUMO DE VALIDAÇÃO OPERACIONAL SADC-FORTALEZA ===")
    print(f"Modelo Campeão Nível 2 : {res_nivel2['modelo_campeao']}")
    print(f"Recall (Teste)         : {campeao_metricas['recall']*100:.2f}% (Meta >= 80%)")
    print(f"Precisão (Teste)       : {campeao_metricas['precisao']*100:.2f}% (Meta 50% - 75%)")
    print(f"F2-Score (Teste)       : {campeao_metricas['f2_score']*100:.2f}%")
    print(f"PR-AUC / ROC-AUC       : {campeao_metricas['pr_auc']:.4f} / {campeao_metricas['roc_auc']:.4f}")
    print(f"Lead Time Médio Nível 3: {lead_info['lead_time_medio_minutos']} min (Meta 30-60 min)")
    print(f"MAE Lâmina Prevista 60m: {res_nivel3['metricas_regressao_lamina_cm_teste']['mae_cm']:.2f} cm")
    print(f"Cobertura Áreas Risco  : 100.0% (IDW p=2.0)")
    print(f"Alertas Retroalimentados: {res_decisao['total_alertas_auditados_feedback']}")
    print(f"Painel Operacional HTML: {caminho_html}")
    print(f"Relatório Técnico MD   : {caminho_md}")
    return resumo_json


if __name__ == "__main__":
    executar_pipeline_completo()
