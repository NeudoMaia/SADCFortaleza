"""
Utilitário de sincronização automática Git/GitHub para o projeto SADC-Fortaleza.
Identidade configurada: NeudoMaia (100650913+NeudoMaia@users.noreply.github.com)
Repositório Remoto: https://github.com/NeudoMaia/SADCFortaleza.git (branch main -> origin/main)
"""

from datetime import datetime
from pathlib import Path
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent


def sincronizar_github(mensagem: str = "") -> int:
    if not mensagem:
        agora = datetime.now().strftime("%Y-%m-%d %H:%M")
        mensagem = f"chore(auto-sync): atualizacao automatica SADC-Fortaleza ({agora})"

    subprocess.run(["git", "add", "-A"], cwd=str(ROOT_DIR), check=True)
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
    )
    if status.stdout.strip():
        subprocess.run(["git", "commit", "-m", mensagem], cwd=str(ROOT_DIR), check=True)
        print(f"Commit criado: {mensagem}")
    else:
        print("Nenhuma alteracao pendente para commit.")

    res_push = subprocess.run(["git", "push", "origin", "main"], cwd=str(ROOT_DIR))
    return res_push.returncode


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    sys.exit(sincronizar_github(msg))
