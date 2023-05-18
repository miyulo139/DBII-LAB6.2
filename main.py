from itertools import islice
import nltk
from nltk.stem.snowball import SnowballStemmer


# nltk.download('punkt')

# Separar las palabras del texto
def tokenizar(text):
    return nltk.word_tokenize(text.lower())


# Remover los stopwords
def clean_text(palabras):
    # Leer StopList
    fileStopList = open('keys/stoplist.txt', 'r')
    StopListTXT = fileStopList.read()
    fileStopList.close()

    stop_list = tokenizar(StopListTXT)
    stop_list += ['.', '?', '¿', '-', '!', '\'', ',', ':', '«', '(', ')',
                  '``', 'con', ';']
    palabras_limpias = []
    for token in palabras:
        if token.lower() not in stop_list:
            palabras_limpias.append(token)
    return palabras_limpias


# Encontrar la raiz(lexema) de las palabras tokenizadas y filtradas
def found_root(palabras):
    stemmer = SnowballStemmer('spanish')
    just_roots = []
    for w in palabras:
        just_roots.append(stemmer.stem(w))
    return just_roots


def load_file(name_file):
    file = open('docs/' + name_file, 'r')
    tokenFile = tokenizar(file.read())
    filtrado = clean_text(tokenFile)
    filtrado = found_root(filtrado)
    file.close()
    return filtrado


def indice_invertido_(docs):
    archivo = open("indiceinvertido.txt", "w")
    indice_invertido = {}
    freq = {}

    # Hallar la frecuencia de cada token
    for libro in docs:
        texto_filtrado = load_file(libro)

        for palabra in texto_filtrado:
            if palabra in freq:
                freq[palabra] = freq[palabra] + 1
            else:
                freq[palabra] = 1

    # Filtrar los 500 más frecuentes
    freq_sort = dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
    freq_sort_500 = dict(islice(freq_sort.items(), 500))
    freq_500 = list(freq_sort_500.keys())

    # Elaborar el índice invertido con los 500 token más frecuentes
    for libro in docs:
        texto_filtrado = load_file(libro)
        for palabra in texto_filtrado:
            if palabra in freq_500:
                if palabra in indice_invertido:
                    indice_invertido[palabra] = indice_invertido[palabra] + [libro]
                else:
                    indice_invertido[palabra] = [libro]
            else:
                continue

    # eliminar repetidos y ordenar
    for key in indice_invertido:
        indice_invertido[key] = sorted(list(set(indice_invertido[key])))
        archivo.write(key + ": " + str(indice_invertido[key]) + '\n')

    return indice_invertido


def L(palabra, indiceinvertido):
    stemmer = SnowballStemmer('spanish')
    palabra_root = stemmer.stem(palabra.lower())
    if palabra_root in indiceinvertido:
        return indiceinvertido[palabra_root]
    else:
        return []


def AND(lista1, lista2):
    c1 = 0
    c2 = 0
    result = []
    while c1 < len(lista1) and c2 < len(lista2):
        if lista1[c1] == lista2[c2]:
            result.append(lista1[c1])
            c1 += 1
            c2 += 1
        elif lista1[c1] < lista2[c2]:
            c1 += 1
        else:
            c2 += 1
    return result


def OR(lista1, lista2):
    # contadores:
    c1 = 0
    c2 = 0
    result = []
    while c1 < len(lista1) and c2 < len(lista2):
        if lista1[c1] == lista2[c2]:
            result.append(lista1[c1])
            c1 += 1
            c2 += 1
        elif lista1[c1] < lista2[c2]:
            result.append(lista1[c1])
            c1 += 1
        else:
            result.append(lista2[c2])
            c2 += 1

    while c1 < len(lista1):
        result.append(lista1[c1])
        c1 += 1

    while c2 < len(lista2):
        result.append(lista2[c2])
        c2 += 1

    return result


def AND_NOT(lista1, lista2):
    c1 = 0
    c2 = 0
    result = []
    while c1 < len(lista1) and c2 < len(lista2):
        if lista1[c1] == lista2[c2]:
            c1 += 1
            c2 += 1
        elif lista1[c1] < lista2[c2]:
            result.append(lista1[c1])
            c1 += 1
        else:
            c2 += 1

    while c1 < len(lista1):
        result.append(lista1[c1])
        c1 += 1

    return result


libros = ["libro1.txt", "libro2.txt", "libro3.txt", "libro4.txt", "libro5.txt", "libro6.txt"]
indice = indice_invertido_(libros)

# ============================================================================================

# TESTS
# CONSULTA 1
result = AND_NOT(AND(L("Gandalf", indice), L("Boromir", indice)), L("Gollum", indice))
print("Libros recuperados de la consulta 1: ", result)  # ['libro2.txt', 'libro3.txt', 'libro5.txt']

# CONSULTA 2
result = AND(OR(L("muerte", indice), L("batalla", indice)), L("ataque", indice))
print("Libros recuperados de la consulta 2: ", result)  # ['libro3.txt', 'libro5.txt']

# CONSULTA 3
result = AND_NOT(AND(OR(L("herencia", indice), L("batalla", indice)), L("anillo", indice)), L("fuerza", indice))
print("Libros recuperados de la consulta 3: ", result)  # ['libro1.txt', 'libro6.txt']
