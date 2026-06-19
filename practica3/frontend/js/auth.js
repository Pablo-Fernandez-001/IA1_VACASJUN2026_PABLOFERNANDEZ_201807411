document.querySelector("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.querySelector("#message");
  try {
    const data = await api("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: document.querySelector("#username").value,
        password: document.querySelector("#password").value,
      }),
    });
    localStorage.setItem("smartinvoice_token", data.access_token);
    location.href = "dashboard.html";
  } catch (error) {
    message.textContent = error.message;
  }
});

document.querySelector("#registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.querySelector("#message");
  try {
    await api("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: document.querySelector("#r_username").value,
        email: document.querySelector("#r_email").value,
        full_name: document.querySelector("#r_full_name").value,
        password: document.querySelector("#r_password").value,
      }),
    });
    message.textContent = "Usuario registrado. Ya puede iniciar sesion.";
  } catch (error) {
    message.textContent = error.message;
  }
});
