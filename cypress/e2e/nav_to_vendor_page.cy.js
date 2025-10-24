describe('template spec', () => {
  it('passes', () => {
    cy.visit('http://127.0.0.1:5500/')
    cy.get('#files a[href="/SearchFeed.html"] span.name').click();
    cy.get('div:nth-child(8) h5.card-title').click();
    cy.get('div.clickable-card img.responsive').click();
  })
})