describe('template spec', () => {
  it('passes', () => {
    cy.visit('/')
    cy.get('#files a[href="/SearchFeed.html"] span.name').click();
    cy.get('input.search-input').click();
    cy.get('input.search-input').type('farm{enter}');
    cy.get('div:nth-child(2) > div.card-footer > div.row > div:nth-child(2) > div.clickable-container > span.comment-text').click();
  })
})