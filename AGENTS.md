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

## 3. Estado Atual do Painel Operacional (`v2.2.0-funceme-radar-rmf`)
- **Servidor Web**: `app_server.py` usando `SADCThreadingHTTPServer` (`allow_reuse_address = False`, cabeçalhos `Clear-Site-Data: "cache"` e `Cache-Control: no-store`) nas portas **`3005`** (`http://localhost:3005/?v=2.2`) e **`3006`** (`http://localhost:3006/`).
- **Credenciais Padrão da Interface (`public/index.html`)**:
  - Usuário: `admin.defesacivil` | Senha: `admindc`
  - Brasão vetorial oficial da Defesa Civil de Fortaleza (padrão `DCCALOR`).
- **Estrutura Visual da Aba Principal**:
  1. **Topo (Acima do Mapa)**: Painel **📡 Monitoramento Dinâmico por Radar Meteorológico FUNCEME (`GMWR1000SST` — Fortaleza/RMF)** integrado ao endereço `https://radar.funceme.br/radar/GMWR1000SST/prsf/RADAR_FORTALEZARMF/20/true/2/0` e à API oficial da FUNCEME (`https://api1.funceme.br/rpc/v1/produto-gerado`), exibindo animação temporal interativa das **20 varreduras de 5 em 5 minutos** (`PRSF Chuva Agora`, `ACUM-H`, `ACUM-D` e Portal Embutido), **mensuração quantitativa de pluviometria por pixel (`dBZ` e `mm/h` via relação de Marshall-Palmer $Z = 200 R^{1.6}$)** sobre as 11 estações e sobre **4 corredores de aproximação barlavento** (`Leste`, `Nordeste`, `Sudeste` e `Sudoeste`).
  2. **Esquerda**: Mapa Georreferenciado Leaflet com a chave pública oficial da CARTO (`cb1_2t7z_1_b4192d625bdc678b8f9125ad` via `?key=...`, sem marca d'água `"API KEY REQUIRED"`), sobreposição do **Feixe do Radar FUNCEME**, limite municipal IBGE, malha de 121 bairros, raio IDW de 2 km, 11 estações e pontos críticos.
  3. **Direita (Ao Lado do Mapa — Padrão DCCALOR)**: **Monitoramento Pluviométrico por Bairro (Ciclo 5 Min + Radar)** exibindo o bairro principal, o **endereço da estação como ponto de referência**, os bairros secundários cobertos, a leitura automática em `mm / 5m` (`1h`) combinada à mensuração do radar (`dBZ` e `mm/h`) e a barra de saturação pluviométrica.
  4. **Abaixo do Mapa e da Lista**: **Diagnóstico Hidrológico por Ponto Crítico / Microbacia (3 Níveis)** com fusão Solo + Radar no Nowcasting (Nível 3), confirmação visual pelas 103 câmeras do PMPU e registro de retroalimentação obrigatória (Canal 40199 / COMDEC).

## 4. Continuidade Linear (Próximos Passos ao Retomar)
- Validar junto ao usuário a visualização do painel `v2.2` (`http://localhost:3005/?v=2.2` ou `http://localhost:3006/`) com o Radar Meteorológico FUNCEME dinâmico e coletar eventuais ratificações ou retificações.
