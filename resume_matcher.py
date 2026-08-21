#!/usr/bin/env python3
"""
resume_matcher.py

Compara um currículo com a descrição de uma vaga e aponta quais
palavras-chave da vaga estão faltando no currículo — útil pra entender
por que um ATS (sistema de triagem automática) pode estar descartando
sua candidatura antes de chegar em um humano.

Uso:
    python3 resume_matcher.py --curriculo curriculo.txt --vaga vaga.txt

Também aceita currículo e vaga em .pdf (requer a biblioteca pypdf,
veja requirements.txt):
    python3 resume_matcher.py --curriculo curriculo.pdf --vaga vaga.txt

Ou, sem arquivos, rodando no modo interativo:
    python3 resume_matcher.py
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# Abaixo do número de caracteres extraídos de um PDF, tratamos como
# indício de PDF escaneado sem OCR (texto vazio ou quase vazio) em vez
# de seguir com uma análise sem sentido.
MIN_CARACTERES_PDF = 50

# Stopwords em português (palavras comuns que não ajudam a identificar
# competências específicas de uma vaga).
STOPWORDS_PT = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da",
    "dos", "das", "em", "no", "na", "nos", "nas", "por", "para", "com",
    "sem", "sob", "sobre", "entre", "até", "após", "ante", "desde",
    "e", "ou", "mas", "que", "se", "não", "sim", "é", "são", "foi",
    "ser", "ter", "tem", "há", "como", "quando", "onde", "qual", "quais",
    "este", "esta", "isso", "essa", "esse", "aquele", "aquela", "outro",
    "outra", "outros", "outras", "seu", "sua", "seus", "suas", "nosso",
    "nossa", "eu", "tu", "ele", "ela", "nós", "vós", "eles", "elas",
    "você", "vocês", "lhe", "lhes", "me", "te", "nos", "vos", "mais",
    "menos", "muito", "muita", "muitos", "muitas", "pouco", "pouca",
    "todo", "toda", "todos", "todas", "cada", "algum", "alguma",
    "alguns", "algumas", "nenhum", "nenhuma", "também", "já", "ainda",
    "assim", "então", "pois", "porque", "porquê", "atuar", "atuação",
    "vaga", "empresa", "candidato", "candidata", "necessário",
    "necessária", "desejável", "diferencial", "experiência", "anos",
    "ano", "conhecimento", "conhecimentos", "área", "trabalho",
}

# Termos técnicos de múltiplas palavras que valem a pena detectar
# como bloco único, em vez de quebrar palavra por palavra.
TERMOS_COMPOSTOS = [
    "testes automatizados", "controle de versão", "trabalho em equipe",
    "resolução de problemas", "metodologias ágeis", "clean code",
    "code review", "ci/cd", "api rest", "banco de dados",
    "orientação a objetos", "estrutura de dados", "design patterns",
    "testes unitários", "integração contínua", "entrega contínua",
]


def normalizar(texto: str) -> str:
    """Minúsculas e limpeza leve de pontuação, preservando acentos."""
    texto = texto.lower()
    texto = re.sub(r"[^\w\sáàâãéèêíïóôõöúçñ/]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def extrair_termos_compostos(texto: str) -> list[str]:
    encontrados = []
    for termo in TERMOS_COMPOSTOS:
        if termo in texto:
            encontrados.append(termo)
    return encontrados


def extrair_palavras_chave(texto: str, top_n: int = 25) -> list[tuple[str, int]]:
    """Extrai as palavras (e termos compostos) mais frequentes de um texto,
    ignorando stopwords e palavras muito curtas."""
    texto_norm = normalizar(texto)

    compostos = extrair_termos_compostos(texto_norm)
    for termo in compostos:
        texto_norm = texto_norm.replace(termo, "")

    palavras = [
        p for p in texto_norm.split()
        if p not in STOPWORDS_PT and len(p) > 2 and not p.isdigit()
    ]

    contagem = Counter(palavras)
    for termo in compostos:
        contagem[termo] += 3  # termos compostos pesam mais: são mais específicos

    return contagem.most_common(top_n)


def comparar(curriculo: str, vaga: str, top_n: int = 25) -> None:
    palavras_vaga = extrair_palavras_chave(vaga, top_n=top_n)
    curriculo_norm = normalizar(curriculo)

    presentes = []
    faltando = []

    for termo, freq in palavras_vaga:
        if termo in curriculo_norm:
            presentes.append((termo, freq))
        else:
            faltando.append((termo, freq))

    total = len(palavras_vaga)
    aderencia = round(100 * len(presentes) / total, 1) if total else 0.0

    print("\n=== Análise de aderência currículo x vaga ===\n")
    print(f"Aderência estimada: {aderencia}% ({len(presentes)}/{total} termos-chave da vaga aparecem no currículo)\n")

    print("✅ Termos da vaga que JÁ aparecem no currículo:")
    if presentes:
        for termo, freq in presentes:
            print(f"   - {termo} (mencionado {freq}x na vaga)")
    else:
        print("   (nenhum encontrado)")

    print("\n⚠️  Termos da vaga que NÃO aparecem no currículo (considere adicionar, se fizer sentido):")
    if faltando:
        for termo, freq in faltando:
            print(f"   - {termo} (mencionado {freq}x na vaga)")
    else:
        print("   (nenhum — ótima aderência!)")

    print("\nDica: só adicione um termo se ele for verdade sobre sua experiência.")
    print("O objetivo é usar a MESMA palavra que a vaga usa pra descrever o que você já sabe fazer,")
    print("não inventar competência que você não tem.\n")


def ler_pdf(caminho: str, rotulo: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        print(
            "Erro: ler arquivos .pdf requer a biblioteca 'pypdf'.\n"
            "Instale com: pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    leitor = PdfReader(caminho)
    texto = "\n".join(pagina.extract_text() or "" for pagina in leitor.pages)

    if len(texto.strip()) < MIN_CARACTERES_PDF:
        print(
            f"Erro: não foi possível extrair texto útil de '{caminho}' ({rotulo}).\n"
            "Isso costuma acontecer com PDFs escaneados (imagem, sem camada de texto)\n"
            "— nesse caso, use OCR antes ou exporte o documento como .txt.",
            file=sys.stderr,
        )
        sys.exit(1)

    return texto


def ler_arquivo_ou_stdin(caminho: str | None, rotulo: str) -> str:
    if caminho:
        if Path(caminho).suffix.lower() == ".pdf":
            return ler_pdf(caminho, rotulo)
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    print(f"Cole o texto de: {rotulo}")
    print("(cole o texto e finalize com uma linha contendo apenas: FIM)\n")
    linhas = []
    for linha in sys.stdin:
        if linha.strip() == "FIM":
            break
        linhas.append(linha)
    return "\n".join(linhas)


def main():
    # Consoles do Windows com codepage legada (cp1252) quebram ao imprimir
    # acentos e emojis da saída; força UTF-8 quando o terminal permitir.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Compara currículo com descrição de vaga e aponta palavras-chave faltando."
    )
    parser.add_argument("--curriculo", help="Caminho do arquivo .txt ou .pdf com o currículo")
    parser.add_argument("--vaga", help="Caminho do arquivo .txt ou .pdf com a descrição da vaga")
    parser.add_argument("--top", type=int, default=25, help="Quantos termos-chave analisar (padrão: 25)")
    args = parser.parse_args()

    curriculo = ler_arquivo_ou_stdin(args.curriculo, "CURRÍCULO")
    vaga = ler_arquivo_ou_stdin(args.vaga, "DESCRIÇÃO DA VAGA")

    comparar(curriculo, vaga, top_n=args.top)


if __name__ == "__main__":
    main()
