"""Teachers UPC - versión web.

Une el diseño visual (templates/ + static/) con la lógica que ya funcionaba
(service/, repository/, modelo/): registro, inicio de sesión, búsqueda de docentes,
opiniones con análisis de sentimiento y el asistente de IA.

Ejecutar:  python app.py   y abrir  http://127.0.0.1:5000
"""
import os

# Los .csv se leen con rutas relativas: siempre junto a este archivo.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import threading
from functools import wraps

from flask import Flask, jsonify, render_template, request, session, url_for

from service.agente_service import AgenteService
from service.docente_service import DocenteService
from service.estudiante_service import EstudianteService
from service.opinion_service import OpinionService

app = Flask(__name__)
# Para desplegar de verdad, define SECRET_KEY en el .env.
app.secret_key = os.getenv("SECRET_KEY", "teachers-upc-clave-de-desarrollo")

agente = AgenteService()
estudiante_service = EstudianteService()
docente_service = DocenteService()
opinion_service = OpinionService(agente)

# Los datos viven en archivos .csv: se atiende una operación a la vez para no corromperlos.
datos_lock = threading.RLock()

MAX_COMENTARIO = 500


# ---------------------------------------------------------------- utilidades
def usuario_actual():
    uid = session.get("usuario_id")
    if not uid:
        return None
    with datos_lock:
        for e in estudiante_service.repo.obtener_todos():
            if e.id == uid:
                return e
    return None


def requiere_sesion(f):
    @wraps(f)
    def envoltura(*args, **kwargs):
        usuario = usuario_actual()
        if not usuario:
            return jsonify(error="Debes iniciar sesión para continuar."), 401
        return f(usuario, *args, **kwargs)
    return envoltura


def usuario_json(u):
    return {"id": u.id, "nombre": u.nombre, "correo": u.correo} if u else None


def url_foto(docente):
    """La foto solo se usa si el archivo existe en static/imagenes/; si no, la web dibuja un avatar."""
    nombre = os.path.basename(docente.foto or "")
    if nombre and os.path.exists(os.path.join(app.static_folder, "imagenes", nombre)):
        return url_for("static", filename=f"imagenes/{nombre}")
    return None


def docente_json(d):
    opinion_service.cargar_opiniones_a_docente(d)
    return {
        "id": d.id,
        "nombre": d.nombre,
        "cursos": d.cursos,
        "foto": url_foto(d),
        "puntaje": d.puntaje_general,
        "total_opiniones": len(d.opiniones),
    }


# ---------------------------------------------------------------- páginas
@app.get("/")
def inicio():
    return render_template("index.html")


@app.get("/api/estadisticas")
def api_estadisticas():
    """Totales generales (no incluyen datos personales); se muestran en la portada."""
    with datos_lock:
        return jsonify(
            docentes=len(docente_service.obtener_docentes()),
            opiniones=len(opinion_service.repo.obtener_todas()),
            estudiantes=len(estudiante_service.repo.obtener_todos()),
        )


# ---------------------------------------------------------------- sesión
@app.get("/api/sesion")
def api_sesion():
    return jsonify(usuario=usuario_json(usuario_actual()))


@app.post("/api/registro")
def api_registro():
    d = request.get_json(silent=True) or {}
    nombre = str(d.get("nombre", "")).strip()
    correo = str(d.get("correo", "")).strip()
    clave = str(d.get("clave", "")).strip()
    if not nombre or not correo or not clave:
        return jsonify(error="Todos los campos son obligatorios."), 400
    if "@" not in correo:
        return jsonify(error="Escribe un correo válido."), 400
    with datos_lock:
        nuevo, mensaje = estudiante_service.registrar_estudiante(nombre, correo, clave)
    if not nuevo:
        return jsonify(error=mensaje), 409
    session["usuario_id"] = nuevo.id
    return jsonify(usuario=usuario_json(nuevo), mensaje=mensaje)


@app.post("/api/login")
def api_login():
    d = request.get_json(silent=True) or {}
    with datos_lock:
        usuario = estudiante_service.iniciar_sesion(
            str(d.get("correo", "")).strip(), str(d.get("clave", "")).strip())
    if not usuario:
        return jsonify(error="Credenciales incorrectas."), 401
    session["usuario_id"] = usuario.id
    return jsonify(usuario=usuario_json(usuario))


@app.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify(ok=True)


# ---------------------------------------------------------------- docentes
@app.get("/api/docentes")
@requiere_sesion
def api_docentes(usuario):
    texto = request.args.get("q", "").strip()
    with datos_lock:
        docentes = docente_service.buscar(texto) if texto else docente_service.obtener_docentes()
        return jsonify(docentes=[docente_json(d) for d in docentes])


@app.get("/api/docentes/<id_docente>")
@requiere_sesion
def api_docente(usuario, id_docente):
    with datos_lock:
        d = docente_service.obtener_por_id(id_docente)
        if not d:
            return jsonify(error="Docente no encontrado."), 404
        datos = docente_json(d)
        # Las opiniones son anónimas y no se muestra su análisis de sentimiento:
        # el navegador solo recibe el comentario y el puntaje.
        # Cuántas opiniones hay con cada puntaje (para el gráfico de barras del perfil).
        datos["distribucion"] = {str(n): sum(1 for op in d.opiniones if op.puntaje == n)
                                 for n in (5, 4, 3, 2, 1)}
        datos["opiniones"] = [
            {"comentario": op.comentario, "puntaje": op.puntaje}
            for op in reversed(d.opiniones)  # las más recientes primero
        ]
    return jsonify(datos)


@app.post("/api/docentes/<id_docente>/opiniones")
@requiere_sesion
def api_publicar_opinion(usuario, id_docente):
    d = request.get_json(silent=True) or {}
    comentario = str(d.get("comentario", "")).strip()
    try:
        puntaje = int(d.get("puntaje"))
    except (TypeError, ValueError):
        puntaje = 0
    if not comentario:
        return jsonify(error="Escribe tu opinión."), 400
    if len(comentario) > MAX_COMENTARIO:
        return jsonify(error=f"La opinión no puede superar {MAX_COMENTARIO} caracteres."), 400
    if not 1 <= puntaje <= 5:
        return jsonify(error="El puntaje debe ser entre 1 y 5."), 400
    with datos_lock:
        if not docente_service.obtener_por_id(id_docente):
            return jsonify(error="Docente no encontrado."), 404
        opinion_service.publicar_opinion(usuario.id, str(id_docente), comentario, puntaje)
    return jsonify(ok=True)


# ---------------------------------------------------------------- asistente IA
@app.post("/api/ia")
@requiere_sesion
def api_ia(usuario):
    pregunta = str((request.get_json(silent=True) or {}).get("pregunta", "")).strip()
    if not pregunta:
        return jsonify(error="Escribe una pregunta."), 400
    with datos_lock:
        docentes = docente_service.obtener_docentes()
        respuesta = opinion_service.preguntar_a_la_ia(pregunta, docentes)
    return jsonify(respuesta=respuesta)


if __name__ == "__main__":
    # Calienta el modelo de sentimiento en segundo plano para que la primera opinión no se demore.
    # (Con el reloader de debug se evita duplicarlo.)
    threading.Thread(target=agente._cargar_modelo, daemon=True).start()
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
