from modelo.estudiante import Estudiante
from utils.csv_utils import leer_csv, escribir_csv


class EstudianteRepository:
    CAMPOS = ["id", "nombre", "correo", "clave"]

    def __init__(self, ruta_csv="estudiantes.csv"):
        self.ruta_csv = ruta_csv

    def obtener_todos(self):
        filas = leer_csv(self.ruta_csv, self.CAMPOS)
        return [Estudiante.from_dict(f) for f in filas]

    def guardar_todos(self, estudiantes):
        datos = [e.to_dict() for e in estudiantes]
        escribir_csv(self.ruta_csv, self.CAMPOS, datos)