const API_URL = "http://127.0.0.1:8000";

let ciudadesCache = [];
let ultimaRutaMasCorta = null;
let ultimasRutas = [];

document.addEventListener("DOMContentLoaded", async () => {
  await verificarBackend();
  await cargarCiudades();
});

async function verificarBackend() {
  const status = document.getElementById("apiStatus");

  try {
    const response = await fetch(`${API_URL}/`);
    if (!response.ok) throw new Error("Backend no respondió correctamente");

    status.classList.remove("error");
    status.classList.add("ok");
    status.innerHTML = `<span class="status-dot"></span> Backend conectado`;
  } catch (error) {
    status.classList.remove("ok");
    status.classList.add("error");
    status.innerHTML = `<span class="status-dot"></span> Backend apagado`;
    mostrarToast("No se pudo conectar con el backend. Encendé uvicorn.", "error");
  }
}

async function cargarCiudades() {
  try {
    const response = await fetch(`${API_URL}/ciudades/`);

    if (!response.ok) {
      throw new Error("No se pudo cargar ciudades");
    }

    const data = await response.json();
    ciudadesCache = data.ciudades || [];

    llenarSelect("origen", ciudadesCache);
    llenarSelect("destino", ciudadesCache);
    actualizarMetrica("metricCiudades", ciudadesCache.length);

    if (ciudadesCache.length > 1) {
      const destino = document.getElementById("destino");
      destino.selectedIndex = 1;
    }
  } catch (error) {
    mostrarResultadoError("No se pudieron cargar las ciudades. Revisá que el backend esté encendido.");
    actualizarMetrica("metricCiudades", "--");
  }
}

function llenarSelect(id, ciudades) {
  const select = document.getElementById(id);
  select.innerHTML = "";

  ciudades.forEach(ciudad => {
    const option = document.createElement("option");
    option.value = ciudad;
    option.textContent = formatearNombre(ciudad);
    select.appendChild(option);
  });
}

async function buscarRutaMasCorta() {
  const origen = document.getElementById("origen").value;
  const destino = document.getElementById("destino").value;

  if (!validarSeleccion(origen, destino)) return;

  mostrarResultadoCargando("Consultando Prolog para encontrar la ruta óptima...");

  try {
    const response = await fetch(`${API_URL}/rutas/mas-corta?origen=${encodeURIComponent(origen)}&destino=${encodeURIComponent(destino)}`);

    if (!response.ok) {
      ultimaRutaMasCorta = null;
      ultimasRutas = [];

      actualizarMetrica("metricDistancia", "--");
      actualizarMetrica("metricRutas", "--");
      actualizarRutasCounter(0);

      rellenarConexionConValores(origen, destino);
      mostrarMensajeSinRuta(origen, destino);

      mostrarToast("No existe ruta. Podés crear una nueva conexión.", "info");
      return;
    }

    const data = await response.json();
    ultimaRutaMasCorta = data;

    actualizarMetrica("metricDistancia", data.distancia);
    mostrarResultadoRuta(data, origen, destino);

    await buscarTodasLasRutas(false);
    mostrarToast("Ruta más corta calculada correctamente.", "success");
  } catch (error) {
    mostrarResultadoError("Error al consultar la ruta más corta.");
    mostrarToast("Error de comunicación con el backend.", "error");
  }
}

async function buscarTodasLasRutas(mostrarToastFinal = true) {
  const origen = document.getElementById("origen").value;
  const destino = document.getElementById("destino").value;
  const container = document.getElementById("rutasContainer");

  if (!validarSeleccion(origen, destino)) return;

  container.classList.remove("empty-routes");
  container.innerHTML = `<div class="empty-routes">Buscando todas las rutas posibles...</div>`;

  try {
    const response = await fetch(`${API_URL}/rutas/todas?origen=${encodeURIComponent(origen)}&destino=${encodeURIComponent(destino)}`);

    if (!response.ok) {
      ultimasRutas = [];

      actualizarRutasCounter(0);
      actualizarMetrica("metricRutas", "--");

      container.classList.add("empty-routes");
      container.innerHTML = `
    No se encontraron rutas disponibles entre
    ${formatearNombre(origen)} y ${formatearNombre(destino)}.
  `;

      ocultarEstadisticasRutas();

      if (mostrarToastFinal) {
        mostrarMensajeSinRuta(origen, destino);
        mostrarToast("No hay rutas para comparar.", "info");
      }

      return;
    }

    const data = await response.json();
    ultimasRutas = data.rutas || [];

    pintarRutas(ultimasRutas);
    actualizarRutasCounter(ultimasRutas.length);
    actualizarMetrica("metricRutas", ultimasRutas.length);
    mostrarEstadisticasRutas(ultimasRutas);

    if (mostrarToastFinal) {
      mostrarToast(`Se encontraron ${ultimasRutas.length} rutas posibles.`, "success");
    }
  } catch (error) {
    container.classList.add("empty-routes");
    container.innerHTML = "Error al consultar todas las rutas.";
    mostrarToast("Error al consultar rutas alternativas.", "error");
  }
}

async function agregarConexion() {
  const origen = document.getElementById("nuevoOrigen").value.trim();
  const destino = document.getElementById("nuevoDestino").value.trim();
  const distancia = Number(document.getElementById("nuevaDistancia").value);

  if (!origen || !destino || !distancia) {
    mostrarToast("Completá origen, destino y distancia.", "error");
    return;
  }

  if (distancia <= 0) {
    mostrarToast("La distancia debe ser mayor que cero.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_URL}/conexiones/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ origen, destino, distancia })
    });

    const data = await response.json();

    if (!response.ok) {
      mostrarToast(data.detail || "No se pudo agregar la conexión.", "error");
      return;
    }

    limpiarFormularioAgregar();
    await cargarCiudades();
    seleccionarSiExiste("origen", data.conexion?.origen || origen);
    seleccionarSiExiste("destino", data.conexion?.destino || destino);

    mostrarToast("Conexión agregada correctamente.", "success");
    await buscarRutaMasCorta();
  } catch (error) {
    mostrarToast("Error al agregar conexión.", "error");
  }
}

async function eliminarConexion() {
  const origen = document.getElementById("eliminarOrigen").value.trim();
  const destino = document.getElementById("eliminarDestino").value.trim();

  if (!origen || !destino) {
    mostrarToast("Completá origen y destino para eliminar.", "error");
    return;
  }

  const confirmar = confirm(`¿Seguro que querés eliminar la conexión entre ${origen} y ${destino}?`);
  if (!confirmar) return;

  try {
    const response = await fetch(`${API_URL}/conexiones/`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ origen, destino })
    });

    if (!response.ok) {
      mostrarToast("No se pudo eliminar la conexión.", "error");
      return;
    }

    document.getElementById("eliminarOrigen").value = "";
    document.getElementById("eliminarDestino").value = "";

    await cargarCiudades();
    limpiarResultados();

    mostrarToast("Conexión eliminada correctamente.", "success");
  } catch (error) {
    mostrarToast("Error al eliminar conexión.", "error");
  }
}

function validarSeleccion(origen, destino) {
  if (!origen || !destino) {
    mostrarToast("Seleccioná origen y destino.", "error");
    return false;
  }

  if (origen === destino) {
    mostrarResultadoError("El origen y destino no pueden ser iguales.");
    mostrarToast("Seleccioná dos ciudades diferentes.", "error");
    return false;
  }

  return true;
}

function intercambiarCiudades() {
  const origen = document.getElementById("origen");
  const destino = document.getElementById("destino");
  const temp = origen.value;
  origen.value = destino.value;
  destino.value = temp;
  mostrarToast("Origen y destino intercambiados.", "info");
}

function rellenarConexionConSeleccion() {
  const origen = document.getElementById("origen").value;
  const destino = document.getElementById("destino").value;
  rellenarConexionConValores(origen, destino);
  mostrarToast("Selección actual copiada al formulario de conexión.", "info");
}

function rellenarEliminacionConSeleccion() {
  const origen = document.getElementById("origen").value;
  const destino = document.getElementById("destino").value;
  document.getElementById("eliminarOrigen").value = formatearNombre(origen);
  document.getElementById("eliminarDestino").value = formatearNombre(destino);
  mostrarToast("Selección actual copiada al formulario de eliminación.", "info");
}

function rellenarConexionConValores(origen, destino) {
  document.getElementById("nuevoOrigen").value = formatearNombre(origen);
  document.getElementById("nuevoDestino").value = formatearNombre(destino);
}

function limpiarFormularioAgregar() {
  document.getElementById("nuevoOrigen").value = "";
  document.getElementById("nuevoDestino").value = "";
  document.getElementById("nuevaDistancia").value = "";
}

function seleccionarSiExiste(id, value) {
  const select = document.getElementById(id);
  const normalizado = normalizarTexto(value);
  const option = [...select.options].find(opt => normalizarTexto(opt.value) === normalizado);
  if (option) select.value = option.value;
}

function mostrarResultadoRuta(data, origen, destino) {
  const ruta = data.ruta || [];
  const totalCiudades = ruta.length;
  const totalTramos = Math.max(totalCiudades - 1, 0);
  const timeline = ruta.map(ciudad => `
    <div class="timeline-step">
      <span class="timeline-dot"></span>
      <span class="timeline-name">${formatearNombre(ciudad)}</span>
    </div>
  `).join("");

  mostrarResultado(`
    <div class="result-success">
      <div class="result-header">
        <div>
          <h3>Ruta óptima encontrada</h3>
          <p>${formatearNombre(origen)} → ${formatearNombre(destino)}</p>
        </div>
        <span class="badge">Calculada por Prolog</span>
      </div>
      <div class="distance-hero"><strong>${data.distancia}</strong><span>km</span></div>
      <div class="timeline">${timeline}</div>
      <div class="result-meta">
        <div class="meta-box"><strong>${totalCiudades}</strong><span>ciudades</span></div>
        <div class="meta-box"><strong>${totalTramos}</strong><span>tramos</span></div>
        <div class="meta-box"><strong>${data.distancia}</strong><span>km total</span></div>
      </div>
    </div>
  `);
}

function pintarRutas(rutas) {
  const container = document.getElementById("rutasContainer");
  container.classList.remove("empty-routes");
  container.innerHTML = "";

  if (!rutas.length) {
    container.classList.add("empty-routes");
    container.innerHTML = "No hay rutas cargadas todavía.";
    return;
  }

  rutas.forEach((item, index) => {
    const div = document.createElement("div");
    div.className = `route-item ${index === 0 ? "best-route" : ""}`;
    div.innerHTML = `
      <div class="route-top">
        <span class="route-title">${index === 0 ? "Mejor ruta" : `Ruta ${index + 1}`}</span>
        <span class="route-distance">${item.distancia} km</span>
      </div>
      <div class="route-path">${formatearRuta(item.ruta)}</div>
    `;
    container.appendChild(div);
  });
}

function mostrarResultado(html) {
  document.getElementById("resultadoPrincipal").innerHTML = html;
}

function mostrarResultadoCargando(mensaje) {
  mostrarResultado(`<div class="empty-state"><div class="empty-icon">⟳</div><h3>Procesando consulta</h3><p>${mensaje}</p></div>`);
}

function mostrarResultadoError(mensaje) {
  mostrarResultado(`<div class="empty-state"><div class="empty-icon">!</div><h3>No se pudo completar</h3><p>${mensaje}</p></div>`);
}

function limpiarResultados() {
  ultimaRutaMasCorta = null;
  ultimasRutas = [];

  actualizarMetrica("metricRutas", "--");
  actualizarMetrica("metricDistancia", "--");
  actualizarRutasCounter(0);

  mostrarResultado(`
    <div class="empty-state">
      <div class="empty-icon">⌁</div>
      <h3>Esperando consulta</h3>
      <p>Selecciona origen y destino para visualizar la ruta más corta.</p>
    </div>
  `);

  const rutasContainer = document.getElementById("rutasContainer");
  rutasContainer.classList.add("empty-routes");
  rutasContainer.innerHTML = "No hay rutas cargadas todavía.";

  ocultarEstadisticasRutas();
  limpiarMapa();

  mostrarToast("Resultados limpiados.", "info");
}

function formatearRuta(ruta) {
  return ruta.map(ciudad => formatearNombre(ciudad)).join(" → ");
}

function formatearNombre(nombre) {
  if (!nombre) return "";
  return String(nombre).replaceAll("_", " ").replace(/\b\w/g, letra => letra.toUpperCase());
}

function normalizarTexto(value) {
  return String(value || "").toLowerCase().trim().replaceAll(" ", "_").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function actualizarMetrica(id, valor) {
  const el = document.getElementById(id);
  if (el) el.textContent = valor;
}

function actualizarRutasCounter(total) {
  const counter = document.getElementById("rutasCounter");
  counter.textContent = `${total} ${total === 1 ? "ruta" : "rutas"}`;
}

function mostrarToast(mensaje, tipo = "info") {
  const toast = document.getElementById("toast");
  toast.textContent = mensaje;
  toast.className = `toast show ${tipo}`;
  clearTimeout(mostrarToast.timeoutId);
  mostrarToast.timeoutId = setTimeout(() => { toast.className = "toast"; }, 3200);
}

function limpiarMapa() {
  // Esta función es segura aunque no exista un mapa en esta versión del frontend.
  // Se deja aquí para limpiar estados visuales cuando no hay ruta o se reinicia la búsqueda.
}

function mostrarMensajeSinRuta(origen, destino) {
  const mensaje = `
    <div class="no-route-box">
      <h3>No existe una ruta disponible</h3>
      <p>
        No se encontró ningún recorrido entre
        <strong>${formatearNombre(origen)}</strong> y
        <strong>${formatearNombre(destino)}</strong>.
      </p>
      <p>
        Esto puede pasar porque las ciudades no están conectadas todavía en la base de conocimiento de Prolog.
      </p>
      <div class="no-route-actions">
        <button onclick="rellenarConexionConSeleccion()" class="btn-primary">
          Crear conexión entre estas ciudades
        </button>
        <button onclick="limpiarResultados()" class="btn-muted">
          Limpiar búsqueda
        </button>
      </div>
    </div>
  `;

  mostrarResultado(mensaje);

  const rutasContainer = document.getElementById("rutasContainer");
  rutasContainer.classList.add("empty-routes");
  rutasContainer.innerHTML = `
    No hay rutas posibles para comparar porque no existe conexión entre las ciudades seleccionadas.
  `;

  ocultarEstadisticasRutas();
  limpiarMapa();
}

function mostrarEstadisticasRutas(rutas) {
  const panel = document.getElementById("estadisticasRutas");

  if (!panel || !rutas.length) {
    ocultarEstadisticasRutas();
    return;
  }

  const distancias = rutas.map(ruta => Number(ruta.distancia));
  const menor = Math.min(...distancias);
  const mayor = Math.max(...distancias);
  const promedio = distancias.reduce((acc, item) => acc + item, 0) / distancias.length;
  const diferencia = mayor - menor;

  panel.classList.remove("hidden");

  panel.innerHTML = `
    <div class="stat-card">
      <strong>${rutas.length}</strong>
      <span>rutas encontradas</span>
    </div>

    <div class="stat-card">
      <strong>${menor}</strong>
      <span>km ruta más corta</span>
    </div>

    <div class="stat-card">
      <strong>${mayor}</strong>
      <span>km ruta más larga</span>
    </div>

    <div class="stat-card">
      <strong>${promedio.toFixed(1)}</strong>
      <span>km promedio</span>
    </div>

    <div class="stat-card">
      <strong>${diferencia}</strong>
      <span>km de diferencia</span>
    </div>
  `;
}

function ocultarEstadisticasRutas() {
  const panel = document.getElementById("estadisticasRutas");

  if (!panel) return;

  panel.classList.add("hidden");
  panel.innerHTML = "";
}