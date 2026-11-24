// Teachers UPC - interfaz web conectada al servidor (app.py)

document.addEventListener("DOMContentLoaded", function () {
  const $ = (id) => document.getElementById(id);

  let usuario = null;
  let modoAuth = "login"; // "login" | "registro"
  let docenteAbierto = null;
  let ultimaBusqueda = "";
  let docentesCargados = [];
  let puntajeElegido = 0;

  // ---------- utilidades ----------
  async function api(url, opciones = {}) {
    const config = { method: opciones.method || "GET", headers: {} };
    if (opciones.body !== undefined) {
      config.headers["Content-Type"] = "application/json";
      config.body = JSON.stringify(opciones.body);
    }
    const resp = await fetch(url, config);
    let datos = {};
    try { datos = await resp.json(); } catch (e) { /* respuesta sin cuerpo */ }
    if (resp.status === 401 && usuario) establecerUsuario(null); // la sesión expiró
    if (!resp.ok) throw new Error(datos.error || "Ocurrió un error. Inténtalo de nuevo.");
    return datos;
  }

  // Todo texto que viene del usuario se inserta con textContent (nunca como HTML).
  function el(etiqueta, clase, texto) {
    const nodo = document.createElement(etiqueta);
    if (clase) nodo.className = clase;
    if (texto !== undefined) nodo.textContent = texto;
    return nodo;
  }

  function toast(mensaje, tipo) {
    const t = el("div", "toast " + (tipo || ""), mensaje);
    $("toasts").append(t);
    setTimeout(() => t.remove(), 3500);
  }

  function avatar(nombre) {
    const iniciales = nombre.split(/\s+/).filter(Boolean).slice(0, 2)
      .map((p) => p[0].toUpperCase()).join("");
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">` +
      `<rect width="200" height="200" fill="#ffd9a8"/>` +
      `<text x="50%" y="54%" font-family="Georgia,serif" font-size="80" fill="#C94F29" ` +
      `text-anchor="middle" dominant-baseline="middle">${iniciales}</text></svg>`;
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  }

  function ponerFoto(img, docente) {
    const respaldo = avatar(docente.nombre);
    img.onerror = function () { img.onerror = null; img.src = respaldo; };
    img.src = docente.foto || respaldo;
    img.alt = "Foto de " + docente.nombre;
  }

  // ★★★★☆ para un valor de 0 a 5
  function estrellas(valor, clase) {
    const caja = el("span", clase || "estrellas-fila");
    const llenas = Math.round(valor);
    caja.setAttribute("aria-label", valor.toFixed ? valor.toFixed(1) + " de 5" : valor + " de 5");
    for (let i = 1; i <= 5; i++) caja.append(el("span", i <= llenas ? "" : "vacia", "★"));
    return caja;
  }

  const textoOpiniones = (n) => n + (n === 1 ? " opinión" : " opiniones");

  // ---------- estadísticas ----------
  async function cargarEstadisticas() {
    try {
      const e = await api("/api/estadisticas");
      document.querySelectorAll(".stat-docentes").forEach((n) => (n.textContent = e.docentes));
      document.querySelectorAll(".stat-opiniones").forEach((n) => (n.textContent = e.opiniones));
      document.querySelectorAll(".stat-estudiantes").forEach((n) => (n.textContent = e.estudiantes));
    } catch (err) { /* las cifras son decorativas */ }
  }

  // ---------- sesión ----------
  function establecerUsuario(u) {
    usuario = u;
    $("saludoUsuario").hidden = !u;
    $("saludoUsuario").textContent = u ? "Hola, " + u.nombre.split(" ")[0] : "";
    $("btnAbrirLogin").hidden = !!u;
    $("btnAbrirRegistro").hidden = !!u;
    $("btnLogout").hidden = !u;
    $("landing").hidden = !!u;
    $("app").hidden = !u;
    if (u) {
      $("tituloBienvenida").textContent = "Bienvenido, " + u.nombre.split(" ")[0];
    } else {
      docentesCargados = [];
      $("resultados").replaceChildren();
      $("filtros").hidden = true;
      $("contadorResultados").textContent = "";
      $("chatIA").replaceChildren();
      cerrarPerfil();
    }
    cargarEstadisticas();
  }

  function abrirAuth(modo) {
    modoAuth = modo;
    const registro = modo === "registro";
    $("tituloAuth").textContent = registro ? "Crear cuenta" : "Iniciar sesión";
    $("campoNombre").hidden = !registro;
    $("authNombre").required = registro;
    $("authClave").autocomplete = registro ? "new-password" : "current-password";
    $("btnEnviarAuth").textContent = registro ? "Registrarme" : "Entrar";
    $("textoCambiar").textContent = registro ? "¿Ya tienes cuenta?" : "¿No tienes cuenta?";
    $("linkCambiarAuth").textContent = registro ? "Iniciar sesión" : "Crear cuenta";
    $("errorAuth").hidden = true;
    $("modalAuth").classList.add("abierto");
    (registro ? $("authNombre") : $("authCorreo")).focus();
  }

  function cerrarAuth() {
    $("modalAuth").classList.remove("abierto");
    $("formAuth").reset();
  }

  $("btnAbrirLogin").addEventListener("click", () => abrirAuth("login"));
  $("btnAbrirRegistro").addEventListener("click", () => abrirAuth("registro"));
  document.querySelectorAll("[data-abrir]").forEach((b) =>
    b.addEventListener("click", () => abrirAuth(b.dataset.abrir)));
  $("cerrarAuth").addEventListener("click", cerrarAuth);
  $("linkCambiarAuth").addEventListener("click", (e) => {
    e.preventDefault();
    abrirAuth(modoAuth === "login" ? "registro" : "login");
  });

  $("formAuth").addEventListener("submit", async (e) => {
    e.preventDefault();
    const boton = $("btnEnviarAuth");
    boton.disabled = true;
    $("errorAuth").hidden = true;
    try {
      const cuerpo = { correo: $("authCorreo").value, clave: $("authClave").value };
      if (modoAuth === "registro") cuerpo.nombre = $("authNombre").value;
      const datos = await api(modoAuth === "registro" ? "/api/registro" : "/api/login",
        { method: "POST", body: cuerpo });
      cerrarAuth();
      establecerUsuario(datos.usuario);
      toast(modoAuth === "registro" ? "¡Cuenta creada! Bienvenido(a)." : "Sesión iniciada.", "exito");
      mostrarTodos();
    } catch (err) {
      $("errorAuth").textContent = err.message;
      $("errorAuth").hidden = false;
    } finally {
      boton.disabled = false;
    }
  });

  $("btnLogout").addEventListener("click", async () => {
    try { await api("/api/logout", { method: "POST" }); } catch (e) { /* ignorar */ }
    establecerUsuario(null);
    toast("Sesión cerrada.");
  });

  // ---------- búsqueda, filtros y resultados ----------
  function pintarResultados(docentes, mensajeVacio) {
    const cont = $("resultados");
    if (docentes.length === 0) {
      cont.replaceChildren(el("p", "mensaje-vacio", mensajeVacio));
      return;
    }
    cont.replaceChildren(...docentes.map((d) => {
      const tarjeta = el("div", "tarjeta-profesor");
      const img = el("img", "foto-profesor");
      ponerFoto(img, d);
      const boton = el("button", "btn-perfil", "Ver perfil");
      boton.dataset.id = d.id;
      const nota = el("p", "calificacion");
      if (d.total_opiniones > 0) nota.append(estrellas(d.puntaje), " " + d.puntaje.toFixed(1));
      else nota.textContent = "Sin calificaciones";
      tarjeta.append(
        img,
        el("h3", "", d.nombre),
        el("p", "", "Cursos: " + d.cursos.join(", ")),
        nota,
        el("p", "", textoOpiniones(d.total_opiniones)),
        boton
      );
      return tarjeta;
    }));
  }

  function reconstruirFiltroCursos() {
    const select = $("filtroCurso");
    const previo = select.value;
    const cursos = [...new Set(docentesCargados.flatMap((d) => d.cursos))]
      .sort((a, b) => a.localeCompare(b, "es"));
    select.replaceChildren(new Option("Todos", ""), ...cursos.map((c) => new Option(c, c)));
    select.value = cursos.includes(previo) ? previo : "";
  }

  function aplicarVista() {
    let lista = [...docentesCargados];
    const curso = $("filtroCurso").value;
    if (curso) lista = lista.filter((d) => d.cursos.includes(curso));

    const orden = $("ordenResultados").value;
    if (orden === "az") lista.sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));
    else if (orden === "opiniones") lista.sort((a, b) => b.total_opiniones - a.total_opiniones);
    else lista.sort((a, b) =>
      (b.total_opiniones > 0) - (a.total_opiniones > 0) ||
      b.puntaje - a.puntaje || b.total_opiniones - a.total_opiniones);

    $("contadorResultados").textContent =
      docentesCargados.length ? `(${lista.length} ${lista.length === 1 ? "docente" : "docentes"})` : "";
    pintarResultados(lista, ultimaBusqueda
      ? "No encontramos profesores ni cursos relacionados."
      : "No hay docentes para mostrar.");
  }

  async function cargarDocentes(texto) {
    if (!usuario) { abrirAuth("login"); return; }
    ultimaBusqueda = texto;
    $("resultados").replaceChildren(...Array.from({ length: 4 }, () => el("div", "esqueleto")));
    try {
      const url = texto ? "/api/docentes?q=" + encodeURIComponent(texto) : "/api/docentes";
      docentesCargados = (await api(url)).docentes;
      $("filtros").hidden = docentesCargados.length === 0;
      reconstruirFiltroCursos();
      aplicarVista();
    } catch (err) {
      $("resultados").replaceChildren(el("p", "mensaje-vacio", err.message));
    }
  }

  function buscar() {
    const texto = $("buscarProfesor").value.trim();
    if (texto === "") {
      toast("Escribe el nombre de un profesor o curso.");
      return;
    }
    cargarDocentes(texto);
  }

  function mostrarTodos() {
    $("buscarProfesor").value = "";
    cargarDocentes("");
  }

  $("btnBuscar").addEventListener("click", buscar);
  $("btnTodos").addEventListener("click", mostrarTodos);
  $("buscarProfesor").addEventListener("keydown", (e) => { if (e.key === "Enter") buscar(); });
  $("filtroCurso").addEventListener("change", aplicarVista);
  $("ordenResultados").addEventListener("change", aplicarVista);

  // ---------- perfil del profesor ----------
  function cerrarPerfil() {
    $("modalPerfil").classList.remove("abierto");
    docenteAbierto = null;
  }

  function elegirPuntaje(valor) {
    puntajeElegido = valor;
    $("estrellas").querySelectorAll("button").forEach((b) => {
      const activa = Number(b.dataset.valor) <= valor;
      b.classList.toggle("activa", activa);
      b.setAttribute("aria-checked", Number(b.dataset.valor) === valor ? "true" : "false");
    });
  }

  $("estrellas").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b) elegirPuntaje(Number(b.dataset.valor));
  });

  $("textoOpinion").addEventListener("input", () => {
    $("contadorCaracteres").textContent = $("textoOpinion").value.length;
  });

  function pintarPerfil(d) {
    ponerFoto($("fotoPerfil"), d);
    $("nombrePerfil").textContent = d.nombre;
    $("cursoPerfil").textContent = "Cursos: " + d.cursos.join(", ");
    const nota = $("notaPerfil");
    nota.replaceChildren();
    if (d.total_opiniones > 0) nota.append(estrellas(d.puntaje), " " + d.puntaje.toFixed(1) + " / 5");
    else nota.textContent = "Sin calificaciones";
    $("cantidadComentarios").textContent = textoOpiniones(d.total_opiniones);

    // gráfico de barras de puntajes
    const total = d.total_opiniones || 1;
    $("distribucion").replaceChildren(...["5", "4", "3", "2", "1"].map((n) => {
      const cantidad = d.distribucion[n] || 0;
      const fila = el("div", "fila-barra");
      const fondo = el("div", "barra-fondo");
      const relleno = el("div", "barra-relleno");
      relleno.style.width = Math.round((cantidad / total) * 100) + "%";
      fondo.append(relleno);
      fila.append(el("span", "", n + " ★"), fondo, el("span", "", String(cantidad)));
      return fila;
    }));
    $("distribucion").hidden = d.total_opiniones === 0;

    // opiniones anónimas: solo estrellas y texto
    const lista = $("listaComentarios");
    if (d.opiniones.length === 0) {
      lista.replaceChildren(el("p", "", "Aún no hay opiniones. ¡Sé el primero en opinar!"));
      return;
    }
    lista.replaceChildren(...d.opiniones.map((op) => {
      const caja = el("div", "comentario-perfil");
      caja.append(estrellas(op.puntaje, "puntos-comentario"), el("p", "", op.comentario));
      return caja;
    }));
  }

  async function abrirPerfil(id) {
    try {
      const d = await api("/api/docentes/" + encodeURIComponent(id));
      docenteAbierto = d.id;
      pintarPerfil(d);
      $("errorOpinion").hidden = true;
      $("modalPerfil").classList.add("abierto");
    } catch (err) {
      toast(err.message, "error");
    }
  }

  $("resultados").addEventListener("click", (e) => {
    const boton = e.target.closest(".btn-perfil");
    if (boton) abrirPerfil(boton.dataset.id);
  });
  $("cerrarPerfil").addEventListener("click", cerrarPerfil);

  // ---------- términos ----------
  $("abrirTerminos").addEventListener("click", (e) => { e.preventDefault(); $("modalTerminos").classList.add("abierto"); });
  $("cerrarTerminos").addEventListener("click", () => $("modalTerminos").classList.remove("abierto"));

  // cerrar con clic en el fondo oscuro o con Escape
  const cierres = { modalPerfil: cerrarPerfil, modalAuth: cerrarAuth, modalTerminos: () => $("modalTerminos").classList.remove("abierto") };
  for (const id in cierres) {
    $(id).addEventListener("click", (e) => { if (e.target === $(id)) cierres[id](); });
  }
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") Object.values(cierres).forEach((f) => f());
  });

  // ---------- publicar opinión ----------
  $("formOpinion").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!docenteAbierto) return;
    if (!puntajeElegido) {
      $("errorOpinion").textContent = "Elige un puntaje de 1 a 5 estrellas.";
      $("errorOpinion").hidden = false;
      return;
    }
    const boton = $("btnPublicar");
    boton.disabled = true;
    boton.textContent = "Publicando...";
    $("errorOpinion").hidden = true;
    try {
      await api("/api/docentes/" + docenteAbierto + "/opiniones", {
        method: "POST",
        body: { comentario: $("textoOpinion").value, puntaje: puntajeElegido },
      });
      $("formOpinion").reset();
      elegirPuntaje(0);
      $("contadorCaracteres").textContent = "0";
      await abrirPerfil(docenteAbierto);
      toast("¡Opinión publicada!", "exito");
      cargarDocentes(ultimaBusqueda); // refresca la tarjeta con el nuevo puntaje
      cargarEstadisticas();
    } catch (err) {
      $("errorOpinion").textContent = err.message;
      $("errorOpinion").hidden = false;
    } finally {
      boton.disabled = false;
      boton.textContent = "Publicar";
    }
  });

  // ---------- asistente IA ----------
  async function preguntarIA(pregunta) {
    if (!usuario) { abrirAuth("login"); return; }
    const chat = $("chatIA");
    chat.append(el("div", "burbuja yo", pregunta));
    const pensando = el("div", "burbuja ia pensando", "Pensando...");
    chat.append(pensando);
    chat.scrollTop = chat.scrollHeight;
    $("preguntaIA").value = "";
    $("btnPreguntarIA").disabled = true;
    try {
      const datos = await api("/api/ia", { method: "POST", body: { pregunta } });
      pensando.className = "burbuja ia";
      pensando.textContent = datos.respuesta;
    } catch (err) {
      pensando.className = "burbuja ia";
      pensando.textContent = err.message;
    } finally {
      $("btnPreguntarIA").disabled = false;
      chat.scrollTop = chat.scrollHeight;
    }
  }

  $("formIA").addEventListener("submit", (e) => {
    e.preventDefault();
    const pregunta = $("preguntaIA").value.trim();
    if (pregunta) preguntarIA(pregunta);
  });
  document.querySelectorAll(".chip").forEach((c) =>
    c.addEventListener("click", () => preguntarIA(c.dataset.pregunta)));

  // ---------- arranque ----------
  api("/api/sesion").then((d) => {
    establecerUsuario(d.usuario);
    if (d.usuario) mostrarTodos();
  }).catch(() => establecerUsuario(null));
});
