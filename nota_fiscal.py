import re

from utils import (
    _normalizar_data,
    _validar_chave_nf
)


def extrair_dados_nf(texto):

    chave = ''
    data_emissao = ''

    texto_upper = texto.upper()

    # -------------------------
    # DATA EMISSÃO
    m_emi = re.search(
        r'(EMISS[ÃA]O|DATA DE EMISS[ÃA]O|DATA DOCUMENTO|DATA DO DOCUMENTO|PROCESSAMENTO)[:\s]*(\d{2}/\d{2}/\d{2,4})',
        texto,
        re.I
    )

    if m_emi:
        data_emissao = _normalizar_data(m_emi.group(2))

    else:
        datas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)

        if datas:
            data_emissao = _normalizar_data(datas[0])

    # -------------------------
    # CHAVE DE ACESSO
    matches = re.finditer(r'(\d[\s.]*){44}', texto_upper)

    for match in matches:

        limpo = re.sub(r'\D', '', match.group(0))

        if len(limpo) != 44:
            continue

        if limpo.startswith('000000'):
            continue

        if _validar_chave_nf(limpo):
            chave = limpo
            break

    return {
        'chave_acesso': chave,
        'data_emissao': data_emissao
    }