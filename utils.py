import re

def normalizar_texto(texto):
    if not texto:
        return ""
    texto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    texto = re.sub(r'\s+', ' ', texto)
    return texto.upper().strip()

def extrair_numeros(texto):
    return re.sub(r'\D', '', texto)

def normalizar_data(raw):
    raw = raw.strip()

    m = re.match(r'^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$', raw)
    if m:
        return f"{int(m.group(3)):02d}/{int(m.group(2)):02d}/{m.group(1)}"

    m = re.match(r'^(\d{1,2})[-/.](\d{1,2})[-/.](\d{2})$', raw)
    if m:
        return f"{int(m.group(1)):02d}/{int(m.group(2)):02d}/20{m.group(3)}"

    m = re.match(r'^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$', raw)
    if m:
        return f"{int(m.group(1)):02d}/{int(m.group(2)):02d}/{m.group(3)}"

    return raw

def modulo10(numero):
    soma = 0
    peso = 2

    for n in reversed(numero):
        calc = int(n) * peso

        if calc > 9:
            calc = sum(map(int, str(calc)))

        soma += calc
        peso = 1 if peso == 2 else 2

    resto = soma % 10
    return 0 if resto == 0 else 10 - resto

def modulo11_nfe(chave):
    if len(chave) != 44:
        return False

    pesos = [2,3,4,5,6,7,8,9] * 6
    soma = 0

    for i, n in enumerate(reversed(chave[:-1])):
        soma += int(n) * pesos[i % 8]

    resto = soma % 11
    dv = 11 - resto

    if dv >= 10:
        dv = 0

    return dv == int(chave[-1])

def validar_chave_nf(chave):
    return len(chave) == 44 and chave.isdigit() and modulo11_nfe(chave)