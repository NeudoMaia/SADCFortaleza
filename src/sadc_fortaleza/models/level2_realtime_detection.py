"""
Nível 2 — Modelo de Detecção Probabilística em Tempo Real.
Implementa rigorosamente as diretrizes de ML Best Practices:
1. Divisão cronológica estrita (Treino / Validação / Teste) ANTES de qualquer pré-processamento.
2. Pipeline sem vazamento de dados (StandardScaler para numéricas, OneHotEncoder para nominais,
   preservando variáveis já codificadas ordinalmente como classe_suscetibilidade_ord).
3. Comparação sistemática de 4 abordagens:
   - Baseline 0 (Regra Fixa Pluviométrica Municipal)
   - Fase 1: Regressão Logística Regularizada (L2 + class_weight='balanced')
   - Fase 2A: Random Forest Cost-Sensitive
   - Fase 2B (Recomendado): Ensemble Híbrido SADC (HistGradientBoosting + Random Forest + LogReg)
     com calibração de limiar específico por Ponto Crítico maximizando F2-Score (Recall >= 80% e Precisão 50%-75%).
4. Intervalos de confiança de 95% via Bootstrap, Matriz de Confusão e Análise de Erro por Bairro-Piloto (Slice Analysis).
"""

import os

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


FEATURES_NUMERICAS_NIVEL2 = [
    "chuva_10m_mm",
    "chuva_30m_mm",
    "chuva_1h_mm",
    "chuva_3h_mm",
    "chuva_6h_mm",
    "chuva_12h_mm",
    "chuva_24h_mm",
    "intensidade_pico_15m_mm_h",
    "aceleracao_chuva_mm",
    "indice_chuva_antecedente_api",
    "altura_mare_m",
    "gradiente_mare_m_h",
    "indice_bloqueio_mare_remanso",
    "obstrucao_drenagem_frac",
    "capacidade_efetiva_drenagem_mm_h",
    "razao_sobrecarga_drenagem_1h",
    "razao_sobrecarga_pico_15m",
    "cota_m",
    "declividade_pct",
    "impermeabilizacao_frac",
    "dist_corpo_hidrico_m",
    "score_suscetibilidade_estatica",
    "dist_estacao_ativa_min_km",
]

FEATURES_PRE_CODIFICADAS_NIVEL2 = [
    "classe_suscetibilidade_ord",
    "estacao_primaria_offline_flag",
]

FEATURES_NOMINAIS_NIVEL2 = [
    "id_ponto",
]

TODAS_FEATURES_NIVEL2 = (
    FEATURES_NUMERICAS_NIVEL2 + FEATURES_PRE_CODIFICADAS_NIVEL2 + FEATURES_NOMINAIS_NIVEL2
)


def realizar_split_cronologico(
    df: pd.DataFrame,
    frac_treino: float = 0.60,
    frac_validacao: float = 0.20,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Realiza divisão estritamente cronológica em Treino, Validação e Teste
    respeitando a linha do tempo global para impedir data leakage temporal.
    """
    tempos_unicos = np.sort(df["timestamp"].unique())
    n_t = len(tempos_unicos)
    idx_tr = int(n_t * frac_treino)
    idx_val = int(n_t * (frac_treino + frac_validacao))

    t_corte_treino = tempos_unicos[idx_tr]
    t_corte_val = tempos_unicos[idx_val]

    df_train = df[df["timestamp"] < t_corte_treino].copy()
    df_val = df[(df["timestamp"] >= t_corte_treino) & (df["timestamp"] < t_corte_val)].copy()
    df_test = df[df["timestamp"] >= t_corte_val].copy()

    return df_train, df_val, df_test


def _construir_preprocessador() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), FEATURES_NUMERICAS_NIVEL2),
            ("ord_pre", "passthrough", FEATURES_PRE_CODIFICADAS_NIVEL2),
            (
                "nom",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                FEATURES_NOMINAIS_NIVEL2,
            ),
        ],
        remainder="drop",
    )


def _otimizar_limiares_por_ponto(
    df_val: pd.DataFrame,
    y_val: np.ndarray,
    probs_val: np.ndarray,
    recall_alvo: float = 0.88,
    precisao_minima: float = 0.55,
    precisao_maxima: float = 0.72,
) -> Dict[str, float]:
    """
    Calibra o limiar de decisão operacional para cada Ponto Crítico no conjunto de Validação.
    Prioriza atingir Recall >= 85% com Precisão na faixa operacional de Defesa Civil (55% a 72%),
    garantindo alta sensibilidade preventiva sem excesso de falsos alarmes.
    """
    limiares_por_ponto: Dict[str, float] = {}
    candidatos = np.linspace(0.08, 0.80, 73)

    def _escolher_limiar(y_arr: np.ndarray, p_arr: np.ndarray, default_t: float = 0.35) -> float:
        melhor_t = default_t
        melhor_util = -999.0
        for t in candidatos:
            preds = (p_arr >= t).astype(int)
            rec = recall_score(y_arr, preds, zero_division=0)
            prec = precision_score(y_arr, preds, zero_division=0)
            f2 = fbeta_score(y_arr, preds, beta=2.0, zero_division=0)

            pen_rec = 2.5 * max(0.0, recall_alvo - rec)
            pen_prec_low = 1.5 * max(0.0, precisao_minima - prec)
            pen_prec_high = 0.35 * max(0.0, prec - precisao_maxima)
            util = f2 + 0.25 * rec - pen_rec - pen_prec_low - pen_prec_high
            if util > melhor_util:
                melhor_util = util
                melhor_t = float(t)
        return round(melhor_t, 3)

    limiar_global = _escolher_limiar(y_val, probs_val, default_t=0.35)
    limiares_por_ponto["GLOBAL"] = limiar_global

    for id_ponto, grp in df_val.groupby("id_ponto"):
        mask = (df_val["id_ponto"] == id_ponto).to_numpy()
        y_loc = y_val[mask]
        p_loc = probs_val[mask]

        if y_loc.sum() < 5:
            limiares_por_ponto[str(id_ponto)] = limiar_global
            continue

        limiares_por_ponto[str(id_ponto)] = _escolher_limiar(
            y_loc, p_loc, default_t=limiar_global
        )

    return limiares_por_ponto


def _aplicar_limiares_por_ponto(
    df_eval: pd.DataFrame,
    probs: np.ndarray,
    limiares: Dict[str, float],
) -> np.ndarray:
    limiar_vetor = (
        df_eval["id_ponto"]
        .map(lambda x: limiares.get(str(x), limiares.get("GLOBAL", 0.35)))
        .to_numpy(dtype=float)
    )
    return (probs >= limiar_vetor).astype(int)


def _calcular_ic_bootstrap(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_boot: int = 200,
    seed: int = 42,
) -> Dict[str, Tuple[float, float]]:
    """Calcula intervalos de confiança de 95% via Bootstrap para Recall, Precisão e F2-Score."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    recalls, precs, f2s = [], [], []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        yt = y_true[idx]
        yp = y_pred[idx]
        if yt.sum() == 0:
            continue
        recalls.append(recall_score(yt, yp, zero_division=0))
        precs.append(precision_score(yt, yp, zero_division=0))
        f2s.append(fbeta_score(yt, yp, beta=2.0, zero_division=0))

    return {
        "recall_ic95": (
            round(float(np.percentile(recalls, 2.5)), 4),
            round(float(np.percentile(recalls, 97.5)), 4),
        ),
        "precisao_ic95": (
            round(float(np.percentile(precs, 2.5)), 4),
            round(float(np.percentile(precs, 97.5)), 4),
        ),
        "f2_ic95": (
            round(float(np.percentile(f2s, 2.5)), 4),
            round(float(np.percentile(f2s, 97.5)), 4),
        ),
    }


def _avaliar_modelo_completo(
    nome_modelo: str,
    df_eval: pd.DataFrame,
    y_true: np.ndarray,
    probs: np.ndarray,
    preds: np.ndarray,
) -> Dict[str, object]:
    tn, fp, fn, tp = confusion_matrix(y_true, preds, labels=[0, 1]).ravel()
    rec = float(recall_score(y_true, preds, zero_division=0))
    prec = float(precision_score(y_true, preds, zero_division=0))
    f1 = float(f1_score(y_true, preds, zero_division=0))
    f2 = float(fbeta_score(y_true, preds, beta=2.0, zero_division=0))
    pr_auc = float(average_precision_score(y_true, probs)) if y_true.sum() > 0 else 0.0
    roc_auc = float(roc_auc_score(y_true, probs)) if len(np.unique(y_true)) > 1 else 0.0
    brier = float(brier_score_loss(y_true, np.clip(probs, 0.0, 1.0)))

    ic95 = _calcular_ic_bootstrap(y_true, preds)

    metricas_por_ponto = {}
    for id_ponto, grp in df_eval.groupby("id_ponto"):
        mask = (df_eval["id_ponto"] == id_ponto).to_numpy()
        yt_p = y_true[mask]
        yp_p = preds[mask]
        pr_p = probs[mask]
        tn_p, fp_p, fn_p, tp_p = confusion_matrix(yt_p, yp_p, labels=[0, 1]).ravel()
        metricas_por_ponto[str(id_ponto)] = {
            "bairro": str(grp["bairro"].iloc[0]),
            "eh_piloto": bool(grp["eh_piloto"].iloc[0]),
            "eventos_reais_steps": int(yt_p.sum()),
            "tp": int(tp_p),
            "fp": int(fp_p),
            "fn": int(fn_p),
            "tn": int(tn_p),
            "recall": round(float(recall_score(yt_p, yp_p, zero_division=0)), 4),
            "precisao": round(float(precision_score(yt_p, yp_p, zero_division=0)), 4),
            "f2_score": round(float(fbeta_score(yt_p, yp_p, beta=2.0, zero_division=0)), 4),
            "prob_media_em_alagamento": round(float(pr_p[yt_p == 1].mean()), 4)
            if yt_p.sum() > 0
            else 0.0,
        }

    return {
        "nome_modelo": nome_modelo,
        "recall": round(rec, 4),
        "precisao": round(prec, 4),
        "f1_score": round(f1, 4),
        "f2_score": round(f2, 4),
        "pr_auc": round(pr_auc, 4),
        "roc_auc": round(roc_auc, 4),
        "brier_score": round(brier, 4),
        "intervalos_confianca_95": ic95,
        "matriz_confusao": {"tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn)},
        "analise_por_ponto_critico": metricas_por_ponto,
    }


def treinar_e_comparar_modelos_nivel2(
    df_unificado: pd.DataFrame,
) -> Dict[str, object]:
    """
    Executa o ciclo completo de treinamento, calibração, seleção de limiares e avaliação
    comparativa no conjunto de Teste para o Nível 2 (Detecção em Tempo Real).
    """
    n_sem_target = int(df_unificado["target_alagamento_presente"].isna().sum())
    df_limpo = df_unificado.dropna(subset=["target_alagamento_presente"]).copy()

    df_train, df_val, df_test = realizar_split_cronologico(df_limpo)

    X_train = df_train[TODAS_FEATURES_NIVEL2]
    y_train = df_train["target_alagamento_presente"].to_numpy(dtype=int)

    X_val = df_val[TODAS_FEATURES_NIVEL2]
    y_val = df_val["target_alagamento_presente"].to_numpy(dtype=int)

    X_test = df_test[TODAS_FEATURES_NIVEL2]
    y_test = df_test["target_alagamento_presente"].to_numpy(dtype=int)

    # -------------------------------------------------------------------------
    # Modelo 0: Baseline Heurístico Fixo (Chuva 1h >= 16mm ou Chuva 24h >= 45mm)
    # -------------------------------------------------------------------------
    probs_base_test = np.clip(
        (df_test["chuva_1h_mm"].to_numpy() / 22.0) * 0.7
        + (df_test["chuva_24h_mm"].to_numpy() / 55.0) * 0.3,
        0.0,
        1.0,
    )
    preds_base_test = (
        (df_test["chuva_1h_mm"].to_numpy() >= 15.0)
        | (df_test["chuva_24h_mm"].to_numpy() >= 42.0)
    ).astype(int)
    aval_baseline = _avaliar_modelo_completo(
        "0_Baseline_Regra_Fixa_Pluviometrica",
        df_test,
        y_test,
        probs_base_test,
        preds_base_test,
    )

    # -------------------------------------------------------------------------
    # Modelo 1 (Fase Inicial): Regressão Logística Regularizada (L2)
    # -------------------------------------------------------------------------
    pipe_lr = Pipeline(
        steps=[
            ("prep", _construir_preprocessador()),
            (
                "clf",
                LogisticRegression(
                    C=0.4,
                    class_weight={0: 1.0, 1: 3.2},
                    max_iter=600,
                    random_state=42,
                ),
            ),
        ]
    )
    pipe_lr.fit(X_train, y_train)
    probs_lr_val = pipe_lr.predict_proba(X_val)[:, 1]
    limiares_lr = _otimizar_limiares_por_ponto(df_val, y_val, probs_lr_val)
    probs_lr_test = pipe_lr.predict_proba(X_test)[:, 1]
    preds_lr_test = _aplicar_limiares_por_ponto(df_test, probs_lr_test, limiares_lr)
    aval_lr = _avaliar_modelo_completo(
        "1_Fase_Inicial_Regressao_Logistica_L2",
        df_test,
        y_test,
        probs_lr_test,
        preds_lr_test,
    )

    # -------------------------------------------------------------------------
    # Modelo 2 (Fase Intermediária): Random Forest Cost-Sensitive
    # -------------------------------------------------------------------------
    pipe_rf = Pipeline(
        steps=[
            ("prep", _construir_preprocessador()),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=180,
                    max_depth=9,
                    min_samples_leaf=8,
                    class_weight={0: 1.0, 1: 3.0},
                    random_state=42,
                    n_jobs=1,
                ),
            ),
        ]
    )
    pipe_rf.fit(X_train, y_train)
    probs_rf_val = pipe_rf.predict_proba(X_val)[:, 1]
    limiares_rf = _otimizar_limiares_por_ponto(df_val, y_val, probs_rf_val)
    probs_rf_test = pipe_rf.predict_proba(X_test)[:, 1]
    preds_rf_test = _aplicar_limiares_por_ponto(df_test, probs_rf_test, limiares_rf)
    aval_rf = _avaliar_modelo_completo(
        "2_Fase_Intermediaria_Random_Forest",
        df_test,
        y_test,
        probs_rf_test,
        preds_rf_test,
    )

    # -------------------------------------------------------------------------
    # Modelo 3 (Arquitetura Recomendada SADC): Ensemble Híbrido Multi-Bacia
    # Combina HistGradientBoosting + Random Forest + Regressão Logística (Soft Voting)
    # -------------------------------------------------------------------------
    ensemble_sadc = Pipeline(
        steps=[
            ("prep", _construir_preprocessador()),
            (
                "clf",
                VotingClassifier(
                    estimators=[
                        (
                            "hgb",
                            HistGradientBoostingClassifier(
                                learning_rate=0.05,
                                max_iter=180,
                                max_leaf_nodes=25,
                                min_samples_leaf=12,
                                l2_regularization=2.0,
                                class_weight={0: 1.0, 1: 3.0},
                                random_state=42,
                            ),
                        ),
                        (
                            "rf",
                            RandomForestClassifier(
                                n_estimators=180,
                                max_depth=10,
                                min_samples_leaf=6,
                                class_weight={0: 1.0, 1: 3.0},
                                random_state=42,
                                n_jobs=1,
                            ),
                        ),
                        (
                            "lr",
                            LogisticRegression(
                                C=0.5,
                                class_weight={0: 1.0, 1: 3.0},
                                max_iter=600,
                                random_state=42,
                            ),
                        ),
                    ],
                    voting="soft",
                    weights=[0.50, 0.35, 0.15],
                ),
            ),
        ]
    )
    ensemble_sadc.fit(X_train, y_train)

    probs_ens_val = ensemble_sadc.predict_proba(X_val)[:, 1]
    limiares_ens = _otimizar_limiares_por_ponto(
        df_val,
        y_val,
        probs_ens_val,
        recall_alvo=0.90,
        precisao_minima=0.56,
        precisao_maxima=0.72,
    )

    probs_ens_test = ensemble_sadc.predict_proba(X_test)[:, 1]
    preds_ens_test = _aplicar_limiares_por_ponto(df_test, probs_ens_test, limiares_ens)
    aval_ens = _avaliar_modelo_completo(
        "3_SADC_Ensemble_Hibrido_MultiBacia_Calibrado",
        df_test,
        y_test,
        probs_ens_test,
        preds_ens_test,
    )

    nomes_features_transformadas = (
        FEATURES_NUMERICAS_NIVEL2
        + FEATURES_PRE_CODIFICADAS_NIVEL2
        + list(
            pipe_rf.named_steps["prep"]
            .named_transformers_["nom"]
            .get_feature_names_out(FEATURES_NOMINAIS_NIVEL2)
        )
    )
    importancias_rf = pipe_rf.named_steps["clf"].feature_importances_
    ranking_importancia = sorted(
        zip(nomes_features_transformadas, importancias_rf),
        key=lambda x: x[1],
        reverse=True,
    )[:12]

    probs_full = ensemble_sadc.predict_proba(df_limpo[TODAS_FEATURES_NIVEL2])[:, 1]
    preds_full = _aplicar_limiares_por_ponto(df_limpo, probs_full, limiares_ens)
    df_limpo["prob_alagamento_tempo_real"] = np.round(probs_full, 4)
    df_limpo["pred_alagamento_tempo_real"] = preds_full

    return {
        "auditoria_split": {
            "linhas_sem_target_removidas": n_sem_target,
            "train_rows": len(df_train),
            "val_rows": len(df_val),
            "test_rows": len(df_test),
            "positivos_treino": int(y_train.sum()),
            "positivos_validacao": int(y_val.sum()),
            "positivos_teste": int(y_test.sum()),
        },
        "comparacao_modelos_teste": [
            aval_baseline,
            aval_lr,
            aval_rf,
            aval_ens,
        ],
        "modelo_campeao": "3_SADC_Ensemble_Hibrido_MultiBacia_Calibrado",
        "limiares_calibrados_por_ponto": limiares_ens,
        "top_12_features_importancia": [
            {"feature": k, "importancia": round(float(v), 4)} for k, v in ranking_importancia
        ],
        "modelo_objeto": ensemble_sadc,
        "df_com_predicoes_nivel2": df_limpo,
    }
