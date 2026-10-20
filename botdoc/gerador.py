import pymupdf
import re
import random

FONT_REG = "fonts/OpenSans-Regular.ttf"
FONT_BOLD = "fonts/OpenSans-Bold.ttf"

COLOR_PURPLE = (138/255, 5/255, 190/255)
COLOR_TEXT = (34/255, 34/255, 34/255)
FONT_SIZE = 6.7525

def format_cpf(cpf_raw: str) -> str:
    digits = re.sub(r'\D', '', cpf_raw)
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    return cpf_raw.strip()

def formatar_estilo_nubank_exato(endereco: str) -> str:
    """
    Padroniza qualquer endereço no padrão idêntico do Nubank:
    - Transforma 'Rua' em 'R.' e 'Avenida' em 'Av.'
    - Troca barras de estado por hífen (ex: Aracaju/SE -> Aracaju - SE)
    - Remove a palavra 'CEP' e formata como 00000-000 no final
    - Mantém em linha única contínua
    Exemplo original: R. Ariperana, 119a - Taquara, Rio de Janeiro - RJ, 22725-530
    """
    if not endereco:
        return ""

    lines = [l.strip() for l in endereco.splitlines() if l.strip()]
    texto = " ".join(lines)
    texto = re.sub(r'\s+', ' ', texto)

    # 1. Abreviação padrão: Rua -> R. | Avenida -> Av.
    texto = re.sub(r'^(?:Rua|r\.)\s+', 'R. ', texto, flags=re.IGNORECASE)
    texto = re.sub(r'^(?:Avenida|av\.)\s+', 'Av. ', texto, flags=re.IGNORECASE)
    texto = re.sub(r'^Av\s+', 'Av. ', texto, flags=re.IGNORECASE)

    # 2. Trata CEP: remove 'CEP' e formata 00000-000 no final com vírgula
    cep_match = re.search(r'(?:CEP\s*:?\s*)?(\d{5})[-.\s]?(\d{3})', texto, re.IGNORECASE)
    if cep_match:
        cep_formatado = f"{cep_match.group(1)}-{cep_match.group(2)}"
        texto = texto[:cep_match.start()] + texto[cep_match.end():]
        texto = re.sub(r'[\s,;\-]+$', '', texto).strip()
        texto = f"{texto}, {cep_formatado}"

    # 3. Troca barra antes de UF por hífen: /SE -> - SE
    texto = re.sub(r'/\s*([A-Za-z]{2})\b', r' - \1', texto)

    # 4. Garante UF em maiúsculo
    texto = re.sub(r'-\s*([a-z]{2})\b', lambda m: f'- {m.group(1).upper()}', texto)
    texto = re.sub(r',\s*,+', ', ', texto)
    texto = re.sub(r'-\s*-+', '- ', texto)
    texto = re.sub(r'\s+', ' ', texto)

    return texto.strip()

def gerar_saldo_alto_aleatorio() -> str:
    inteiro = random.randint(4500, 28500)
    centavos = random.randint(10, 95)
    total = inteiro + (centavos / 100.0)
    return f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_conta_aleatoria() -> str:
    num = random.randint(10000000, 99999999)
    dig = random.randint(0, 9)
    return f"{num}-{dig}"

def gerar_comprovante(
    nome: str,
    cpf: str,
    endereco: str,
    template_path: str = "modelo.pdf",
    output_path: str = "comprovante_gerado.pdf"
):
    doc = pymupdf.open(template_path)
    page = doc[0]

    page.insert_font(fontname="OSRegular", fontfile=FONT_REG)
    page.insert_font(fontname="OSBold", fontfile=FONT_BOLD)

    nome_clean = nome.strip()
    cpf_formatted = format_cpf(cpf)
    endereco_linha_unica = formatar_estilo_nubank_exato(endereco)

    # Gera conta e saldo alto aleatórios
    conta_gerada = gerar_conta_aleatoria()
    saldo_gerado = f"R$ {gerar_saldo_alto_aleatorio()}"

    # 1. Topo: nome da pessoa em maiúsculo na cor roxa oficial Nubank
    rect_header = pymupdf.Rect(135.0, 78.0, 305.0, 96.0)
    page.add_redact_annot(rect_header, fill=(1, 1, 1))

    # 2. Nome
    rect_nome = pymupdf.Rect(84.5, 177.0, 300.0, 191.0)
    page.add_redact_annot(rect_nome, fill=(1, 1, 1))

    # 3. CPF
    rect_cpf = pymupdf.Rect(76.5, 196.0, 250.0, 210.0)
    page.add_redact_annot(rect_cpf, fill=(1, 1, 1))

    # 4. Conta
    rect_conta = pymupdf.Rect(84.5, 253.0, 200.0, 267.0)
    page.add_redact_annot(rect_conta, fill=(1, 1, 1))

    # 5. Saldo
    rect_saldo_val = pymupdf.Rect(204.0, 291.0, 300.0, 305.0)
    page.add_redact_annot(rect_saldo_val, fill=(1, 1, 1))

    # 6. Endereço: limpa toda a linha horizontalmente e verticalmente
    rect_end = pymupdf.Rect(95.5, 310.0, 560.0, 335.0)
    page.add_redact_annot(rect_end, fill=(1, 1, 1))

    page.apply_redactions()

    # Re-inserções:
    # 1. Topo em roxo
    page.insert_text(
        pymupdf.Point(136.78, 90.5),
        nome_clean.upper(),
        fontname="OSBold",
        fontfile=FONT_BOLD,
        fontsize=FONT_SIZE,
        color=COLOR_PURPLE
    )

    # 2. Nome
    page.insert_text(
        pymupdf.Point(84.89, 186.4),
        " " + nome_clean,
        fontname="OSRegular",
        fontfile=FONT_REG,
        fontsize=FONT_SIZE,
        color=COLOR_TEXT
    )

    # 3. CPF
    page.insert_text(
        pymupdf.Point(76.84, 205.3),
        " " + cpf_formatted,
        fontname="OSRegular",
        fontfile=FONT_REG,
        fontsize=FONT_SIZE,
        color=COLOR_TEXT
    )

    # 4. Conta
    page.insert_text(
        pymupdf.Point(84.56, 262.0),
        " " + conta_gerada,
        fontname="OSRegular",
        fontfile=FONT_REG,
        fontsize=FONT_SIZE,
        color=COLOR_TEXT
    )

    # 5. Saldo
    page.insert_text(
        pymupdf.Point(204.36, 299.8),
        " " + saldo_gerado,
        fontname="OSRegular",
        fontfile=FONT_REG,
        fontsize=FONT_SIZE,
        color=COLOR_TEXT
    )

    # 6. Endereço no padrão idêntico do Nubank em linha única
    page.insert_text(
        pymupdf.Point(95.88, 318.7),
        " " + endereco_linha_unica,
        fontname="OSRegular",
        fontfile=FONT_REG,
        fontsize=FONT_SIZE,
        color=COLOR_TEXT
    )

    doc.save(output_path)
    return {
        "output_path": output_path,
        "nome": nome_clean,
        "cpf": cpf_formatted,
        "conta": conta_gerada,
        "saldo": saldo_gerado,
        "endereco": endereco_linha_unica
    }
