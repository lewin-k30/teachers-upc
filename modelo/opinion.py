class Opinion:
    def __init__(self, id_opinion, estudiante_id, docente_id, comentario, puntaje,
                 sentimiento="SIN_ANALIZAR", confianza=0.0):
        self.id = str(id_opinion)
        self.estudiante_id = str(estudiante_id)
        self.docente_id = str(docente_id)
        self.comentario = comentario
        self.puntaje = int(puntaje)
        self.sentimiento = sentimiento or "SIN_ANALIZAR"
        self.confianza = float(confianza or 0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "estudiante_id": self.estudiante_id,
            "docente_id": self.docente_id,
            "comentario": self.comentario,
            "puntaje": str(self.puntaje),
            "sentimiento": self.sentimiento,
            "confianza": f"{self.confianza:.2f}"
        }

    @staticmethod
    def from_dict(datos):
        # .get() permite leer opiniones.csv antiguos que no tienen las columnas nuevas
        return Opinion(
            datos["id"],
            datos["estudiante_id"],
            datos["docente_id"],
            datos["comentario"],
            datos["puntaje"],
            datos.get("sentimiento") or "SIN_ANALIZAR",
            datos.get("confianza") or 0.0
        )