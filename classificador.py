import re

from leitor_pdf import extrair_texto_pdf
from boleto import extrair_dados_boleto, extrair_linha_digitavel
from nota_fiscal import extrair_dados_nf
from utils import _validar_chave_nf


def _classificar_documento(texto):

    t = texto.upper()

    sb = 0
    snf = 0
    sr = 0

    # -------------------------
    # BOLETO
    termos_boleto = [
        'LINHA DIGITAVEL',
        'FICHA DE COMPENSAÇÃO',
        'NOSSO NÚMERO',
        'VENCIMENTO',
        'PAGÁVEL',
        'AUTENTICAÇÃO MECÂNICA',
        'BENEFICIÁRIO',
        'CEDENTE'
    ]

    for termo in termos_boleto:
        if termo in t:
            sb += 15

    if extrair_linha_digitavel(t):
        sb += 70

    # -------------------------
    # NOTA FISCAL
    termos_nf = [
        'DANFE',
        'DOCUMENTO AUXILIAR DA NOTA FISCAL',
        'NOTA FISCAL',
        'NOTA FISCAL ELETRONICA',
        'NOTA FISCAL ELETRÔNICA',
        'CHAVE DE ACESSO',
        'PROTOCOLO DE AUTORIZAÇÃO',
        'NATUREZA DA OPERAÇÃO',
        'VALOR TOTAL DA NOTA',
        'BASE DE CÁLCULO DO ICMS',
        'ICMS',
        'EMITENTE',
        'DESTINATÁRIO'
    ]

    for termo in termos_nf:
        if termo in t:
            snf += 15

    # busca chave NF válida
    numeros = re.findall(r'(\d[\d\s\.-]{40,})', t)

    for trecho in numeros:

        limpo = re.sub(r'\D', '', trecho)

        if len(limpo) >= 44:

            for i in range(len(limpo) - 43):

                chave = limpo[i:i+44]

                if _validar_chave_nf(chave):

                    if any(x in t for x in [
                        'DANFE',
                        'NOTA FISCAL',
                        'CHAVE DE ACESSO',
                        'EMITENTE',
                        'DESTINATÁRIO',
                        'PROTOCOLO'
                    ]):
                        snf += 90
                    break

    # NFS-e
    if 'NFS-E' in t or 'NOTA FISCAL DE SERVIÇOS' in t:
        snf += 50

    # reduz score NF se parecer boleto
    if 'LINHA DIGITAVEL' in t:
        snf -= 30

    # -------------------------
    # OUTROS
    termos_outros = [
        'RECIBO',
        'COMPROVANTE',
        'DEVOLUÇÃO',
        'DECLARAÇÃO'
    ]

    for termo in termos_outros:
        if termo in t:
            sr += 20

    # limites
    sb = max(0, min(sb, 100))
    snf = max(0, min(snf, 100))
    sr = max(0, min(sr, 100))

    return sb, snf, sr


def processar_documento(caminho_pdf):

    texto = extrair_texto_pdf(caminho_pdf)

    if not texto:
        return {
            'tipo': 'DESCONHECIDO',
            'confianca': 0,
            'erro': 'PDF sem texto'
        }

    sb, snf, sr = _classificar_documento(texto)

    dados_boleto = extrair_dados_boleto(texto)
    dados_nf = extrair_dados_nf(texto)

    # -------------------------
    # NOTA FISCAL TEM PRIORIDADE SE SCORE MAIOR
    termos_nf = [
        'DANFE',
        'CHAVE DE ACESSO',
        'NOTA FISCAL',
        'EMITENTE',
        'DESTINATÁRIO',
        'PROTOCOLO',
        'ICMS'
    ]

    qtd = sum(1 for x in termos_nf if x in texto.upper())

    if dados_nf['chave_acesso'] and qtd >= 2:
        return {
            'tipo': 'NOTA_FISCAL',
            'confianca': snf,
            **dados_nf
        }

    # -------------------------
    # BOLETO
    if dados_boleto['linha_digitavel'] and sb > 0:
        return {
            'tipo': 'BOLETO',
            'confianca': sb,
            **dados_boleto
        }

    # -------------------------
    # OUTROS
    if sr >= 20:
        return {
            'tipo': 'OUTROS',
            'confianca': sr,
            'descricao': 'Recibo / Comprovante'
        }

    # -------------------------
    return {
        'tipo': 'DESCONHECIDO',
        'confianca': 0,
        'erro': 'Documento não identificado'
    }