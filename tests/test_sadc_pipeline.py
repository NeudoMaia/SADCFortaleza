"""
Testes automatizados de integridade de engenharia de dados, ausência de data leakage,
controle de qualidade pluviométrica e cumprimento das metas operacionais do SADC-Fortaleza.
"""

from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from run_pilot_pipeline import executar_pipeline_completo


class TestSADCFortalezaPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resultados = executar_pipeline_completo(ROOT_DIR / "outputs")

    def test_controle_qualidade_detecta_anomalias(self):
        qc = self.resultados["qualidade_telemetria_qc"]["anomalias_detectadas"]
        self.assertGreater(qc["offline_null_count"], 0)
        self.assertGreater(qc["valores_negativos_count"], 0)
        self.assertGreater(qc["picos_irreais_spike_count"], 0)

    def test_cobertura_100pct_areas_risco(self):
        self.assertTrue(
            self.resultados["verificacao_indicadores_sucesso"]["cobertura_100pct_areas_risco"]
        )

    def test_pilotos_obrigatorios_presentes_nivel1(self):
        susc = self.resultados["nivel1_suscetibilidade_estatica"]
        bairros = {info["bairro"] for info in susc.values() if info["eh_piloto"]}
        self.assertEqual(bairros, {"Jacarecanga", "Padre Andrade", "Aldeota", "Itaoca"})

    def test_metas_recall_precisao_lead_time(self):
        ind = self.resultados["verificacao_indicadores_sucesso"]
        self.assertGreaterEqual(
            ind["recall_obtido"],
            0.80,
            f"Recall abaixo da meta de 80%: {ind['recall_obtido']}",
        )
        self.assertGreaterEqual(
            ind["precisao_obtida"],
            0.50,
            f"Precisão abaixo da meta mínima de 50%: {ind['precisao_obtida']}",
        )
        self.assertGreaterEqual(
            ind["lead_time_medio_minutos"],
            30.0,
            f"Lead time médio abaixo de 30 min: {ind['lead_time_medio_minutos']}",
        )
        self.assertTrue(ind["retroalimentacao_obrigatoria_ativa"])


if __name__ == "__main__":
    unittest.main()
