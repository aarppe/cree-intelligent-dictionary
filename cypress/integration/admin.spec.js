const { join: joinPath } = require('path')

const ADMIN_LOGIN_URL = '/admin/login/'
const ADMIN_URL = '/admin/'

const CYPRESS_USER_JSON = joinPath(__dirname, '..', '..', 'src', 'CreeDictionary', '.cypress-user.json')

Cypress.Commands.add('login', () => {
  cy.visit('/admin/login/')
  cy.get('[name=csrfmiddlewaretoken]')
    .should('exist')
    .should('have.attr', 'value')
    .as('csrfToken')

  cy.readFile(CYPRESS_USER_JSON)
    .then(({username, password}) => {
      cy.get('@csrfToken').then(function (token) {
        cy.request({
          method: 'POST',
          url: ADMIN_LOGIN_URL,
          form: true,
          body: {
            username,
            password,
            next: '/admin'
          },
          headers: {
            'X-CSRFTOKEN': token,
          },
          followRedirect: false
        }).then(response => {
          expect(response.status).to.eql(302)
          expect(response.headers).to.have.property('location')
          expect(response.headers.location).to.not.contain('login')
        })
      })
    })
})

context('Admin interface', () => {
  it('should redirect anonymous users to the login page', function() {
    cy.visit('/admin')
    cy.location().then(({pathname}) =>
      expect(pathname).to.contain(ADMIN_LOGIN_URL))
  })

  it('should allow login', function() {
    // If this test fails, you are probably using `manage.py runserver` without
    // USE_TEST_DB=True, because the `cypress` user only gets created in the
    // test database.
    cy.visit('/admin')
    cy.readFile(CYPRESS_USER_JSON)
      .then(cypressUser => {
        cy.get('#id_username').type(cypressUser.username)
        cy.get('#id_password').type(cypressUser.password)
        cy.get('.submit-row > input').click()
      })
    cy.location('pathname').should('eq', ADMIN_URL)
  })

  it('should show auto-translations to logged-in users', function() {
    cy.login()
    cy.visitSearch('acâhkosa')
    cy
      .get('[data-cy=search-result]').contains('little star over there')
      .get('.cite-dict').contains('auto')
  })

  it('should not show auto-translations to anonymous users', function() {
    cy.visitSearch('acâhkosa')
    cy.get('[data-cy=search-result]').each(r => {
      // Every result should have a dictionary citation
      cy.wrap(r).get('.cite-dict').should('have.length.at.least', 1)
        .each(citation => {
          // But none of those should be ‘auto’
          cy.wrap(citation).should('not.contain', 'auto')
        })
    })
  })

  specify('the FST tool should work', function() {
    cy.login()
    for (const [query, result] of [
      ['kikaniminaw', 'PV/ka+nîmiw+V+AI+Ind+12Pl'],
      ['PV/ka+nîmiw+V+AI+Ind+12Pl', 'kika-nîminaw'],
      ['Obv+Dim+ star', 'little star over there'],
      ['Prt+3Pl+ it sings', 'they sang'],
      ['they sing', 'sing +V+AI+3Pl'],
    ]) {
      cy.visit('/admin/fst-tool', {qs: {text: query}})
      cy.get('pre').contains(result)
    }
  })

  it('should not show the FST tool to non-admin users', function() {
    cy.visit('/admin/fst-tool')
    cy.location().then(({pathname}) =>
      expect(pathname).to.contain(ADMIN_LOGIN_URL))
  })
})
