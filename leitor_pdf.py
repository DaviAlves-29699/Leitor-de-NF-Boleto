import io
import pdfplumber

def extrair_texto_pdf(alvo):

    paginas = []

    try:
        with pdfplumber.open(alvo) as pdf:

            for pagina in pdf.pages[:5]:   # limita páginas

                try:
                    texto = pagina.extract_text()

                    if texto:
                        paginas.append(texto)

                except:
                    continue

    except:
        return ''

    return '\n'.join(paginas)