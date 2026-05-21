#!/usr/bin/env bash
#
# md-to-pdf.sh — converte um arquivo .md em PDF na pasta espelho.
#
# Convenção do projeto (AGENTS.md §6, docs/tests/testing-standards.md §9):
#   docs/tests/reports/<timestamp>.md  →  docs/tests/reports-pdf/<timestamp>.pdf
#
# Uso:
#   ./scripts/md-to-pdf.sh docs/tests/reports/2026-05-21_16-38-42.md
#   ./scripts/md-to-pdf.sh docs/tests/testing-standards.md
#
# Engine padrão: pandoc + xelatex. Instalação:
#   sudo apt install -y pandoc texlive-xetex texlive-fonts-recommended texlive-lang-portuguese
#
# Fallback leve (sem TeX, qualidade visual menor):
#   ENGINE=mdpdf ./scripts/md-to-pdf.sh <input.md>
#   (usa `npx mdpdf` — só precisa de Node, ~50 MB de deps efêmeras)

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Uso: $0 <input.md> [--engine=pandoc|mdpdf]" >&2
    exit 1
fi

INPUT="$1"
ENGINE="${ENGINE:-pandoc}"

if [[ ! -f "$INPUT" ]]; then
    echo "Erro: arquivo não encontrado: $INPUT" >&2
    exit 2
fi

# Determina path de saída pela convenção:
#   docs/tests/reports/*.md   → docs/tests/reports-pdf/*.pdf
#   docs/tests/*.md           → docs/tests/*.pdf (raiz)
#   outro/qualquer/*.md       → mesmo dir, mesmo nome, .pdf
INPUT_DIR="$(dirname "$INPUT")"
INPUT_NAME="$(basename "$INPUT" .md)"

case "$INPUT_DIR" in
    docs/tests/reports)
        OUTPUT_DIR="docs/tests/reports-pdf"
        ;;
    *)
        OUTPUT_DIR="$INPUT_DIR"
        ;;
esac

mkdir -p "$OUTPUT_DIR"
OUTPUT="$OUTPUT_DIR/$INPUT_NAME.pdf"

case "$ENGINE" in
    pandoc)
        if ! command -v pandoc >/dev/null 2>&1; then
            echo "Erro: pandoc não instalado. Rode:" >&2
            echo "  sudo apt install -y pandoc texlive-xetex texlive-fonts-recommended texlive-lang-portuguese" >&2
            echo "OU use ENGINE=mdpdf $0 $INPUT" >&2
            exit 3
        fi
        pandoc "$INPUT" \
            --pdf-engine=xelatex \
            -V geometry:margin=2cm \
            -V mainfont='DejaVu Serif' \
            -V monofont='DejaVu Sans Mono' \
            -V linkcolor=blue \
            -V documentclass=article \
            --toc \
            --toc-depth=2 \
            -o "$OUTPUT"
        ;;
    mdpdf)
        if ! command -v npx >/dev/null 2>&1; then
            echo "Erro: npx não disponível. Instale Node 22+ via nvm." >&2
            exit 3
        fi
        npx --yes mdpdf "$INPUT" "$OUTPUT"
        ;;
    *)
        echo "Erro: engine desconhecido '$ENGINE'. Use 'pandoc' ou 'mdpdf'." >&2
        exit 4
        ;;
esac

echo "✓ Gerado: $OUTPUT"
