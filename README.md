# Smart PDF Document Classifier

Sistema em Python para leitura, extração e classificação automática de documentos PDF.

O projeto identifica documentos como:

- Boletos Bancários
- Notas Fiscais (NF-e / NFS-e / NFCOM)
- Recibos / Comprovantes
- Documentos desconhecidos

Além disso, realiza extração automática de informações importantes.

---

# Funcionalidades

## Boletos

- Detecta boletos por conteúdo e nome do arquivo
- Extrai linha digitável
- Gera código de barras
- Extrai data de vencimento
- Extrai data de emissão

## Notas Fiscais

- Detecta NF-e, NFS-e e NFCOM
- Extrai chave de acesso
- Extrai data de emissão

## Outros Documentos

- Recibos
- Comprovantes
- Declarações
- Devoluções

## Processamento em Lote

Lê automaticamente todos os PDFs de uma pasta.

---

# Tecnologias Utilizadas

- Python 
- pdfplumber

---

# Estrutura do Projeto

```bash
projeto/
│── main.py
│── classificador.py
│── boleto.py
│── nota_fiscal.py
│── leitor_pdf.py
│── utils.py
│── requirements.txt
│── README.md
│── arquivos/