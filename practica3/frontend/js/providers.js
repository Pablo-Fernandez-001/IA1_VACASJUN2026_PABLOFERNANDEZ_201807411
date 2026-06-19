const app = document.querySelector("#app");
let editingId = null;
app.innerHTML = `
  <div class="topline"><h1>Proveedores</h1></div>
  <section class="panel">
    <h2 id="formTitle">Nuevo proveedor</h2>
    <form id="providerForm" class="form-grid">
      <label>Nombre<input id="name" required></label>
      <label>NIT<input id="nit" required></label>
      <label>Correo<input id="email" type="email"></label>
      <label>Telefono<input id="phone"></label>
      <label>Direccion<input id="address"></label>
      <label>Categoria<input id="category" value="General"></label>
      <button type="submit">Guardar</button>
      <button type="button" class="secondary" id="cancelEdit">Limpiar</button>
    </form>
    <p class="message" id="message"></p>
  </section>
  <section class="panel">
    <h2>Listado</h2>
    <div class="table-wrap"><table><thead><tr><th>Nombre</th><th>NIT</th><th>Correo</th><th>Telefono</th><th>Categoria</th><th>Acciones</th></tr></thead><tbody id="rows"></tbody></table></div>
  </section>
`;

function readForm() {
  return {
    name: name.value, nit: nit.value, email: email.value, phone: phone.value,
    address: address.value, category: category.value, is_active: true,
  };
}

function clearForm() {
  editingId = null;
  providerForm.reset();
  category.value = "General";
  formTitle.textContent = "Nuevo proveedor";
}

async function loadProviders() {
  const providers = await api("/api/providers");
  rows.innerHTML = providers.map(provider => `
    <tr>
      <td>${provider.name}</td><td>${provider.nit}</td><td>${provider.email || ""}</td>
      <td>${provider.phone || ""}</td><td>${provider.category || ""}</td>
      <td class="actions">
        <button type="button" onclick='editProvider(${JSON.stringify(provider)})'>Editar</button>
        <button class="danger" type="button" onclick="deleteProvider(${provider.id})">Eliminar</button>
      </td>
    </tr>`).join("");
}

window.editProvider = (provider) => {
  editingId = provider.id;
  formTitle.textContent = "Editar proveedor";
  for (const key of ["name", "nit", "email", "phone", "address", "category"]) document.querySelector(`#${key}`).value = provider[key] || "";
};

window.deleteProvider = async (id) => {
  if (!confirm("Eliminar proveedor?")) return;
  await api(`/api/providers/${id}`, { method: "DELETE" });
  loadProviders();
};

providerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api(editingId ? `/api/providers/${editingId}` : "/api/providers", {
      method: editingId ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(readForm()),
    });
    message.textContent = "Proveedor guardado.";
    clearForm();
    loadProviders();
  } catch (error) {
    message.textContent = error.message;
  }
});
cancelEdit.addEventListener("click", clearForm);
loadProviders();
