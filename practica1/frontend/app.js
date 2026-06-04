const API_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  cargarCiudades();
});

async function cargarCiudades() {
  try {
    const response = await fetch(`${API_URL}/ciudades/`);
    const data = await response.json();

    llenarSelect("origen", data.ciudades);
    llenarSelect("destino", data.ciudades);
  } catch (error) {
    mostrarResultado("No se pudieron cargar las ciudades. Revisá que el backend esté encendido.");
  }
}

function llenarSelect(id, ciudades) {
  const select = document.getElementById(id);
  select.innerHTML = "";

  ciudades.forEach(ciudad => {
    const option = document.createElement("option");
    option.value = ciudad;
    option.textContent = ciudad.replaceAll("_", " ");
    select.appendChild(option);
  });
}

async function buscarRutaMasCorta() {
  const origen = document.getElementById("origen").value;
  const destino = document.getElementById("destino").value;

  if (origen === destino) {
    mostrarResultado("El origen y destino no pueden ser iguales.");
    return;
  }

  try {
    const response = await fetch(`${API_URL}/rutas/mas-corta?origen=${origen}&destino=${destino}`);

    if (!response.ok) {
      mostrarResultado("No se encontró una ruta disponible entre esas ciudades.");
      return;
    }

    const data = await response.json();

    mostrarResultado(`
      <h3>Ruta más corta encontrada</h3>
      <p><strong>Ruta:</strong> ${formatearRuta(data.ruta)}</p>
      <p><strong>Distancia total:</strong> ${data.distancia} km</p>
    `);
  } catch (error) {
    mostrarResultado("Error al consultar la ruta más corta.");
  }
}

async function buscarTodasLasRutas() {
  const origen = document.getElementById("origen").value;
  const destino = document.getElementById("destino").value;
  const container = document.getElementById("rutasContainer");

  if (origen === destino) {
    container.innerHTML = "El origen y destino no pueden ser iguales.";
    return;
  }

  try {
    const response = await fetch(`${API_URL}/rutas/todas?origen=${origen}&destino=${destino}`);

    if (!response.ok) {
      container.innerHTML = "No se encontraron rutas disponibles.";
      return;
    }

    const data = await response.json();

    container.innerHTML = "";

    data.rutas.forEach((item, index) => {
      const div = document.createElement("div");
      div.className = "route-item";

      div.innerHTML = `
        <strong>Ruta ${index + 1}</strong>
        <p>${formatearRuta(item.ruta)}</p>
        <p><strong>Distancia:</strong> ${item.distancia} km</p>
      `;

      container.appendChild(div);
    });
  } catch (error) {
    container.innerHTML = "Error al consultar todas las rutas.";
  }
}

async function agregarConexion() {
  const origen = document.getElementById("nuevoOrigen").value;
  const destino = document.getElementById("nuevoDestino").value;
  const distancia = Number(document.getElementById("nuevaDistancia").value);

  if (!origen || !destino || !distancia) {
    alert("Completá origen, destino y distancia.");
    return;
  }

  if (distancia <= 0) {
    alert("La distancia debe ser mayor que cero.");
    return;
  }

  try {
    const response = await fetch(`${API_URL}/conexiones/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        origen,
        destino,
        distancia
      })
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.detail || "No se pudo agregar la conexión.");
      return;
    }

    alert("Conexión agregada correctamente.");

    document.getElementById("nuevoOrigen").value = "";
    document.getElementById("nuevoDestino").value = "";
    document.getElementById("nuevaDistancia").value = "";

    await cargarCiudades();

  } catch (error) {
    alert("Error al agregar conexión.");
  }
}

async function eliminarConexion() {
  const origen = document.getElementById("eliminarOrigen").value;
  const destino = document.getElementById("eliminarDestino").value;

  if (!origen || !destino) {
    alert("Completá origen y destino.");
    return;
  }

  try {
    const response = await fetch(`${API_URL}/conexiones/`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        origen,
        destino
      })
    });

    if (!response.ok) {
      alert("No se pudo eliminar la conexión.");
      return;
    }

    alert("Conexión eliminada correctamente.");

    document.getElementById("eliminarOrigen").value = "";
    document.getElementById("eliminarDestino").value = "";

    await cargarCiudades();

  } catch (error) {
    alert("Error al eliminar conexión.");
  }
}

function mostrarResultado(html) {
  document.getElementById("resultadoPrincipal").innerHTML = html;
}

function limpiarResultados() {
  document.getElementById("resultadoPrincipal").innerHTML = "Seleccioná origen y destino para buscar una ruta.";
  document.getElementById("rutasContainer").innerHTML = "No hay rutas cargadas todavía.";
}

function formatearRuta(ruta) {
  return ruta.map(ciudad => ciudad.replaceAll("_", " ")).join(" → ");
}