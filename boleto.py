import re
from datetime import datetime

from utils import (
    normalizar_texto,
    _extrair_numeros,
    _normalizar_data,
    _modulo10,
    _validar_chave_nf
)


def _validar_linha_digitavel(linha):
    if len(linha) not in (47, 48):
        return False

    if linha.startswith('000'):
        return False

    try:
        # boleto bancário
        if len(linha) == 47:

            campo1 = linha[0:9]
            dv1 = int(linha[9])

            campo2 = linha[10:20]
            dv2 = int(linha[20])

            campo3 = linha[21:31]
            dv3 = int(linha[31])

            return (
                _modulo10(campo1) == dv1 and
                _modulo10(campo2) == dv2 and
                _modulo10(campo3) == dv3
            )

        # arrecadação
        if len(linha) == 48:

            if not linha.startswith('8'):
                return False

            for i in range(4):
                bloco = linha[i*12:(i*12)+11]
                dv = int(linha[(i*12)+11])

                if _modulo10(bloco) != dv:
                    return False

            return True

    except:
        return False

    return False


def extrair_linha_digitavel(texto):
    numeros = _extrair_numeros(texto)

    for i in range(len(numeros) - 46):

        trecho47 = numeros[i:i+47]
        if _validar_linha_digitavel(trecho47):
            return trecho47

        trecho48 = numeros[i:i+48]
        if _validar_linha_digitavel(trecho48):
            return trecho48

    return ''


def linha_digitavel_para_codigo_barras(linha):

    if len(linha) == 47:
        return (
            linha[0:4] +
            linha[32] +
            linha[33:47] +
            linha[4:9] +
            linha[10:20] +
            linha[21:31]
        )

    elif len(linha) == 48:
        return (
            linha[0:11] +
            linha[12:23] +
            linha[24:35] +
            linha[36:47]
        )

    return ''


def extrair_dados_boleto(texto):

    texto = normalizar_texto(texto)

    linha_digitavel = ''
    codigo_barras = ''
    data_vencimento = ''
    data_emissao = ''

    # -------------------------
    # Números candidatos
    candidatos = re.findall(r'[\d\.\s]{30,}', texto)

    for candidato in candidatos:

        num = re.sub(r'\D', '', candidato)

        # Linha digitável
        if len(num) in (47, 48) and not linha_digitavel:

            if _validar_linha_digitavel(num):
                linha_digitavel = num

            continue

        # Código barras 44
        if len(num) == 44 and not codigo_barras:

            if not _validar_chave_nf(num):
                codigo_barras = num

            continue

    # -------------------------
    # Vencimento
    m_venc = re.search(
        r'(VENCIMENTO|DATA DE VENCIMENTO)[^\d]*(\d{2}/\d{2}/\d{4})',
        texto
    )

    if m_venc:
        data_vencimento = _normalizar_data(m_venc.group(2))

    # -------------------------
    # Emissão
    m_emi = re.search(
        r'(EMISS[ÃA]O|DATA DE EMISS[ÃA]O|DOCUMENTO)[^\d]*(\d{2}/\d{2}/\d{4})',
        texto
    )

    if m_emi:
        data_emissao = _normalizar_data(m_emi.group(2))

    else:

        datas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)

        datas_validas = []

        for d in datas:
            try:
                dt = datetime.strptime(d, "%d/%m/%Y")

                if dt.year >= 2020:
                    datas_validas.append(dt)

            except:
                pass

        if datas_validas:

            datas_validas.sort()

            if data_vencimento:

                try:
                    venc = datetime.strptime(
                        data_vencimento,
                        "%d/%m/%Y"
                    )

                    anteriores = [
                        d for d in datas_validas
                        if d <= venc
                    ]

                    if anteriores:
                        data_emissao = anteriores[-1].strftime("%d/%m/%Y")
                    else:
                        data_emissao = datas_validas[0].strftime("%d/%m/%Y")

                except:
                    data_emissao = datas_validas[0].strftime("%d/%m/%Y")

            else:
                data_emissao = datas_validas[0].strftime("%d/%m/%Y")

    # -------------------------
    if not codigo_barras and linha_digitavel:
        codigo_barras = linha_digitavel_para_codigo_barras(linha_digitavel)

    return {
        'linha_digitavel': linha_digitavel,
        'codigo_barras': codigo_barras,
        'data_vencimento': data_vencimento,
        'data_emissao': data_emissao
    }