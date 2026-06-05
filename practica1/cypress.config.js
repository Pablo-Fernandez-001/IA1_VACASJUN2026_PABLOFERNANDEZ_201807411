const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    defaultCommandTimeout: 10000,
    downloadsFolder: "evidencias/cypress/downloads",
    screenshotsFolder: "evidencias/cypress/screenshots",
    specPattern: "cypress/e2e/**/*.cy.js",
    supportFile: false,
    video: false,
    viewportHeight: 900,
    viewportWidth: 1366
  }
});
