"""O caminho que um prompt percorre no second brain — medido, não desenhado.

Lê o transcript de UMA sessão do Claude Code (`~/.claude/projects/<repo>/
<id>.jsonl`, que registra cada chamada de ferramenta) e devolve, na ordem em
que apareceram, os arquivos do repositório que a sessão abriu para responder ao
primeiro prompt. É o insumo do slide 12 da final: os nós do grafo do
`grafo_repo.py` que acendem quando a pergunta entra.

Só conta o que é nó do grafo (`.md` e `.py` do branch) e só até a segunda fala
do humano — a resposta ao primeiro prompt. A busca é por nome literal de
arquivo dentro do input da ferramenta (`cat X`, `sed -n ... X`, `grep ... X`,
Read/Edit com `file_path`), a mesma regra de aresta do grafo.

Grava `Uteis/dados/trace_sessao.json` com o prompt verbatim, a lista de
arquivos e quantos comandos a sessão rodou. O transcript em si fica fora do
repositório (é local da máquina); o JSON é o que o slide consome.

Uso:

    python scripts/trace_sessao.py 9ed8510d          # prefixo do id da sessão
    python scripts/trace_sessao.py caminho/x.jsonl   # ou o arquivo direto
    python scripts/trace_sessao.py --demo
"""

import json
import sys
from pathlib import Path

import grafo_repo

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "Uteis" / "dados" / "trace_sessao.json"
TRANSCRIPTS = Path.home() / ".claude" / "projects" / "C--Users-felip-Documents-Pessoal-Desafio-Quant-Itau"


def _texto_humano(mensagem):
    """O texto de uma fala do humano, ou None se é retorno de ferramenta/sistema."""
    conteudo = mensagem.get("content")
    if isinstance(conteudo, str):
        partes = [conteudo]
    else:
        partes = [b.get("text", "") for b in conteudo or [] if b.get("type") == "text"]
    texto = "\n".join(p for p in partes if p).strip()
    return texto if texto and not texto.startswith("<") else None


def rastrear(linhas, nomes):
    """(prompt, arquivos na ordem de 1ª aparição, nº de comandos) do 1º turno."""
    prompt, arquivos, comandos = None, [], 0
    for linha in linhas:
        try:
            j = json.loads(linha)
        except ValueError:
            continue
        m = j.get("message") or {}
        if j.get("type") == "user":
            texto = _texto_humano(m)
            if texto is None:
                continue
            if prompt is None:
                prompt = texto
                continue
            break                         # 2ª fala do humano: fim do 1º turno
        if j.get("type") != "assistant" or prompt is None:
            continue
        for b in m.get("content") or []:
            if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                continue
            comandos += 1
            alvo = json.dumps(b.get("input", {}), ensure_ascii=False)
            for nome in nomes:
                if nome in alvo and nome not in arquivos:
                    arquivos.append(nome)
    return prompt, arquivos, comandos


def localizar(arg):
    p = Path(arg)
    if p.exists():
        return p
    achados = sorted(TRANSCRIPTS.glob(f"{arg}*.jsonl"))
    if len(achados) != 1:
        raise SystemExit(f"{len(achados)} transcripts casam com '{arg}' em {TRANSCRIPTS}")
    return achados[0]


def demo():
    nomes = ["Decisoes_pendentes.md", "bl_optimizer.py", "backtest.py", "backtest_v1.py"]
    def fala(t): return json.dumps({"type": "user", "message": {"content": t}})
    def tool(cmd): return json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}})
    linhas = [fala("por que o beta?"), tool("cat Decisoes_pendentes.md"),
              tool("sed -n 1,9p scripts/backtest_v1.py; cat Decisoes_pendentes.md"),
              fala("e o teto?"), tool("cat src/bl_optimizer.py")]
    prompt, arquivos, n = rastrear(linhas, nomes)
    assert prompt == "por que o beta?" and n == 2, (prompt, n)
    # ordem de 1ª aparição, sem repetir, e `backtest.py` NÃO casa em `backtest_v1.py`
    assert arquivos == ["Decisoes_pendentes.md", "backtest_v1.py"], arquivos
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
        sys.exit()
    transcript = localizar(sys.argv[1] if len(sys.argv) > 1 else "9ed8510d")
    nomes, familias, _ = grafo_repo.levantar()
    familia = dict(zip(nomes, familias))
    with open(transcript, encoding="utf-8") as f:
        prompt, arquivos, comandos = rastrear(f, nomes)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps({
        "sessao": transcript.stem[:8], "prompt": prompt, "comandos": comandos,
        "arquivos": [{"nome": a, "familia": familia[a]} for a in arquivos],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{SAIDA.relative_to(RAIZ)}: {len(arquivos)} arquivos em {comandos} comandos")
    for a in arquivos:
        print(f"  {familia[a]:9s} {a}")
