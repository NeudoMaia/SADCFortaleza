# Diretrizes do Projeto SADC-Fortaleza e Automação GitHub

## 1. Configuração e Sincronização Automática Git/GitHub
- **Conta GitHub Padrão**: `NeudoMaia`
- **E-mail Git**: `100650913+NeudoMaia@users.noreply.github.com`
- **Repositório Remoto**: `https://github.com/NeudoMaia/SADCFortaleza.git` (branch `main` rastreando `origin/main` com `vscode-merge-base = origin/main`).
- **Automação de Commit/Push**: Sempre que alterações relevantes de código, modelos ou documentação forem concluídas, utilize o script `python scripts/git_autosync.py "<mensagem>"` (ou `git add -A`, `git commit` no sandbox seguido de `git push origin main` fora do sandbox) para manter o repositório remoto sincronizado sem exigir configuração manual do usuário.

## 2. Diretrizes de Domínio (Defesa Civil de Fortaleza)
- As **11 estações automáticas da Defesa Civil de Fortaleza** (ciclo de 10 minutos) são a fonte primária de medição meteorológica (`chuva`, `temperatura`, `umidade`, `vento`, `rajada`, `UV` e `pressão`), complementadas pelos postos da Funceme, CEMADEN, maré do Mucuripe, 103 câmeras do PMPU e canal 40199.
- A modelagem deve sempre operar por **Ponto Crítico / Microbacia** em 3 níveis (Suscetibilidade Estática, Detecção em Tempo Real e Antecipação/Nowcasting de 30–60 min), mantendo `Recall >= 80%`, `Precisão >= 50%` e `Lead Time` entre 30 e 60 minutos.
