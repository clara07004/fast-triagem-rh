# Gera 3 currículos fictícios (.docx) na área de trabalho, em teste_triagem/,
# para validar a triagem da vaga "Auxiliar Administrativo Comercial - Centro/RJ"
# em produção. Um candidato forte (aprovado), um ambíguo (verificar) e um fora
# do perfil (reprovado). Rodar: python scripts/gerar_cvs_teste.py
from pathlib import Path

from docx import Document

PASTA = Path.home() / "Desktop" / "teste_triagem"


def cv(nome_arquivo: str, linhas: list[tuple[str, str]]) -> None:
    doc = Document()
    for estilo, texto in linhas:
        if estilo == "h":
            doc.add_heading(texto, level=1)
        elif estilo == "h2":
            doc.add_heading(texto, level=2)
        else:
            doc.add_paragraph(texto)
    doc.save(PASTA / nome_arquivo)
    print("criado:", PASTA / nome_arquivo)


def main() -> None:
    PASTA.mkdir(parents=True, exist_ok=True)

    # 1) Candidata forte — espera-se APROVADO
    cv(
        "cv_mariana_lopes.docx",
        [
            ("h", "Mariana Lopes da Silva"),
            ("p", "Rio de Janeiro - RJ (Centro) | (21) 98888-1111 | mariana.lopes.teste@email.com"),
            ("h2", "Objetivo"),
            ("p", "Atuar como Auxiliar Administrativo na área comercial, em regime presencial."),
            ("h2", "Formação"),
            (
                "p",
                "Ensino médio completo (2018). Superior em Administração em andamento — "
                "4º período, Estácio (noturno).",
            ),
            ("h2", "Experiência profissional"),
            (
                "p",
                "Auxiliar Administrativo Comercial — Casa & Construção Materiais (2021-2025): "
                "rotinas administrativas do setor comercial, emissão de pedidos e notas, "
                "controle de planilhas de vendas em Excel (PROCV e tabela dinâmica), "
                "elaboração de propostas no Word, atendimento a clientes e suporte ao time "
                "de vendas, atualização de cadastros no CRM (RD Station).",
            ),
            (
                "p",
                "Recepcionista — Clínica Recanto (2019-2021): agendamento, atendimento ao "
                "público e organização de documentos.",
            ),
            ("h2", "Conhecimentos"),
            (
                "p",
                "Pacote Office (Word e Excel intermediário/avançado), CRM RD Station, noções "
                "de materiais de construção. Disponibilidade imediata para trabalho "
                "presencial no Centro do Rio.",
            ),
        ],
    )

    # 2) Candidato ambíguo — espera-se VERIFICAR
    cv(
        "cv_pedro_santana.docx",
        [
            ("h", "Pedro Santana Ribeiro"),
            ("p", "Niterói - RJ | (21) 97777-2222 | pedro.santana.teste@email.com"),
            ("h2", "Formação"),
            ("p", "Ensino médio completo (2020)."),
            ("h2", "Experiência profissional"),
            (
                "p",
                "Assistente de loja — Ótica Visão Clara, Niterói (2023-2024, 14 meses): "
                "atendimento ao cliente, organização de cadastros de clientes, lançamento "
                "de vendas no sistema da loja e apoio ao gerente em tarefas do dia a dia.",
            ),
            (
                "p",
                "Jovem aprendiz administrativo — Escritório contábil (2021-2022): arquivo de "
                "documentos, digitação e apoio geral ao escritório.",
            ),
            ("h2", "Conhecimentos"),
            (
                "p",
                "Informática básica e digitação. Curso livre de informática (Word). Busco "
                "oportunidade na área administrativa.",
            ),
        ],
    )

    # 3) Candidato fora do perfil — espera-se REPROVADO
    cv(
        "cv_carlos_meneses.docx",
        [
            ("h", "Carlos Meneses Filho"),
            ("p", "Duque de Caxias - RJ | (21) 96666-3333 | carlos.meneses.teste@email.com"),
            ("h2", "Formação"),
            ("p", "Ensino fundamental completo. Curso de NR-35 (trabalho em altura)."),
            ("h2", "Experiência profissional"),
            (
                "p",
                "Ajudante de obra — Construtora Horizonte (2019-2024): apoio a pedreiros e "
                "carpinteiros, carga e descarga de materiais, limpeza e organização do "
                "canteiro de obras.",
            ),
            (
                "p",
                "Auxiliar de produção — Fábrica de esquadrias (2016-2019): operação de "
                "máquina de corte e montagem de peças.",
            ),
            ("h2", "Conhecimentos"),
            (
                "p",
                "Experiência em canteiro de obras e produção. Não tenho experiência com "
                "computador.",
            ),
        ],
    )

    print()
    print("3 arquivos prontos em", PASTA)


if __name__ == "__main__":
    main()
