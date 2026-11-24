class Docente:
    def __init__(self, id_docente, nombre, cursos, foto):
        self.id = str(id_docente)
        self.nombre = nombre
        if isinstance(cursos, str):
            self.cursos = [c.strip() for c in cursos.split(";") if c.strip()]
        else:
            self.cursos = cursos
        self.foto = foto
        self.opiniones = []
        self.puntaje_general = 0.0

    def calcular_puntaje_general(self):
        """Promedio simple. El promedio que se muestra en pantalla lo calcula
        AgenteService.calcular_puntaje_ponderado (ver OpinionService)."""
        if not self.opiniones:
            self.puntaje_general = 0.0
            return 0.0
        suma = sum(int(op.puntaje) for op in self.opiniones)
        self.puntaje_general = round(suma / len(self.opiniones), 1)
        return self.puntaje_general

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cursos": ";".join(self.cursos),
            "foto": self.foto
        }

    @staticmethod
    def from_dict(datos):
        return Docente(datos["id"], datos["nombre"], datos["cursos"], datos["foto"])