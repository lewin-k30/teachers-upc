from modelo.docente import Docente
from utils.csv_utils import leer_csv, escribir_csv


class DocenteRepository:
    CAMPOS = ["id", "nombre", "cursos", "foto"]

    def __init__(self, ruta_csv="docentes.csv"):
        self.ruta_csv = ruta_csv

    def obtener_todos(self):
        filas = leer_csv(self.ruta_csv, self.CAMPOS)
        return [Docente.from_dict(f) for f in filas]

    def guardar_todos(self, docentes):
        datos = [d.to_dict() for d in docentes]
        escribir_csv(self.ruta_csv, self.CAMPOS, datos)