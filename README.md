# Teachers UPC (web)

Plataforma de calificación de docentes: el **diseño visual** (carpetas `templates/` y `static/`)
conectado a la **lógica del programa** (`service/`, `repository/`, `modelo/`, `utils/`).

## Primera vez (VS Code)

1. Instala Python y la extensión **Python** de VS Code.
2. **File > Open Folder** y elige esta carpeta.
3. En la terminal de VS Code:

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Ctrl+Shift+P > Python: Select Interpreter** y elige el de `.venv`.

## Ejecutar

- Presiona **F5** y elige **"Teachers UPC - Web (app.py)"**, o en la terminal: `python app.py`
- Abre **http://127.0.0.1:5000** en el navegador.

## Qué hace la página

- **Registrarse / Iniciar sesión** (usa `estudiantes.csv`).
- **Buscador** por nombre de docente o por curso, y botón **Ver todos**.
- **Ver perfil**: puntaje, opiniones, análisis de sentimiento y formulario para **publicar una opinión**.
- **Inteligencia Artificial**: chat con el asistente Gemini (`GEMINI_API_KEY` en `.env`).

## Fotos de los docentes

Copia las fotos a `static/imagenes/` con el nombre que aparece en la columna `foto` de `docentes.csv`
(`ana.jpg`, `luis.jpg`, ...). Si una foto no existe, se muestra un avatar con las iniciales.

## Versión de consola

`main.py` sigue funcionando igual que antes (opción "Plataforma Docentes - consola" en F5).

## Notas

- La primera vez que se analiza una opinión, `transformers` descarga el modelo
  `pysentimiento/robertuito-sentiment-analysis` (necesita internet). Si no carga, la página
  funciona igual pero sin análisis de sentimiento.
- Los datos viven en `docentes.csv`, `estudiantes.csv` y `opiniones.csv`.

## Publicar en GitHub y Render (plan gratuito, 512 MB de RAM)

`torch` y `transformers` no caben en 512 MB, por eso Render usa **`requirements-render.txt`**
(sin esas librerías). El análisis de sentimiento lo hace entonces Gemini, con la misma clave.

1. **GitHub:** sube el proyecto (el `.gitignore` ya excluye `.env` y `.venv`; nunca subas tu clave).
2. **Render > New > Web Service**, conecta el repositorio y configura:
   - **Build Command:** `pip install -r requirements-render.txt`
   - **Start Command:** `gunicorn app:app --workers 1 --threads 4 --timeout 120`
     (usa **1 worker**: los datos están en archivos .csv y varios workers los corromperían).
3. **Environment** (variables en el panel de Render):
   - `GEMINI_API_KEY` = tu clave
   - `SECRET_KEY` = una frase larga y aleatoria
   - `SENTIMIENTO_BACKEND` = `gemini`

**Importante:** en el plan gratuito de Render el disco es temporal. Cada vez que el servicio se
reinicia, se duerme por inactividad o se vuelve a desplegar, los `.csv` vuelven a como están en GitHub,
así que **los usuarios y opiniones nuevos se pierden**. Sirve para una demostración; para guardar datos
de forma permanente hace falta una base de datos.
