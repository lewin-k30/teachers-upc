from modelo.opinion import Opinion
from utils.csv_utils import leer_csv, escribir_csv


class OpinionRepository:
    CAMPOS = ["id", "estudiante_id", "docente_id", "comentario", "puntaje",
              "sentimiento", "confianza"]

    def __init__(self, ruta_csv="opiniones.csv"):
        self.ruta_csv = ruta_csv

    def obtener_todas(self):
        filas = leer_csv(self.ruta_csv, self.CAMPOS)
        return [Opinion.from_dict(f) for f in filas]

    def guardar_todas(self, opiniones):
        datos = [op.to_dict() for op in opiniones]
        escribir_csv(self.ruta_csv, self.CAMPOS, datos)