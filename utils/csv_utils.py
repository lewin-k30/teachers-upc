import csv
import os


def leer_csv(ruta, campos):
    if not os.path.exists(ruta):
        return []

    with open(ruta, mode='r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        return list(lector)


def escribir_csv(ruta, campos, datos):
    with open(ruta, mode='w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(datos)