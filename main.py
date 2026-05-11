import os

from classificador import processar_documento


def main():

    pasta = "./arquivos"

    print(f"Lendo arquivos de: {pasta}")

    try:
        arquivos = [
            f for f in os.listdir(pasta)
            if f.lower().endswith('.pdf')
        ]

    except Exception as erro:
        print(f"Erro ao acessar pasta: {erro}")
        return

    if not arquivos:
        print("Nenhum PDF encontrado.")
        return

    for arquivo in arquivos:

        caminho = os.path.join(pasta, arquivo)

        resultado = processar_documento(caminho)

        print("=" * 60)
        print(f"Arquivo: {arquivo}")

        tipo = resultado.get('tipo', 'DESCONHECIDO')

        print(f"Tipo Identificado: {tipo}")

        if tipo == 'NOTA_FISCAL':

            print(f"Chave Acesso: {resultado.get('chave_acesso')}")
            print(f"Data Emissão: {resultado.get('data_emissao')}")

        elif tipo == 'BOLETO':

            print(f"Linha Digitável: {resultado.get('linha_digitavel')}")
            print(f"Código Barras: {resultado.get('codigo_barras')}")
            print(f"Data Vencimento: {resultado.get('data_vencimento')}")
            print(f"Data Emissão: {resultado.get('data_emissao')}")

        elif tipo == 'OUTROS':

            print(f"Descrição: {resultado.get('descricao')}")

        else:

            print(f"Status: {resultado.get('erro')}")

        print(f"DEBUG → confiança: {resultado.get('confianca')}")


if __name__ == "__main__":
    main()