const BACKEND_URL = Cypress.env("BACKEND_URL") || "http://127.0.0.1:8000";
const FRONTEND_URL = Cypress.env("FRONTEND_URL") || "http://127.0.0.1:5500";

describe("Frontend con live server y backend real", () => {
  beforeEach(() => {
    cy.request(`${BACKEND_URL}/`).its("status").should("eq", 200);
    cy.visit(FRONTEND_URL);
  });

  it("carga con live server y muestra conexion real al backend", () => {
    cy.get("#apiStatus", { timeout: 15000 })
      .should("have.class", "ok")
      .and("contain", "Backend conectado");

    cy.get("#origen option").should("have.length.greaterThan", 1);
    cy.get("#destino option").should("have.length.greaterThan", 1);
    cy.get("#metricCiudades").invoke("text").then((text) => {
      expect(Number(text)).to.be.greaterThan(1);
    });

    cy.screenshot("frontend-live-server-conectado");
  });

  it("consulta la ruta mas corta usando la API real y captura el resultado", () => {
    cy.intercept("GET", `${BACKEND_URL}/rutas/mas-corta*`).as("rutaMasCorta");
    cy.intercept("GET", `${BACKEND_URL}/rutas/todas*`).as("rutasPosibles");

    cy.get("#apiStatus", { timeout: 15000 }).should("have.class", "ok");
    cy.get("#origen").select("guatemala");
    cy.get("#destino").select("quetzaltenango");
    cy.contains("button", "Buscar ruta").click();

    cy.wait("@rutaMasCorta").its("response.statusCode").should("eq", 200);
    cy.wait("@rutasPosibles").its("response.statusCode").should("eq", 200);

    cy.get("#resultadoPrincipal").should("contain", "230");
    cy.get("#resultadoPrincipal").should("contain", "Guatemala");
    cy.get("#resultadoPrincipal").should("contain", "Quetzaltenango");
    cy.get("#metricDistancia").should("have.text", "230");
    cy.get("#rutasCounter").should("not.have.text", "0 rutas");

    cy.screenshot("frontend-ruta-mas-corta-real");
  });
});
