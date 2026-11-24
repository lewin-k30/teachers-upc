from repository.docente_repository import DocenteRepository


class DocenteService:
    def __init__(self):
        self.repo = DocenteRepository()

    def obtener_docentes(self):
        return self.repo.obtener_todos()

    def buscar_por_nombre(self, texto_busqueda):
        docentes = self.repo.obtener_todos()
        resultado = [
            d for d in docentes
            if texto_busqueda.lower() in d.nombre.lower()
        ]
        return resultado

    def buscar(self, texto_busqueda):
        """Busca por nombre del docente o por curso (lo que pide el buscador de la web)."""
        texto = texto_busqueda.lower().strip()
        return [
            d for d in self.repo.obtener_todos()
            if texto in d.nombre.lower() or any(texto in c.lower() for c in d.cursos)
        ]

    def obtener_por_id(self, id_docente):
        docentes = self.repo.obtener_todos()
        for d in docentes:
            if d.id == str(id_docente):
                return d
        return None