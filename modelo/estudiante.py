class Estudiante:
    def __init__(self, id_estudiante, nombre, correo, clave):
        self.id = str(id_estudiante)
        self.nombre = nombre
        self.correo = correo
        self.clave = clave

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "clave": self.clave
        }

    @staticmethod
    def from_dict(datos):
        return Estudiante(datos["id"], datos["nombre"], datos["correo"], datos["clave"])