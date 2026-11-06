# SADC-Fortaleza — Sistema de Alerta e Detecção de Alagamentos Críticos de Fortaleza

Sistema preditivo georreferenciado em **3 níveis** para monitoramento, detecção em tempo real (ciclo de 10 minutos) e antecipação (*nowcasting* de 30 a 60 minutos) de alagamentos urbanos em Fortaleza, integrando a rede de **11 estações automáticas da Defesa Civil**, postos **Funceme/CEMADEN**, tábua/sensor de **maré do Porto do Mucuripe**, **103 câmeras do PMPU** e registros do **Canal 40199**.

## Estrutura do Projeto

- `docs/ANALISE_PLANEJAMENTO_E_ARQUITETURA.md`: Análise crítica do planejamento (ratificações, retificações e modelagem física/ML).
- `src/sadc_fortaleza/`:
  - `config.py`: Catálogo georreferenciado das 11 estações da Defesa Civil, postos parceiros, áreas-piloto (**Jacarecanga**, **Padre Andrade**, **Aldeota**, **Itaoca**) e protocolos operacionais (`NORMAL`, `VIGILANCIA`, `ATENCAO`, `ALERTA`, `ALARME`).
  - `data_pipeline/`: Controle de Qualidade (QC), Interpolação Espacial (IDW $p=2$) e Engenharia de Atributos Hidrológicos ($API_k$, Remanso Costeiro de Maré e Razão de Sobrecarga de Drenagem).
  - `models/`:
    - `level1_susceptibility.py`: Nível 1 — Suscetibilidade estática e limiares históricos por ponto crítico.
    - `level2_realtime_detection.py`: Nível 2 — Ensemble Híbrido Multi-Bacia calibrado em tempo real.
    - `level3_nowcasting.py`: Nível 3 — Antecipação (30–60 min), estimativa de lâmina d'água (cm) e cálculo de *Lead Time*.
  - `decision_engine/`: Motor de decisão operacional e livro de retroalimentação obrigatória.
  - `dashboard/`: Gerador do Painel Operacional Interativo HTML e relatórios técnicos.
- `outputs/`:
  - `painel_operacional_sadc_fortaleza.html`: Painel operacional interativo.
  - `RELATORIO_PILOTO_E_MODELOS.md`: Relatório técnico de avaliação dos modelos.
  - `relatorio_piloto_semanal.json`: Métricas estruturadas e verificação de metas.

## Como Executar

```bash
# Executar o pipeline completo e regerar os relatórios e painel HTML
python run_pilot_pipeline.py

# Executar a suíte de testes automatizados
python -m unittest tests/test_sadc_pipeline.py -v
```
