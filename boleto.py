import re
from datetime import datetime

from utils import (
    normalizar_texto,
    extrair_numeros,
    normalizar_data,
    modulo10,
    validar_chave_nf
)


# =====================================================
# VALIDAÇÃO LINHA DIGITÁVEL
# =====================================================

def validar_linha_digitavel(linha):
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
                modulo10(campo1) == dv1 and
                modulo10(campo2) == dv2 and
                modulo10(campo3) == dv3
            )

        # arrecadação
        if len(linha) == 48:

            if not linha.startswith('8'):
                return False

            for i in range(4):
                bloco = linha[i*12:(i*12)+11]
                dv = int(linha[(i*12)+11])

                if modulo10(bloco) != dv:
                    return False

            return True

    except:
        return False

    return False


# =====================================================
# EXTRAI LINHA DIGITÁVEL REAL
# =====================================================

def extrair_linha_digitavel(texto):
    numeros = extrair_numeros(texto)

    for i in range(len(numeros) - 46):

        trecho47 = numeros[i:i+47]
        if validar_linha_digitavel(trecho47):
            return trecho47

        trecho48 = numeros[i:i+48]
        if validar_linha_digitavel(trecho48):
            return trecho48

    return ''


# =====================================================
# CONVERTE PARA CÓDIGO BARRAS
# =====================================================

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


# =====================================================
# CONTEXTO DE BOLETO
# =====================================================

def score_contexto_boleto(texto):
    t = texto.upper()

    termos = [
        'LINHA DIGITAVEL',
        'LINHA DIGITÁVEL',
        'FICHA DE COMPENSAÇÃO',
        'NOSSO NÚMERO',
        'VENCIMENTO',
        'PAGÁVEL',
        'BENEFICIÁRIO',
        'CEDENTE',
        'SACADO'
    ]

    return sum(1 for termo in termos if termo in t)


# =====================================================
# EXTRAÇÃO PRINCIPAL
# =====================================================

def extrair_dados_boleto(texto):

    texto = normalizar_texto(texto)

    linha_digitavel = ''
    codigo_barras = ''
    data_vencimento = ''
    data_emissao = ''

    contexto = score_contexto_boleto(texto)

    # -------------------------------------------------
    # 1 - linha digitável válida
    # -------------------------------------------------
    linha_digitavel = extrair_linha_digitavel(texto)

    if linha_digitavel:
        codigo_barras = linha_digitavel_para_codigo_barras(
            linha_digitavel
        )

    # -------------------------------------------------
    # 2 - se não tem linha e contexto fraco = não boleto
    # -------------------------------------------------
    if not linha_digitavel and contexto < 2:
        return {
            'linha_digitavel': '',
            'codigo_barras': '',
            'data_vencimento': '',
            'data_emissao': ''
        }

    # -------------------------------------------------
    # 3 - procurar código barras 44 somente se contexto
    # -------------------------------------------------
    if not codigo_barras:

        candidatos = re.findall(r'\d{44}', extrair_numeros(texto))

        for num in candidatos:

            if validar_chave_nf(num):
                continue

            if num[0] in '123456789':
                codigo_barras = num
                break

    # -------------------------------------------------
    # 4 - vencimento
    # -------------------------------------------------
    m_venc = re.search(
        r'(VENCIMENTO|DATA DE VENCIMENTO)[^\d]*(\d{2}/\d{2}/\d{4})',
        texto,
        re.I
    )

    if m_venc:
        data_vencimento = normalizar_data(m_venc.group(2))

    # -------------------------------------------------
    # 5 - emissão
    # -------------------------------------------------
    m_emi = re.search(
        r'(EMISS[ÃA]O|DATA DE EMISS[ÃA]O)[^\d]*(\d{2}/\d{2}/\d{4})',
        texto,
        re.I
    )

    if m_emi:
        data_emissao = normalizar_data(m_emi.group(2))

    # fallback inteligente
    if not data_emissao:

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
            data_emissao = datas_validas[0].strftime("%d/%m/%Y")

    return {
        'linha_digitavel': linha_digitavel,
        'codigo_barras': codigo_barras,
        'data_vencimento': data_vencimento,
        'data_emissao': data_emissao
    }