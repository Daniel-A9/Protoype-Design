describe('template spec', () => {
  it('passes', () => {
    cy.visit('/')
    cy.get('div:nth-child(1) > div.card-image > img.responsive').click();
    cy.get('#products-grid img[alt="Chocolate Stout"]').click();
  })
})