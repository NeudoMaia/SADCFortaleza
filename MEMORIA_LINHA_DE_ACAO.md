# Memória da Linha de Ação — Projeto SADC-Fortaleza

**Última atualização**: `2026-11-06 13:14 BRT`  
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

3. **Integração em Tempo Real com as 11 Estações Plugfield + API Satelital NASA**:
   - Cliente em tempo real em [`plugfield_client.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/src/sadc_fortaleza/data_pipeline/plugfield_client.py):
     - Conecta às **11 estações automáticas da Defesa Civil** (incluindo o sensor ultrassônico de nível do canal do Rio Maranguapinho em Dom Lustosa, `sensorId=314`).
     - Alimenta automaticamente a **pluviometria a cada 5 minutos (`300s`)** com classificação automática de nível e barra de saturação por bairro.
     - Integra a API da **NASA** (`WmJbrCnNL6zCBNnLFCgbLJFtjrTpghH7NNWq8mWb`) consultando `EPIC`, `NASA POWER` e camadas orbitais `GIBS Worldview` (VIIRS, Terra MODIS, Aqua MODIS) sobre Fortaleza/Ceará para cruzamento climatológico × pluviométrico.

4. **Painel Operacional Dinâmico (`v2.1` — Padrão DCCALOR)**:
   - Interface em [`public/index.html`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/public/index.html) servida por [`app_server.py`](file:///c:/Users/elineldo.pinheiro/Desktop/SADCFortaleza/app_server.py) nas portas `3005` e `3006`:
     - **Login padrão**: `admin.defesacivil` / `admindc` + Brasão da Defesa Civil de Fortaleza.
     - **Painel Superior NASA**: imagem satelital sobre Fortaleza + diagnóstico de cruzamento hidrometeorológico.
     - **Mapa Georreferenciado CARTO**: chave pública `cb1_2t7z_1_b4192d625bdc678b8f9125ad` aplicada (`?key=...`), eliminando a marca d'água `"API KEY REQUIRED"`.
     - **Painel Lateral Direito (Padrão DCCALOR)**: Lista de Bairros com o **endereço de referência da estação**, bairros adjacentes cobertos e **pluviometria medida automaticamente a cada 5 minutos (`mm / 5m`, `1h`, `24h`)**.
     - **Painel Inferior**: Diagnóstico Hidrológico por Ponto Crítico em 3 Níveis + confirmação por câmeras PMPU e retroalimentação 40199.

---

## 2. Ponto Exato de Retomada na Próxima Sessão
- Avaliar com o usuário o preview atualizado em **http://localhost:3005/?v=2.1** (ou **http://localhost:3006/**) e prosseguir com os ajustes ou novas funcionalidades que forem definidos após a análise visual.
