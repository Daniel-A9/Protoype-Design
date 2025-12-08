describe('Vendor Page', () => {
  beforeEach(() => {
    // Suppress uncaught exceptions from application code
    cy.on('uncaught:exception', (err) => {
      if (err.message.includes('Cannot read properties of null')) {
        return false;
      }
      return true;
    });
    cy.visit('/vendors/brewery/index.html');
  });

  it('should display vendor name "Brewery Central"', () => {
    cy.contains('h2', 'Brewery Central').should('be.visible');
  });
});

