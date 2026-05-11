import re

from leitor_pdf import extrair_texto_pdf
from boleto import extrair_dados_boleto
from nota_fiscal import extrair_dados_nf
from utils import validar_chave_nf


def classificar_documento(texto):

    t = texto.upper()

    sb = 0
    snf = 0
    sr = 0

    # BOLETO
    
    termos_boleto = [
        'LINHA DIGITAVEL',
        'LINHA DIGITÁVEL',
        'FICHA DE COMPENSAÇÃO',
        'NOSSO NÚMERO',
        'VENCIMENTO',
        'PAGÁVEL',
        'AUTENTICAÇÃO MECÂNICA',
        'BENEFICIÁRIO',
        'CEDENTE',
        'SACADO'
    ]

    for termo in termos_boleto:
        if termo in t:
            sb += 15

    # NOTA FISCAL
    
    termos_nf = [
        'DANFE',
        'DOCUMENTO AUXILIAR DA NOTA FISCAL',
        'NOTA FISCAL',
        'NOTA FISCAL ELETRONICA',
        'NOTA FISCAL ELETRÔNICA',
        'NFS-E',
        'NFSE',
        'CHAVE DE ACESSO',
        'PROTOCOLO',
        'PROTOCOLO DE AUTORIZAÇÃO',
        'NATUREZA DA OPERAÇÃO',
        'VALOR TOTAL DA NOTA',
        'BASE DE CÁLCULO DO ICMS',
        'ICMS',
        'EMITENTE',
        'DESTINATÁRIO',
        'SÉRIE'
    ]

    for termo in termos_nf:
        if termo in t:
            snf += 15

    # CHAVE NF VÁLIDA
    
    numeros = re.findall(r'(\d[\d\s\.-]{40,})', t)

    for trecho in numeros:

        limpo = re.sub(r'\D', '', trecho)

        if len(limpo) >= 44:

            for i in range(len(limpo) - 43):

                chave = limpo[i:i+44]

                if validar_chave_nf(chave):

                    if any(x in t for x in [
                        'DANFE',
                        'NOTA FISCAL',
                        'CHAVE DE ACESSO',
                        'PROTOCOLO',
                        'EMITENTE'
                    ]):
                        snf += 90
                    break

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

    nome = caminho_pdf.upper()
    t = texto.upper()

    dados_boleto = extrair_dados_boleto(texto)
    dados_nf = extrair_dados_nf(texto)

    linha = dados_boleto.get('linha_digitavel', '')
    tem_linha = bool(linha)

    chave_nf = dados_nf.get('chave_acesso', '')
    tem_chave_nf = bool(chave_nf)

    # CONTEXTO
    termos_boleto = [
        'LINHA DIGITAVEL',
        'LINHA DIGITÁVEL',
        'FICHA DE COMPENSAÇÃO',
        'CEDENTE',
        'BENEFICIÁRIO',
        'NOSSO NÚMERO',
        'VENCIMENTO',
        'SACADO'
    ]

    termos_nf = [
        'DANFE',
        'NOTA FISCAL',
        'NFS-E',
        'CHAVE DE ACESSO',
        'PROTOCOLO',
        'EMITENTE',
        'DESTINATÁRIO'
    ]

    qtd_boleto = sum(1 for x in termos_boleto if x in t)
    qtd_nf = sum(1 for x in termos_nf if x in t)

    # PRIORIDADE 1 - NOME DO ARQUIVO

    if 'BOLETO' in nome:
        return {
            'tipo': 'BOLETO',
            'confianca': 100,
            **dados_boleto
        }

    if (
        'NOTA FISCAL' in nome
        or 'DANFE' in nome
        or 'NFS-E' in nome
        or 'NFCOM' in nome
        or re.search(r'(^|[^A-Z0-9])NF([^A-Z0-9]|$)', nome)
    ):
        return {
            'tipo': 'NOTA_FISCAL',
            'confianca': 100,
            **dados_nf
        }

    # PRIORIDADE 2 - DADOS FORTES

    # boleto só se tiver linha + contexto boleto
    if tem_linha and (
        'VENCIMENTO' in texto.upper()
        or 'LINHA DIGITAVEL' in texto.upper()
        or 'BENEFICIÁRIO' in texto.upper()
    ):
        return {
            'tipo': 'BOLETO',
            'confianca': 95,
            **dados_boleto
        }

    # NF só se tiver chave + contexto fiscal
    if tem_chave_nf and qtd_nf >= 1:
        return {
            'tipo': 'NOTA_FISCAL',
            'confianca': 95,
            **dados_nf
        }

    # PRIORIDADE 3 - SCORE

    sb, snf, sr = classificar_documento(texto)

    if snf >= 60 and snf > sb:
        return {
            'tipo': 'NOTA_FISCAL',
            'confianca': snf,
            **dados_nf
        }

    if sb >= 60 and sb > snf:
        return {
            'tipo': 'BOLETO',
            'confianca': sb,
            **dados_boleto
        }

    if sr >= 20:
        return {
            'tipo': 'OUTROS',
            'confianca': sr,
            'descricao': 'Recibo / Comprovante'
        }

    # FINAL

    return {
        'tipo': 'DESCONHECIDO',
        'confianca': 0,
        'erro': 'Documento não identificado'
    }