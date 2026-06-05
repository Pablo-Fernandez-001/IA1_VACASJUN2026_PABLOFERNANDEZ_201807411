const BACKEND_URL = Cypress.env("BACKEND_URL") || "http://127.0.0.1:8000";

describe("Backend FastAPI funcionando", () => {
  it("responde desde el servidor y genera captura del root", () => {
    cy.request(`${BACKEND_URL}/`).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.include({
        mensaje: "API funcionando correctamente",
        backend: "FastAPI",
        motor_logico: "SWI-Prolog"
      });
    });

    cy.visit(`${BACKEND_URL}/estado`);
    cy.contains("API funcionando correctamente").should("be.visible");
    cy.contains("SWI-Prolog").should("be.visible");
    cy.screenshot("backend-servidor-ejecutandose");
  });

  it("valida endpoints reales y genera captura de Swagger docs", () => {
    cy.request(`${BACKEND_URL}/ciudades/`).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body.ciudades).to.include("guatemala");
      expect(response.body.ciudades).to.include("quetzaltenango");
    });

    cy.request(`${BACKEND_URL}/rutas/mas-corta?origen=guatemala&destino=quetzaltenango`)
      .then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.ruta).to.deep.eq([
          "guatemala",
          "antigua",
          "chimaltenango",
          "quetzaltenango"
        ]);
        expect(response.body.distancia).to.eq(230);
      });

    cy.visit(`${BACKEND_URL}/docs`);
    cy.get(".swagger-ui", { timeout: 15000 }).should("be.visible");
    cy.contains("Rutas").should("be.visible");
    cy.screenshot("backend-swagger-docs");
  });

  it("rechaza eliminar una conexion inexistente", () => {
    cy.request({
      method: "DELETE",
      url: `${BACKEND_URL}/conexiones/`,
      failOnStatusCode: false,
      body: {
        origen: "ciudad_inexistente_a",
        destino: "ciudad_inexistente_b"
      }
    }).then((response) => {
      expect(response.status).to.eq(404);
      expect(response.body.detail).to.contain("No existe una conexión registrada");
    });
  });
});
