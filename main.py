import os

# Los archivos .csv se leen con rutas relativas: aseguramos que siempre se busquen
# junto a main.py, sin importar desde que carpeta se ejecute (VS Code, terminal, etc.).
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from service.estudiante_service import EstudianteService
from service.docente_service import DocenteService
from service.opinion_service import OpinionService
from service.agente_service import AgenteService
from utils.password_utils import leer_clave

# Pon False si quieres que la contraseña se escriba con input() normal (sin asteriscos),
# por ejemplo si corres el programa con el botón Run de PyCharm.
USAR_ASTERISCOS = True


def pedir_clave():
    if USAR_ASTERISCOS:
        return leer_clave ("Contraseña: ").strip()
    return input("Contraseña: ").strip()


def menu_principal():
    estudiante_service = EstudianteService()
    docente_service = DocenteService()
    opinion_service = OpinionService(AgenteService())

    usuario_actual = None

    while True:
        print("\n=== PLATAFORMA DE CALIFICACIÓN DE DOCENTES UPC ===")
        if usuario_actual:
            print(f"Usuario activo: {usuario_actual.nombre} ({usuario_actual.correo})")
            print("1. Buscar docentes")
            print("2. Ver todos los docentes")
            print("3. Preguntar a la IA (¿qué profesor es mejor para un curso?)")
            print("4. Cerrar sesión")
            print("0. Salir")
        else:
            print("1. Iniciar sesión")
            print("2. Crear cuenta")
            print("0. Salir")

        opcion = input("\nSeleccione una opción: ").strip()

        if not usuario_actual:
            if opcion == "1":
                correo = input("Correo institucional: ").strip()
                clave = pedir_clave()
                usuario = estudiante_service.iniciar_sesion(correo, clave)
                if usuario:
                    usuario_actual = usuario
                    print(f"\n¡Bienvenido(a), {usuario.nombre}!")
                else:
                    print("\n[ERROR] Credenciales incorrectas.")
            elif opcion == "2":
                print("\n--- REGISTRO DE ESTUDIANTE ---")
                nombre = input("Nombre completo: ").strip()
                correo = input("Correo institucional: ").strip()
                clave = pedir_clave()

                if not nombre or not correo or not clave:
                    print("\n[ERROR] Todos los campos son obligatorios.")
                else:
                    nuevo_usuario, mensaje = estudiante_service.registrar_estudiante(nombre, correo, clave)
                    if nuevo_usuario:
                        print(f"\n¡{mensaje} Bienvenido(a), {nuevo_usuario.nombre}!")
                        usuario_actual = nuevo_usuario
                    else:
                        print(f"\n[ERROR] {mensaje}")
            elif opcion == "0":
                print("\n¡Hasta luego!")
                break
        else:
            if opcion == "1":
                busqueda = input("Ingrese el nombre del docente: ")
                resultados = docente_service.buscar_por_nombre(busqueda)
                mostrar_y_gestionar_docentes(resultados, docente_service, opinion_service, usuario_actual)
            elif opcion == "2":
                resultados = docente_service.obtener_docentes()
                mostrar_y_gestionar_docentes(resultados, docente_service, opinion_service, usuario_actual)
            elif opcion == "3":
                preguntar_a_la_ia(docente_service, opinion_service)
            elif opcion == "4":
                usuario_actual = None
                print("\nSesión cerrada correctamente.")
            elif opcion == "0":
                print("\n¡Hasta luego!")
                break


def preguntar_a_la_ia(docente_service, opinion_service):
    print("\n--- ASISTENTE IA ---")
    print("Pregúntame por un curso o un docente. Ejemplos:")
    print("  - ¿Qué profesor es el mejor para Cálculo?")
    print("  - ¿Qué opinan de Juan Pérez?")
    print("(Escribe 'salir' o presiona Enter para volver al menú)")

    while True:
        pregunta = input("\nTu pregunta: ").strip()
        if not pregunta or pregunta.lower() in ("salir", "volver", "0"):
            return
        print("\nPensando...")
        respuesta = opinion_service.preguntar_a_la_ia(pregunta, docente_service.obtener_docentes())
        print(f"\n[IA] {respuesta}")


def mostrar_y_gestionar_docentes(docentes, docente_service, opinion_service, usuario):
    if not docentes:
        print("\nNo se encontraron docentes.")
        return

    print("\n--- RESULTADOS ---")
    for d in docentes:
        opinion_service.cargar_opiniones_a_docente(d)
        print(f"ID: {d.id} | {d.nombre} | Cursos: {', '.join(d.cursos)} | "
              f"Calificación: {d.puntaje_general}/5.0 ({len(d.opiniones)} opiniones)")

    id_sel = input("\nIngrese el ID del docente para ver detalles (o presione Enter para regresar): ").strip()
    if not id_sel:
        return

    docente_sel = docente_service.obtener_por_id(id_sel)
    if not docente_sel:
        print("\nID de docente no válido.")
        return

    opinion_service.cargar_opiniones_a_docente(docente_sel)
    positivas, negativas, neutrales = opinion_service.resumen_sentimientos(docente_sel)

    print(f"\n==========================================")
    print(f"Docente: {docente_sel.nombre}")
    print(f"Cursos: {', '.join(docente_sel.cursos)}")
    print(f"Puntaje General: {docente_sel.puntaje_general} / 5.0")
    print(f"Opiniones positivas: {positivas} | negativas: {negativas} | neutrales: {neutrales}")
    print(f"==========================================")
    print("OPINIONES:")
    for op in docente_sel.opiniones:
        print(f" - [{op.puntaje}/5] {op.comentario}")

    print("\n1. Publicar una opinión")
    print("2. Volver al menú")
    sub_opcion = input("Opción: ").strip()

    if sub_opcion == "1":
        comentario = input("Escribe tu opinión: ")
        while True:
            try:
                puntaje = int(input("Puntaje (1 a 5): "))
                if 1 <= puntaje <= 5:
                    break
                print("El puntaje debe ser entre 1 y 5.")
            except ValueError:
                print("Ingresa un número entero válido.")

        opinion_service.publicar_opinion(usuario.id, docente_sel.id, comentario, puntaje)
        print("\n¡Opinión publicada con éxito!")


if __name__ == "__main__":
    menu_principal()