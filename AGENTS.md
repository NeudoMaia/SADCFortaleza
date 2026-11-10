# Diretrizes do Projeto SADC-Fortaleza e Memória da Linha de Ação

## 1. Configuração e Sincronização Automática Git/GitHub
- **Conta GitHub Padrão**: `NeudoMaia`
- **E-mail Git**: `100650913+NeudoMaia@users.noreply.github.com`
- **Repositório Remoto**: `https://github.com/NeudoMaia/SADCFortaleza.git` (branch `main` rastreando `origin/main` com `vscode-merge-base = origin/main`).
- **Automação de Commit/Push**: Sempre que alterações relevantes de código, modelos ou documentação forem concluídas, utilize `python scripts/git_autosync.py "<mensagem>"` (ou `git add -A` e `git commit` no sandbox seguido de `git push origin main` fora do sandbox) sem expor `.env`.

## 2. Diretrizes de Domínio e Telemetria (Defesa Civil de Fortaleza)
- **11 Estações Automáticas da Defesa Civil (API Plugfield Ao Vivo)**:
  - Autenticação: `https://prod-api.plugfield.com.br` (`login` e `api-key` em `.env`).
  - Ciclo de atualização do painel: **5 minutos (`300s`)** para acompanhamento pluviométrico automático por bairro (`mm / 5m`, `10m`, `1h`, `24h` e `ano`).
  - Cada uma das 11 estações (`8642` Centro, `3318` Dom Lustosa com sensor sônico `sensorId=314` no Rio Maranguapinho, `9137` Mucuripe, `8836` Montese, `9281` Benfica, `9242` Guararapes, `8869` Vila Velha, `9282` Granja Lisboa, `9134` Conjunto Esperança, `9249` Jangurussu, `9169` Messejana) possui **endereço físico de referência** e lista de **bairros cobertos** em `src/sadc_fortaleza/config.py`.
- **Modelagem Preditiva em 3 Níveis por Ponto Crítico / Microbacia**:
  - **Nível 1**: Suscetibilidade Estrutural Estática + Limiares calibrados por ponto crítico (`15m`, `1h`, `3h`, `24h`).
  - **Nível 2**: Detecção em Tempo Real (`3_SADC_Ensemble_Hibrido_MultiBacia_Calibrado` — `Recall = 99.78%`, `Precisão = 79.76%`, `F2 = 95.01%`).
  - **Nível 3**: Antecipação / Nowcasting (`30–60 min`, `Lead Time médio = 58.9 min`, `MAE lâmina = 2.75 cm`).
  - Áreas-piloto obrigatórias: **Jacarecanga**, **Padre Andrade**, **Aldeota** e **Itaoca** (além de **Aerolândia** e **Messejana**).

## 3. Estado Atual do Painel Operacional (`v2.5.0-symmetric-maps-clean-markers`)
- **Servidor Web**: `app_server.py` usando `SADCThreadingHTTPServer` e `SADCThreadingHTTPServerV6` (dual-stack IPv4 `0.0.0.0` + IPv6 `::1`, cabeçalhos `Clear-Site-Data: "cache"` e `Cache-Control: no-store`) nas portas **`3005`** (`http://localhost:3005/?v=2.5`) e **`3006`** (`http://localhost:3006/`).
- **Credenciais Padrão da Interface (`public/index.html`)**:
  - Usuário: `admin.defesacivil` | Senha: `admindc`
  - Brasão vetorial oficial da Defesa Civil de Fortaleza (padrão `DCCALOR`).
- **Estrutura Visual das Abas Operacionais (Sem Redundância e com Simetria 50%/50%)**:
  1. **Aba 1 (`1. Radar FUNCEME (RMF), Mapa & Pluviometria por Bairro`)**:
     - **Topo (Lado a Lado em Simetria 50% / 50% — `.maps-symmetry-grid`, altura idêntica de `430px`)**:
       - **Esquerda**: **📡 Mapa de Chuva Agora — Radar FUNCEME (`GMWR1000SST` — Fortaleza/RMF)** integrado ao endereço `https://radar.funceme.br/radar/GMWR1000SST/prsf/RADAR_FORTALEZARMF/20/true/2/0`, com **cor padrão no Tema Claro Original do site da FUNCEME (`osm`)** ou **Imagem de Satélite opcional**, animação das **20 varreduras de 5 em 5 minutos**, sem textos sobrepostos à imagem do radar.
       - **Direita**: **🌧️ Mapa dos 11 Pluviômetros Automáticos & Bairros (`CARTO` / Satélite)** com **marcadores circulares limpos** (sem caixas de texto retangulares sobre a imagem do mapa; detalhes exibidos ao passar o mouse ou clicar), sobreposição opcional do feixe do radar, raio IDW de 2 km, 121 bairros, pontos críticos e escolas/abrigos SME.
     - **Faixa Intermediária**: Diagnóstico quantitativo do cruzamento **Radar FUNCEME (`dBZ` e `mm/h`) × 11 Pluviômetros de Solo (`5m` e `1h`)** e os 4 corredores barlavento.
     - **Abaixo dos Mapas Simétricos (Largura Total em Grade de 2 Colunas — `.bairro-list-grid`)**: **Lista das 11 Estações Automáticas & Bairros com os Respectivos Impactos Pluviométricos** (`5m`, `10m`, `1h`, `24h`, `Radar dBZ / mm/h`, `Saturação %`, `Nível Sônico` e bairros cobertos).
  2. **Aba 2 (`2. Abrigos Temporários & Escolas de Apoio por Bairro`)**:
     - Apresenta a **Relação Oficial das Unidades Escolares da Rede Municipal de Fortaleza (Fonte: SME / ASSEPLAN — 12 páginas, 457 Unidades Escolares em 97 Bairros, Distritos I a VI: 280 `PAT`, 106 `CEI`, 51 `CRC`, 13 `ANE`, 7 `ESP`)** extraída integralmente do PDF oficial (`data/escolas_rede_municipal_fortaleza.json` e `/relacao_unidades_escolares_rede_municipal_fortaleza.pdf`), além das **14 Escolas-Polo Prioritárias da Defesa Civil**.

## 4. Continuidade Linear (Próximos Passos ao Retomar)
- Validar junto ao usuário a visualização do painel `v2.5` (`http://localhost:3005/?v=2.5` ou `http://localhost:3006/`) com os dois mapas lado a lado em simetria, marcadores limpos sem rótulos sobrepostos na imagem, tema claro original da FUNCEME no radar e lista de estações/impactos pluviométricos abaixo.
