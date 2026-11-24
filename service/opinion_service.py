from modelo.opinion import Opinion
from repository.opinion_repository import OpinionRepository
from service.agente_service import AgenteService


class OpinionService:
    def __init__(self, agente=None):
        self.repo = OpinionRepository()
        self.agente = agente or AgenteService()

    def _completar_sentimientos(self, opiniones):
        """Analiza (una sola vez) las opiniones que aún no tienen sentimiento,
        por ejemplo las que ya estaban guardadas antes de agregar la IA."""
        hubo_cambios = False
        for op in opiniones:
            if op.sentimiento == "SIN_ANALIZAR":
                sentimiento, confianza = self.agente.analizar_sentimiento(op.comentario)
                if sentimiento != "SIN_ANALIZAR":
                    op.sentimiento = sentimiento
                    op.confianza = confianza
                    hubo_cambios = True
        if hubo_cambios:
            self.repo.guardar_todas(opiniones)
        return opiniones

    def cargar_opiniones_a_docente(self, docente):
        todas = self._completar_sentimientos(self.repo.obtener_todas())
        docente.opiniones = [
            op for op in todas if op.docente_id == docente.id
        ]
        docente.puntaje_general = self.agente.calcular_puntaje_ponderado(docente.opiniones)

    def publicar_opinion(self, estudiante_id, docente_id, comentario, puntaje):
        todas = self.repo.obtener_todas()

        # La IA analiza solo el texto del comentario; el resultado queda guardado pero no se muestra
        sentimiento, confianza = self.agente.analizar_sentimiento(comentario)

        nuevo_id = str(len(todas) + 1)
        nueva_op = Opinion(nuevo_id, estudiante_id, docente_id, comentario, puntaje,
                           sentimiento, confianza)
        todas.append(nueva_op)
        self.repo.guardar_todas(todas)
        return nueva_op

    def resumen_sentimientos(self, docente):
        """(positivas, negativas, neutrales) de las opiniones ya cargadas en el docente."""
        return self.agente.contar_sentimientos(docente.opiniones)

    def preguntar_a_la_ia(self, pregunta, docentes):
        return self.agente.responder_pregunta(pregunta, docentes, self.cargar_opiniones_a_docente)