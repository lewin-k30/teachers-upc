from modelo.estudiante import Estudiante
from repository.estudiante_repository import EstudianteRepository


class EstudianteService:
    def __init__(self):
        self.repo = EstudianteRepository()

    def iniciar_sesion(self, correo, clave):
        estudiantes = self.repo.obtener_todos()
        for e in estudiantes:
            if e.correo.lower() == correo.lower() and e.clave == clave:
                return e
        return None

    def registrar_estudiante(self, nombre, correo, clave):
        estudiantes = self.repo.obtener_todos()

        # Validar si el correo ya está registrado
        for e in estudiantes:
            if e.correo.lower() == correo.lower():
                return None, "El correo ya se encuentra registrado."

        nuevo_id = str(len(estudiantes) + 1)
        nuevo_estudiante = Estudiante(nuevo_id, nombre, correo, clave)
        estudiantes.append(nuevo_estudiante)
        self.repo.guardar_todos(estudiantes)

        return nuevo_estudiante, "Cuenta creada exitosamente."