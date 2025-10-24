describe('template spec', () => {
  it('passes', () => {
    cy.visit('/')
    cy.get('select:nth-child(3)').select('100 miles');
  })
})