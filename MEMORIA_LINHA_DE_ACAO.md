# Memória da Linha de Ação — Projeto SADC-Fortaleza

**Última atualização**: `2026-11-09 12:34 BRT`  
**Repositório GitHub Sincronizado**: `https://github.com/NeudoMaia/SADCFortaleza.git` (`branch main`)

---

## 1. Linha Cronológica do que já foi Construído e Validado

1. **Planejamento, Retificação e Modelagem Preditiva em 3 Níveis (`src/sadc_fortaleza/`)**:
   - **Controle de Qualidade (QC) e Interpolação Espacial IDW ($p=2$)**: [`quality_and_spatial.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/src/sadc_fortaleza/data_pipeline/quality_and_spatial.py) com cobertura de 100% das áreas de risco.
   - **Engenharia de Atributos Hidrológicos e Costeiros**: [`feature_engineering.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/src/sadc_fortaleza/features/feature_engineering.py) incluindo acumulado antecedente ($API$), aceleração de chuva, remanso de maré do Porto do Mucuripe e sobrecarga de drenagem.
   - **Nível 1 (Suscetibilidade Estática)**: [`level1_susceptibility.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/src/sadc_fortaleza/models/level1_susceptibility.py) com limiares específicos para **Jacarecanga**, **Padre Andrade**, **Aldeota**, **Itaoca**, **Aerolândia** e **Messejana**.
   - **Nível 2 (Detecção em Tempo Real)**: [`level2_realtime_detection.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/src/sadc_fortaleza/models/level2_realtime_detection.py) — Ensemble Híbrido Multi-Bacia Calibrado atingindo `Recall = 99.78%`, `Precisão = 79.76%`, `F2-Score = 95.01%`.
   - **Nível 3 (Antecipação / Nowcasting 30–60 min)**: [`level3_nowcasting.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/src/sadc_fortaleza/models/level3_nowcasting.py) — `Lead Time Médio = 58.9 min` e `MAE Lâmina = 2.75 cm`.
   - **Suíte de Testes**: [`test_sadc_pipeline.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/tests/test_sadc_pipeline.py) (`4/4` testes aprovados).

2. **Automação Git/GitHub (`NeudoMaia`)**:
   - Configurada em [`scripts/git_autosync.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/scripts/git_autosync.py) e [`AGENTS.md`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/AGENTS.md), mantendo `.env` protegido no [`.gitignore`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/.gitignore).

3. **Integração em Tempo Real com as 11 Estações Plugfield + Radar Meteorológico FUNCEME (`GMWR1000SST`)**:
   - Cliente em tempo real em [`plugfield_client.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/src/sadc_fortaleza/data_pipeline/plugfield_client.py):
     - Conecta às **11 estações automáticas da Defesa Civil** (incluindo o sensor ultrassônico de nível do canal do Rio Maranguapinho em Dom Lustosa, `sensorId=314`).
     - Alimenta automaticamente a **pluviometria a cada 5 minutos (`300s`)** com classificação automática de nível e barra de saturação por bairro.
     - Substituiu a imagem estática da NASA pelo **Radar Meteorológico da FUNCEME (`GMWR1000SST` — Fortaleza/RMF)** integrado a `https://radar.funceme.br/radar/GMWR1000SST/prsf/RADAR_FORTALEZARMF/20/true/2/0` e à API oficial `https://api1.funceme.br/rpc/v1/produto-gerado`, trazendo animação temporal das **20 varreduras de 5 em 5 minutos** (`PRSF Chuva Agora`, `ACUM-H`, `ACUM-D` e Portal Embutido) e **mensuração quantitativa de pluviometria por pixel (`dBZ` e `mm/h` via relação de Marshall-Palmer $Z = 200 R^{1.6}$)** sobre as 11 estações e 4 corredores de deslocamento (`Leste`, `Nordeste`, `Sudeste` e `Sudoeste`).

4. **Painel Operacional Dinâmico (`v2.2.0-funceme-radar-rmf` — Padrão DCCALOR Limpo)**:
   - Interface em [`public/index.html`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/public/index.html) servida por [`app_server.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/app_server.py) nas portas `3005` e `3006`:
     - **Login padrão**: `admin.defesacivil` / `admindc` + Brasão da Defesa Civil de Fortaleza.
     - **Painel Superior Radar FUNCEME**: animação de 20 quadros de 5 min + seletor opcional de **Imagem de Satélite** no fundo do radar + mensuração `dBZ`/`mm/h` e corredores de aproximação.
     - **Mapa Georreferenciado Principal (Esquerda)**: chave pública CARTO `cb1_2t7z_1_b4192d625bdc678b8f9125ad` (`?key=...`), seletor opcional de **Imagem de Satélite + Rótulos (`satelite_hibrido`) / Satélite Puro (`satelite_puro`)**, sobreposição do **Feixe do Radar FUNCEME**, 11 estações, raio IDW 2 km e pontos críticos.
     - **Painel Lateral Direito (Padrão DCCALOR)**: Lista de Bairros com o **endereço de referência da estação**, bairros adjacentes cobertos e **pluviometria medida automaticamente a cada 5 minutos (`mm / 5m`, `1h`) + leitura do Radar (`dBZ` / `mm/h`)**.
     - **Limpeza Visual Validada**: O quadro inferior de 6 cartões de diagnóstico hidrológico em 3 níveis foi retirado da aba principal conforme solicitado pelo usuário para manter o painel objetivo e sem poluição visual.

---

## 2. Ponto Exato de Retomada na Próxima Sessão
- Continuar a partir da validação do painel `v2.2.0-funceme-radar-rmf` (**http://localhost:3005/?v=2.3** ou **http://localhost:3006/**) com os dois mapas dotados de opção de **Imagem de Satélite** e o layout limpo focado no Radar FUNCEME + Mapa + Lista de Bairros por Estação.
