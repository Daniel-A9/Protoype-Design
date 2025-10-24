const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: 'https://daniel-a9.github.io/Protoype-Design',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
