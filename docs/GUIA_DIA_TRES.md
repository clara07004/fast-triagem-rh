# Guia Detalhado — Dia Três

> Output Excel, Pipeline orquestrador e CLI. Após esse dia, você tem o MVP rodando ponta a ponta.

**Data:** 2026-05-06  
**Tempo estimado:** 5.5h de trabalho  
**Saída esperada:** Script funcionando: `python -m fast_triagem_rh --vaga criterios.xlsx --cvs pasta/`

---

## Overview do Dia Três

```
T09 (Output Excel)
    ↓
T10 (Pipeline)
    ↓
T11 (CLI)
    ↓
MVP Rodando
```

Você vai fazer 3 tarefas que se conectam assim:
1. **T09** (2h): escrever resultados em Excel com openpyxl
2. **T10** (2.5h): orquestrador que chama parsers → IA → output em sequência
3. **T11** (1h): CLI para Karina usar (`--vaga` + `--cvs`)

No final: script pronto para Dia 4 (teste ponta a ponta com CVs reais).

---

## Pré-requisitos

Antes de começar, confirme:

- [ ] T01–T08 completados (você tem parsers + analyzer funcionando)
- [ ] Arquivo PandaPé em `testes/`
- [ ] Template Excel em `criterios_vaga_template.xlsx`
- [ ] Pasta `src/fast_triagem_rh/output/` criada (você cria em T09)

Se algo acima faltar, resolva antes de começar.

---

# T09 — Output Excel (2h)

## O que é

Um módulo que:
1. Recebe lista de `ResultadoCandidato` (saída da IA)
2. Ordena: aprovado > verificar > reprovado > erros (cada grupo por pontuação desc)
3. Escreve em XLSX com openpyxl
4. Colunas claras para Karina ler: Nome | Contato | Classificação | Pontuação | Pontos Positivos | Pontos Negativos | Justificativa | Fonte | Data

## Por que é importante

Sem isso, o resultado fica só em JSON na memória. Karina precisa de um arquivo Excel que ela entende, que abre no computador dela, e que ela pode revisar antes de encaminhar aos gestores.

## Como fazer

### Passo 1: Criar a pasta e arquivo

Crie `src/fast_triagem_rh/output/` se não existir.

Dentro, crie `excel.py`.

Estrutura esperada:

```
src/fast_triagem_rh/
├── output/
│   ├── __init__.py    (vazio, ou com imports)
│   └── excel.py       (criar agora)
```

### Passo 2: Escrever o código

```python
# src/fast_triagem_rh/output/excel.py
"""Geração de planilha de resultados com openpyxl."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from ..models import ResultadoCandidato
from ..logger import get_logger

log = get_logger(__name__)


class ExcelOutputError(Exception):
    """Erro ao gerar arquivo Excel."""


def gerar_planilha_triagem(
    resultados: list[ResultadoCandidato],
    nome_vaga: str,
    pasta_saida: str | Path = ".",
) -> Path:
    """Gera planilha Excel com resultados de triagem.

    Args:
        resultados: Lista de ResultadoCandidato (saída do analyzer).
        nome_vaga: Nome da vaga (para nomear o arquivo).
        pasta_saida: Pasta onde salvar o arquivo.

    Returns:
        Path do arquivo criado.

    Raises:
        ExcelOutputError: Se não conseguir gerar o arquivo.
    """
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    if not resultados:
        raise ExcelOutputError("Nenhum resultado para gerar planilha")

    try:
        # === Ordenar resultados ===
        # Prioridade: aprovado > verificar > reprovado > erros
        # Dentro de cada grupo: por pontuação descrescente

        def sort_key(r: ResultadoCandidato) -> tuple:
            """Chave de ordenação: (prioridade, -pontuacao)."""
            prioridade_map = {
                "aprovado": 0,
                "verificar": 1,
                "reprovado": 2,
                "erro_parsing": 3,
                "erro_api": 3,
            }
            prioridade = prioridade_map.get(r.classificacao, 99)
            return (prioridade, -r.pontuacao)

        resultados_ordenados = sorted(resultados, key=sort_key)

        # === Criar workbook ===
        wb = Workbook()
        ws = wb.active
        ws.title = "Triagem"

        # === Headers ===
        headers = [
            "Nome",
            "Contato",
            "Classificação",
            "Pontuação",
            "Pontos Positivos",
            "Pontos Negativos",
            "Justificativa",
            "Arquivo Fonte",
            "Data Triagem",
        ]

        # Estilo dos headers
        header_fill = PatternFill(
            start_color="4472C4", end_color="4472C4", fill_type="solid"
        )
        header_font = Font(bold=True, color="FFFFFF", size=11)

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # === Dados ===
        # Cores por classificação
        cores_classificacao = {
            "aprovado": "C6EFCE",  # Verde claro
            "verificar": "FFEB9C",  # Amarelo claro
            "reprovado": "FFC7CE",  # Vermelho claro
            "erro_parsing": "E2EFDA",  # Cinza claro
            "erro_api": "E2EFDA",  # Cinza claro
        }

        for row_num, resultado in enumerate(resultados_ordenados, 2):
            cor_fundo = cores_classificacao.get(resultado.classificacao, "FFFFFF")
            cor_fill = PatternFill(start_color=cor_fundo, end_color=cor_fundo, fill_type="solid")

            # Formatar data
            data_str = resultado.data_triagem.strftime("%Y-%m-%d %H:%M")

            # Formatar listas de pontos
            pontos_positivos_str = " • ".join(resultado.pontos_positivos) if resultado.pontos_positivos else "—"
            pontos_negativos_str = " • ".join(resultado.pontos_negativos) if resultado.pontos_negativos else "—"

            dados_linha = [
                resultado.nome or "—",
                resultado.contato or "—",
                resultado.classificacao,
                resultado.pontuacao,
                pontos_positivos_str,
                pontos_negativos_str,
                resultado.justificativa,
                resultado.arquivo_fonte,
                data_str,
            ]

            for col_num, valor in enumerate(dados_linha, 1):
                cell = ws.cell(row=row_num, column=col_num, value=valor)
                cell.fill = cor_fill
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        # === Ajustar colunas ===
        ws.column_dimensions["A"].width = 20  # Nome
        ws.column_dimensions["B"].width = 25  # Contato
        ws.column_dimensions["C"].width = 15  # Classificação
        ws.column_dimensions["D"].width = 12  # Pontuação
        ws.column_dimensions["E"].width = 35  # Pontos Positivos
        ws.column_dimensions["F"].width = 35  # Pontos Negativos
        ws.column_dimensions["G"].width = 40  # Justificativa
        ws.column_dimensions["H"].width = 30  # Arquivo Fonte
        ws.column_dimensions["I"].width = 18  # Data Triagem

        # Altura das linhas
        ws.row_dimensions[1].height = 30
        for row in range(2, len(resultados_ordenados) + 2):
            ws.row_dimensions[row].height = 40

        # === Resumo no topo ===
        # (Opcional) Adicionar aba de resumo
        ws_resumo = wb.create_sheet("Resumo", 0)
        ws_resumo["A1"] = "Vaga:"
        ws_resumo["B1"] = nome_vaga
        ws_resumo["A2"] = "Data de processamento:"
        ws_resumo["B2"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws_resumo["A4"] = "Estatísticas:"
        ws_resumo["A5"] = "Aprovados:"
        ws_resumo["B5"] = sum(1 for r in resultados_ordenados if r.classificacao == "aprovado")
        ws_resumo["A6"] = "Verificar:"
        ws_resumo["B6"] = sum(1 for r in resultados_ordenados if r.classificacao == "verificar")
        ws_resumo["A7"] = "Reprovados:"
        ws_resumo["B7"] = sum(1 for r in resultados_ordenados if r.classificacao == "reprovado")
        ws_resumo["A8"] = "Erros:"
        ws_resumo["B8"] = sum(1 for r in resultados_ordenados if r.classificacao in ["erro_parsing", "erro_api"])
        ws_resumo["A9"] = "Total:"
        ws_resumo["B9"] = len(resultados_ordenados)

        # === Salvar arquivo ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"triagem_{nome_vaga}_{timestamp}.xlsx"
        caminho_arquivo = pasta_saida / nome_arquivo

        wb.save(caminho_arquivo)

        log.info(f"Planilha gerada: {caminho_arquivo}")
        return caminho_arquivo

    except Exception as exc:
        raise ExcelOutputError(f"Erro ao gerar planilha Excel: {exc}") from exc
```

### Passo 3: Testar

Crie `tests/test_output.py`:

```python
# tests/test_output.py
from datetime import datetime
from pathlib import Path
from src.fast_triagem_rh.models import ResultadoCandidato
from src.fast_triagem_rh.output.excel import gerar_planilha_triagem

# Criar resultados fictícios
resultados = [
    ResultadoCandidato(
        nome="João Silva",
        contato="joao@email.com / (11) 98765-4321",
        classificacao="aprovado",
        pontuacao=92,
        pontos_positivos=["5+ anos Python", "API REST"],
        pontos_negativos=[],
        justificativa="Excelente match com requisitos.",
        arquivo_fonte="joao_cv.pdf",
    ),
    ResultadoCandidato(
        nome="Maria Santos",
        contato="maria@email.com",
        classificacao="verificar",
        pontuacao=65,
        pontos_positivos=["Python", "Backend"],
        pontos_negativos=["Pouca experiência com API"],
        justificativa="Potencial, mas precisa validar.",
        arquivo_fonte="maria_cv.pdf",
    ),
    ResultadoCandidato(
        nome="Pedro Costa",
        contato=None,
        classificacao="reprovado",
        pontuacao=30,
        pontos_positivos=[],
        pontos_negativos=["Sem Python", "Sem API REST"],
        justificativa="Não atende requisitos obrigatórios.",
        arquivo_fonte="pedro_cv.pdf",
    ),
]

# Gerar planilha
caminho = gerar_planilha_triagem(resultados, "Engenheiro Python", ".")

print(f"Planilha criada: {caminho}")
print(f"Arquivo existe: {caminho.exists()}")
```

Roda com:

```bash
python tests/test_output.py
```

Se criar um arquivo `.xlsx` sem erro, passou.

## Checklist de T09

- [ ] Pasta `src/fast_triagem_rh/output/` criada
- [ ] Arquivo `excel.py` com função `gerar_planilha_triagem()`
- [ ] Função recebe lista de `ResultadoCandidato` e path da pasta
- [ ] Retorna Path do arquivo criado
- [ ] Ordena: aprovado > verificar > reprovado > erros (por pontuação)
- [ ] Colunas: Nome | Contato | Classificação | Pontuação | Pontos Positivos | Pontos Negativos | Justificativa | Fonte | Data
- [ ] Cores por classificação (verde, amarelo, vermelho, cinza)
- [ ] Aba "Resumo" com estatísticas
- [ ] Teste no REPL com resultados fictícios passa
- [ ] Arquivo Excel abre normalmente no Excel
- [ ] Commit feito: `feat(output): gerar planilha Excel com openpyxl`

---

# T10 — Pipeline Orquestrador (2.5h)

## O que é

Um módulo que coordena todo o fluxo:

1. Valida critérios (Excel preenchido por Karina)
2. Varre pasta de CVs
3. Identifica tipo de cada arquivo (PDF, DOCX, PandaPé Excel)
4. Parseia cada arquivo
5. Manda para análise (IA)
6. Acumula resultados
7. Gera planilha Excel

Se algo falhar (PDF corrompido, IA com erro), registra e continua.

## Por que é importante

É a "orquestra" — sem ela, você teria que chamar cada parser à mão. Pipeline torna simples rodar centenas de candidatos.

## Como fazer

### Passo 1: Criar o arquivo

Crie `src/fast_triagem_rh/pipeline.py`.

### Passo 2: Escrever o código

```python
# src/fast_triagem_rh/pipeline.py
"""Pipeline de triagem — orquestra parsers, IA e output."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from ..models import ResultadoCandidato, VagaCriterios
from ..parsers.criterios import parse_criterios, CriteriosParseError
from ..parsers.pdf import extrair_texto_pdf, PDFParseError
from ..parsers.docx import extrair_texto_docx, DOCXParseError
from ..analyzer import analisar_candidato, AnalyzerError
from ..output.excel import gerar_planilha_triagem, ExcelOutputError
from ..logger import get_logger

log = get_logger(__name__)


class PipelineError(Exception):
    """Erro geral no pipeline."""


def rodar_triagem(
    arquivo_criterios: str | Path,
    pasta_cvs: str | Path,
    pasta_saida: str | Path = ".",
) -> Path:
    """Executa pipeline completo de triagem.

    Args:
        arquivo_criterios: Path do Excel com critérios (preenchido por Karina).
        pasta_cvs: Pasta contendo CVs (PDF, DOCX, ou Excel PandaPé).
        pasta_saida: Onde salvar o arquivo Excel de resultados.

    Returns:
        Path do arquivo Excel gerado.

    Raises:
        PipelineError: Se falhar irrevogavelmente (critérios inválidos, pasta vazia, etc.).
    """
    arquivo_criterios = Path(arquivo_criterios)
    pasta_cvs = Path(pasta_cvs)
    pasta_saida = Path(pasta_saida)

    run_id = str(uuid4())[:8]  # ID único pra rastrear execução
    log.info(f"Iniciando pipeline (run_id={run_id})")

    # === 1. Validar critérios ===
    try:
        vaga = parse_criterios(arquivo_criterios)
        log.info(f"Critérios carregados: {vaga.cargo}")
    except CriteriosParseError as exc:
        raise PipelineError(f"Erro ao carregar critérios: {exc}") from exc

    # === 2. Listar CVs ===
    if not pasta_cvs.exists():
        raise PipelineError(f"Pasta de CVs não existe: {pasta_cvs}")

    arquivos_cv = list(pasta_cvs.glob("**/*"))
    arquivos_cv = [f for f in arquivos_cv if f.is_file()]

    if not arquivos_cv:
        raise PipelineError(f"Nenhum arquivo encontrado em: {pasta_cvs}")

    log.info(f"Encontrados {len(arquivos_cv)} arquivos")

    # === 3. Processar cada CV ===
    resultados: list[ResultadoCandidato] = []
    estatisticas = {
        "total": len(arquivos_cv),
        "processados": 0,
        "erros_parsing": 0,
        "erros_api": 0,
    }

    for i, arquivo_cv in enumerate(arquivos_cv, 1):
        try:
            log.info(f"[{i}/{len(arquivos_cv)}] Processando: {arquivo_cv.name}")

            # Identificar tipo e parsear
            extensao = arquivo_cv.suffix.lower()

            if extensao == ".pdf":
                try:
                    texto = extrair_texto_pdf(arquivo_cv)
                except PDFParseError as exc:
                    log.warning(f"  Erro ao parsear PDF: {exc}")
                    # Adicionar resultado com erro
                    resultados.append(
                        ResultadoCandidato(
                            nome=None,
                            contato=None,
                            classificacao="erro_parsing",
                            pontuacao=0,
                            pontos_positivos=[],
                            pontos_negativos=[str(exc)],
                            justificativa="PDF não pode ser processado.",
                            arquivo_fonte=arquivo_cv.name,
                        )
                    )
                    estatisticas["erros_parsing"] += 1
                    continue

            elif extensao == ".docx":
                try:
                    texto = extrair_texto_docx(arquivo_cv)
                except DOCXParseError as exc:
                    log.warning(f"  Erro ao parsear DOCX: {exc}")
                    resultados.append(
                        ResultadoCandidato(
                            nome=None,
                            contato=None,
                            classificacao="erro_parsing",
                            pontuacao=0,
                            pontos_positivos=[],
                            pontos_negativos=[str(exc)],
                            justificativa="Word não pode ser processado.",
                            arquivo_fonte=arquivo_cv.name,
                        )
                    )
                    estatisticas["erros_parsing"] += 1
                    continue

            else:
                log.warning(f"  Tipo não suportado: {extensao}. Pulando.")
                continue

            # Analisar com IA
            try:
                resultado = analisar_candidato(vaga, texto, nome_arquivo=arquivo_cv.name)
                resultados.append(resultado)
                log.info(
                    f"  OK: {resultado.nome or 'sem nome'} | "
                    f"{resultado.classificacao} ({resultado.pontuacao}/100)"
                )
                estatisticas["processados"] += 1

            except AnalyzerError as exc:
                log.error(f"  Erro na IA: {exc}")
                resultados.append(
                    ResultadoCandidato(
                        nome=None,
                        contato=None,
                        classificacao="erro_api",
                        pontuacao=0,
                        pontos_positivos=[],
                        pontos_negativos=["IA retornou erro"],
                        justificativa="Erro ao processar com IA.",
                        arquivo_fonte=arquivo_cv.name,
                    )
                )
                estatisticas["erros_api"] += 1
                continue

        except Exception as exc:
            log.exception(f"  Erro inesperado: {exc}")
            estatisticas["erros_parsing"] += 1
            continue

    # === 4. Gerar planilha ===
    if not resultados:
        raise PipelineError("Nenhum resultado gerado (todos os CVs falharam).")

    try:
        caminho_planilha = gerar_planilha_triagem(resultados, vaga.cargo, pasta_saida)
    except ExcelOutputError as exc:
        raise PipelineError(f"Erro ao gerar planilha: {exc}") from exc

    # === Resumo ===
    log.info(f"\nRESUMO DA TRIAGEM (run_id={run_id}):")
    log.info(f"  Total processado: {estatisticas['processados']}/{estatisticas['total']}")
    log.info(f"  Aprovados: {sum(1 for r in resultados if r.classificacao == 'aprovado')}")
    log.info(f"  Verificar: {sum(1 for r in resultados if r.classificacao == 'verificar')}")
    log.info(f"  Reprovados: {sum(1 for r in resultados if r.classificacao == 'reprovado')}")
    log.info(f"  Erros: {estatisticas['erros_parsing'] + estatisticas['erros_api']}")
    log.info(f"  Planilha: {caminho_planilha}")

    return caminho_planilha
```

### Passo 3: Testar

Crie alguns CVs fictícios em `testes/cvs_exemplo/`:

```
testes/cvs_exemplo/
├── joao_silva.pdf         (cria um PDF simples com texto)
├── maria_santos.docx      (cria um DOCX simples)
└── (mais arquivos...)
```

No Python REPL:

```python
from src.fast_triagem_rh.pipeline import rodar_triagem
from pathlib import Path

# Rodar pipeline
resultado = rodar_triagem(
    arquivo_criterios=Path("criterios_vaga_exemplo.xlsx"),
    pasta_cvs=Path("testes/cvs_exemplo"),
    pasta_saida="."
)

print(f"Planilha gerada: {resultado}")
```

Se criar um arquivo `.xlsx` com resultados, passou.

## Checklist de T10

- [ ] Arquivo `src/fast_triagem_rh/pipeline.py` criado
- [ ] Função `rodar_triagem(arquivo_criterios, pasta_cvs, pasta_saida)`
- [ ] Valida critérios com falha rápida
- [ ] Lista arquivos na pasta
- [ ] Identifica tipo (PDF, DOCX, etc.)
- [ ] Parseia cada arquivo
- [ ] Manda para análise (IA)
- [ ] CVs com erro: incluir na planilha com `classificacao="erro_parsing"`, não parar
- [ ] Acumula resultados
- [ ] Chama `gerar_planilha_triagem()` para saída
- [ ] Log por arquivo e resumo final
- [ ] Teste no REPL com pasta fictícia passa
- [ ] Commit feito: `feat(pipeline): orquestrador completo com tratamento de erros`

---

# T11 — CLI (1h)

## O que é

Atualizar `src/fast_triagem_rh/__main__.py` para aceitar argumentos:

```bash
python -m fast_triagem_rh --vaga criterios.xlsx --cvs pasta_cvs/
```

Karina roda isso no terminal (ou duplo-clica um `.bat` que tem esse comando).

## Por que é importante

Sem CLI, Karina teria que editar código ou usar Python REPL. Com CLI, é tão simples quanto clicar.

## Como fazer

### Passo 1: Reescrever `__main__.py`

```python
# src/fast_triagem_rh/__main__.py
"""CLI de triagem de candidatos."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pipeline import rodar_triagem, PipelineError
from .logger import get_logger

log = get_logger(__name__)


def main() -> None:
    """Ponto de entrada da CLI."""
    parser = argparse.ArgumentParser(
        description="Triagem automática de candidatos com IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS:
  python -m fast_triagem_rh --vaga criterios.xlsx --cvs ./cvs/
  python -m fast_triagem_rh -v minha_vaga.xlsx -c ./candidatos/

RESULTADO:
  Arquivo Excel gerado: triagem_<cargo>_<data>.xlsx
        """,
    )

    parser.add_argument(
        "-v",
        "--vaga",
        required=True,
        type=str,
        help="Path do arquivo Excel com critérios (preenchido por Karina)",
    )

    parser.add_argument(
        "-c",
        "--cvs",
        required=True,
        type=str,
        help="Path da pasta contendo CVs (PDF, DOCX, etc.)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="Pasta onde salvar resultado (padrão: pasta atual)",
    )

    args = parser.parse_args()

    # === Validar inputs ===
    arquivo_criterios = Path(args.vaga)
    pasta_cvs = Path(args.cvs)
    pasta_saida = Path(args.output)

    if not arquivo_criterios.exists():
        print(f"ERRO: Arquivo de critérios não encontrado: {arquivo_criterios}")
        sys.exit(1)

    if not pasta_cvs.exists():
        print(f"ERRO: Pasta de CVs não encontrada: {pasta_cvs}")
        sys.exit(1)

    # === Rodar pipeline ===
    try:
        print(f"\n{'='*60}")
        print(f"TRIAGEM DE CANDIDATOS")
        print(f"{'='*60}")
        print(f"Vaga: {arquivo_criterios}")
        print(f"CVs: {pasta_cvs}")
        print(f"Output: {pasta_saida}")
        print(f"{'='*60}\n")

        caminho_resultado = rodar_triagem(arquivo_criterios, pasta_cvs, pasta_saida)

        print(f"\n{'='*60}")
        print(f"SUCESSO!")
        print(f"{'='*60}")
        print(f"Arquivo gerado: {caminho_resultado}")
        print(f"Abra no Excel e revise os candidatos.")
        print(f"{'='*60}\n")

    except PipelineError as exc:
        print(f"\nERRO NA TRIAGEM:")
        print(f"  {exc}")
        sys.exit(1)

    except Exception as exc:
        log.exception("Erro inesperado")
        print(f"\nERRO INESPERADO:")
        print(f"  {exc}")
        print(f"Verifique o log para detalhes.")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Passo 2: Testar

```bash
# Testar help
python -m fast_triagem_rh --help

# Testar com argumentos
python -m fast_triagem_rh --vaga criterios_vaga_exemplo.xlsx --cvs testes/cvs_exemplo/
```

Se der sucesso (gera arquivo `.xlsx`), passou.

### Passo 3: Validar mensagens de erro

```bash
# Testar com arquivo inexistente
python -m fast_triagem_rh --vaga nao_existe.xlsx --cvs ./cvs/

# Output esperado:
# ERRO: Arquivo de critérios não encontrado: nao_existe.xlsx
```

Se erros aparecem com mensagens claras, passou.

## Checklist de T11

- [ ] Arquivo `src/fast_triagem_rh/__main__.py` atualizado com argparse
- [ ] Argumentos: `--vaga` (obrigatório), `--cvs` (obrigatório), `--output` (opcional)
- [ ] Validação de inputs (arquivo/pasta existem?)
- [ ] Mensagens de sucesso e erro claras (sem traceback bruto)
- [ ] Help funciona: `python -m fast_triagem_rh --help`
- [ ] Teste com argumentos válidos passa
- [ ] Teste com argumentos inválidos mostra erro legível
- [ ] Resumo final mostrado (aprovados, verificar, reprovados, erros)
- [ ] Commit feito: `feat(cli): adicionar interface de linha de comando`

---

# Teste Integrado (Fim do Dia Três)

Você finalizou 3 tarefas. Agora testa o fluxo completo.

## Passo 1: Preparar dados fictícios

Crie pasta `testes/cvs_exemplo/` com alguns CVs (pode ser arquivos vazios para teste rápido):

```bash
mkdir -p testes/cvs_exemplo/
echo "João Silva | (11) 98765-4321 | joao@email.com | 6 anos Python" > testes/cvs_exemplo/joao.txt
echo "Maria Santos | (11) 91234-5678 | maria@email.com | 3 anos Python" > testes/cvs_exemplo/maria.txt
```

Crie `criterios_vaga_teste.xlsx` com:
- Linha 1: "Nome da vaga:" | "Engenheiro Python"
- Linha 3: "Nome da etapa:" | "Inscritos"
- Linha 6: Headers (Nome, Sobrenome, E-mail, etc.)

(Ou copie `criterios_vaga_template.xlsx` e preencha)

## Passo 2: Rodar CLI

```bash
python -m fast_triagem_rh --vaga criterios_vaga_teste.xlsx --cvs testes/cvs_exemplo/
```

Esperado:
```
============================================================
TRIAGEM DE CANDIDATOS
============================================================
Vaga: criterios_vaga_teste.xlsx
CVs: testes/cvs_exemplo/
Output: .
============================================================

[1/2] Processando: joao.txt
[2/2] Processando: maria.txt

RESUMO DA TRIAGEM:
  Total processado: 2/2
  Aprovados: X
  Verificar: Y
  Reprovados: Z
  Erros: W

============================================================
SUCESSO!
============================================================
Arquivo gerado: triagem_Engenheiro Python_20260506_153000.xlsx
Abra no Excel e revise os candidatos.
============================================================
```

## Passo 3: Validar arquivo Excel

Abra `triagem_Engenheiro Python_*.xlsx` (nome exato pode variar):
- Deve ter 2 abas: "Resumo" e "Triagem"
- Aba "Triagem" com dados dos 2 candidatos
- Colunas: Nome, Contato, Classificação, Pontuação, Pontos Positivos, Pontos Negativos, Justificativa, Arquivo Fonte, Data
- Cores por classificação

Se arquivo abre e dados estão lá, **Dia Três está completo!**

---

## Resumo do Dia Três

| Tarefa | Tempo | O que sai |
|---|---|---|
| T09 | 2h | Função que gera Excel a partir de `ResultadoCandidato` |
| T10 | 2.5h | Orquestrador que chama tudo em sequência |
| T11 | 1h | CLI para Karina usar (sem saber Python) |
| **Total** | **5.5h** | **MVP Rodando** |

Ao final do dia, você executa `git status` e vê 3 commits:

```
feat(output): gerar planilha Excel com openpyxl
feat(pipeline): orquestrador completo com tratamento de erros
feat(cli): adicionar interface de linha de comando
```

---

**Próximo:** [Dia Quatro — Teste Ponta a Ponta com CVs Reais](GUIA_DIA_QUATRO.md) (a ser criado)

Boa sorte! 🚀
