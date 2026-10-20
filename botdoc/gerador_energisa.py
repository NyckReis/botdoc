import pymupdf
import re

FONT_REG = "fonts/LiberationSans-Regular.ttf"
FONT_BOLD = "fonts/LiberationSans-Bold.ttf"

def mascarar_cpf(cpf_raw: str) -> str:
    digits = re.sub(r'\D', '', cpf_raw)
    if len(digits) == 11:
        # Formato padrão Energisa: 12*.***.**7-08
        return f"{digits[:2]}*.***.**{digits[8]}-{digits[9:]}"
    return cpf_raw

def formatar_endereco_energisa(endereco: str) -> str:
    if not endereco:
        return ""
    lines = [l.strip() for l in endereco.splitlines() if l.strip()]
    texto = " ".join(lines)
    texto = re.sub(r'\s+', ' ', texto)

    # Extrai CEP
    cep_match = re.search(r'(?:CEP\s*:?\s*)?(\d{5})[-.\s]?(\d{3})', texto, re.IGNORECASE)
    if cep_match:
        cep_digits = f"{cep_match.group(1)}{cep_match.group(2)}"
        texto_sem_cep = texto[:cep_match.start()] + texto[cep_match.end():]
        texto_sem_cep = re.sub(r'[\s,;\-]+$', '', texto_sem_cep).strip()
    else:
        cep_digits = ""
        texto_sem_cep = texto

    # Divide em logradouro/bairro e cidade/uf
    if cep_digits:
        m_uf = re.search(r'([^-/,]+)\s*[-/]\s*([A-Za-z]{2})$', texto_sem_cep)
        if m_uf:
            cidade = m_uf.group(1).strip().upper()
            uf = m_uf.group(2).strip().upper()
            resto = texto_sem_cep[:m_uf.start()].strip().rstrip(',-').strip().upper()
            return f"{resto}\nCEP {cep_digits} - {cidade}/{uf}"
        else:
            return f"{texto_sem_cep.upper()}\nCEP {cep_digits}"
    else:
        return texto.upper()

def gerar_energisa(
    nome: str,
    cpf: str,
    endereco: str,
    template_path: str = "modelo_energisa.pdf",
    output_path: str = "comprovante_energisa.pdf"
):
    doc = pymupdf.open(template_path)
    page = doc[0]

    page.insert_font(fontname="LibSansReg", fontfile=FONT_REG)
    page.insert_font(fontname="LibSansBold", fontfile=FONT_BOLD)

    nome_clean = nome.strip().upper()
    cpf_mascarado = f"CNPJ/CPF/RANI: {mascarar_cpf(cpf)}"
    endereco_formatado = formatar_endereco_energisa(endereco)

    # Redações limpas:
    # 1. Nome
    page.add_redact_annot(pymupdf.Rect(18.0, 81.0, 210.0, 89.0), fill=(1, 1, 1))
    # 2. Endereço
    page.add_redact_annot(pymupdf.Rect(18.0, 90.0, 210.0, 118.0), fill=(1, 1, 1))
    # 3. CPF
    page.add_redact_annot(pymupdf.Rect(18.0, 125.0, 150.0, 133.0), fill=(1, 1, 1))

    page.apply_redactions()

    # 1. Inserir Nome (Bold 4.0)
    page.insert_text(
        pymupdf.Point(18.75, 86.5),
        nome_clean,
        fontname="LibSansBold",
        fontfile=FONT_BOLD,
        fontsize=4.0,
        color=(0, 0, 0)
    )

    # 2. Inserir Endereço (Regular 4.0)
    page.insert_textbox(
        pymupdf.Rect(18.75, 90.5, 210.0, 118.0),
        endereco_formatado,
        fontname="LibSansReg",
        fontfile=FONT_REG,
        fontsize=4.0,
        color=(0, 0, 0),
        lineheight=1.25
    )

    # 3. Inserir CPF (Regular 4.0)
    page.insert_text(
        pymupdf.Point(18.75, 130.5),
        cpf_mascarado,
        fontname="LibSansReg",
        fontfile=FONT_REG,
        fontsize=4.0,
        color=(0, 0, 0)
    )

    doc.save(output_path)
    return {
        "output_path": output_path,
        "nome": nome_clean,
        "cpf": cpf_mascarado,
        "endereco": endereco_formatado
    }
