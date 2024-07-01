
import random

lista_nums_aleatorios = []

for i in range(10):

        lista_nums_aleatorios.append(random.randint(0,9999))

string_lista = ",".join(str(elemento) for elemento in lista_nums_aleatorios)

f = open("teste.txt", "w", encoding="utf-8")

f.write(string_lista)

print(lista_nums_aleatorios)

print(len(lista_nums_aleatorios))

f.close()

caminho_arquivo = "teste.txt"

t = open("teste.txt", "r", encoding="utf-8")

