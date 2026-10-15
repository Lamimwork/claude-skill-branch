"""Links da extensão do Claude Code no VS Code, para a skill galho.

  python galho_link.py sessao                      id da conversa atual
  python galho_link.py link --session ID           link que abre uma conversa
  python galho_link.py link --prompt-file ARQ      link que abre conversa nova com o texto preenchido
  ... link [...] --abrir                           também abre no VS Code (code --open-url)

A pasta de sessões é a do projeto aberto (diretório atual). Para usar outra:
  --pasta CAMINHO, ou a variável de ambiente GALHO_PASTA_SESSOES.

O texto preenchido não é enviado: o usuário confere e aperta Enter.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

PROJETOS = Path.home() / ".claude" / "projects"
BASE = "vscode://anthropic.claude-code/open"


def pasta_sessoes(pasta=None):
    """Pasta onde o Claude Code guarda as conversas do projeto atual.

    O Claude Code nomeia a pasta trocando todo caractere que não é letra ou número
    do caminho do projeto por '-' (ex.: C:\\Users\\ana\\proj -> C--Users-ana-proj).
    """
    pasta = pasta or os.environ.get("GALHO_PASTA_SESSOES")
    if pasta:
        return Path(pasta)
    nome = re.sub(r"[^A-Za-z0-9]", "-", str(Path.cwd()))
    if PROJETOS.is_dir():
        for p in PROJETOS.iterdir():
            if p.is_dir() and p.name.lower() == nome.lower():
                return p
    return PROJETOS / nome


def sessao_atual(pasta=None):
    pasta = pasta_sessoes(pasta)
    arquivos = sorted(pasta.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not arquivos:
        sys.exit("Nenhuma sessão encontrada em " + str(pasta) + " (use --pasta ou GALHO_PASTA_SESSOES)")
    return arquivos[0].stem


def montar_link(session=None, prompt=None):
    params = {}
    if session:
        params["session"] = session
    if prompt:
        params["prompt"] = prompt
    return BASE + ("?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote) if params else "")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    ss = sub.add_parser("sessao")
    ss.add_argument("--pasta")
    lk = sub.add_parser("link")
    lk.add_argument("--session")
    lk.add_argument("--prompt-file")
    lk.add_argument("--abrir", action="store_true")
    a = ap.parse_args()

    if a.cmd == "sessao":
        print(sessao_atual(a.pasta))
        return

    prompt = Path(a.prompt_file).read_text(encoding="utf-8").strip() if a.prompt_file else None
    link = montar_link(a.session, prompt)
    print(link)
    if a.abrir:
        code = shutil.which("code") or shutil.which("code.cmd")
        if not code:
            sys.exit("Comando 'code' não encontrado; abrir pelo link no arvore.md.")
        subprocess.run([code, "--open-url", link], check=True)


if __name__ == "__main__":
    main()
