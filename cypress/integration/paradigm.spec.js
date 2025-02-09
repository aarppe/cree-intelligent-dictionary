describe('I want to search for a Cree word and see its inflectional paradigm', () => {
  // Test at least one word from each word class:
  const testCases = [
    {pos: 'VTA', lemma: 'mowêw', inflections: ['kimowin', 'kimowitin', 'ê-mowât']},
    {pos: 'VAI', lemma: 'wâpiw', inflections: ['niwâpin', 'kiwâpin', 'ê-wâpiyit']},
    {pos: 'VTI', lemma: 'mîcisow', inflections: ['nimîcison', 'kimîcison', 'ê-mîcisoyit']},
    {pos: 'VII', lemma: 'nîpin', inflections: ['nîpin', 'ê-nîpihk']},
    {pos: 'NAD', lemma: 'nôhkom', inflections: ['kôhkom', 'ohkoma']},
    {pos: 'NID', lemma: 'mîpit', inflections: ['nîpit', 'kîpit', 'wîpit']},
    {pos: 'NA', lemma: 'minôs', inflections: ['minôsak', 'minôsa']},
    {pos: 'NI', lemma: 'nipiy', inflections: ['nipîhk', 'ninipiy', 'kinipiy']},
  ]

  // Create test cases for each word above
  for (let {pos, lemma, inflections} of testCases) {
    it(`should display the paradigm for a word belonging to the ${pos} word class`, () => {
      cy.visitSearch(lemma)
      cy.get('[data-cy=search-results]')
        .contains('a', lemma)
        .click()

      cy.get('[data-cy=paradigm]')
        .as('paradigm')

      let ctx = cy.get('@paradigm')
        .should('contain', lemma)
      for (let wordform of inflections) {
        ctx = ctx.and('contain', wordform)
      }
    })
  }

  it('should display the paradigm for personal pronouns', () => {
    const head = 'niya'
    const inflections = ['kiya', 'wiya']

    cy.visitSearch(head)
    cy.get('[data-cy=search-results]')
      .contains('a', head)
      .click()

    cy.get('[data-cy=paradigm]')
      .as('paradigm')

    let ctx = cy.get('@paradigm')
      .should('contain', head)
    for (let wordform of inflections) {
      ctx = ctx.and('contain', wordform)
    }

    const labels = [
      { scope: 'col', label: /\bone\b/i },
      { scope: 'col', label: /\bmany\b/i },
      { scope: 'row', label: 'I' },
      { scope: 'row', label: /\byou\b/i },
    ]

    for (let {scope, label} of labels) {
      cy.get('@paradigm')
        .contains('th', label)
        .should('have.attr', 'scope', scope)
    }
  })

  // TODO: the next test should be here, but it is broken because the
  // upstream layouts are broken :/
  it.skip('should display titles within the paradigm', () => {
    // TODO: move this test into the previous test when the layout is fixed.
    cy.visitSearch('minôsis')
    cy.get('[data-cy=search-results]')
      .contains('a', 'minôsis')
      .click()

    cy.get('[data-cy=paradigm]')
      .as('paradigm')

    // TODO: the layouts should be able to differentiate between titles and
    // labels; currently, the specificiation is ambigous, hence, it's seen
    // as a .paradigm-label, when it should be a .paradigm-title :/
    cy.get('@paradigm')
      .contains('.paradigm-title', 'Ownership')
  })
})


describe('I want to know if a form is observed inside a paradigm table', () => {
  // TODO: this test should be re-enabled in linguist mode!
  it.skip('shows inflection frequency as digits in brackets', ()=>{
    cy.visitLemma('nipâw')
    cy.get('[data-cy=paradigm]').contains(/\(\d\)/)
  })
})

describe(' I want to see a clear indicator that a form does not exist', () => {

  it('shows cells that does not exist as a em dash', ()=>{
    cy.visitLemma('minôs')
    cy.getParadigmCell('One', {colLabel: 'Smaller/Lesser/Younger'}).contains('—')
  })
})


describe('paradigms are visitable from link', () => {
  const lemmaText = 'niska'
  it('shows basic paradigm', () => {
    cy.visitLemma(lemmaText, {'analysis': 'niska+N+A+Sg'})
    // Smaller/Lesser/Younger is an exclusive user friendly tag for BASIC paradigms
    cy.get('[data-cy=paradigm]').contains('Smaller/Lesser/Younger')
  })

  it('shows full paradigm', () => {
    cy.visitLemma(lemmaText, {'analysis': 'niska+N+A+Sg', 'paradigm-size': 'FULL'})
    // his/her/their is an exclusive user friendly tag for FULL paradigms
    cy.get('[data-cy=paradigm]').contains('his/her/their')
  })

  it('shows linguistic paradigm', () => {
    cy.visitLemma(lemmaText, {'analysis': 'niska+N+A+Sg', 'paradigm-size': 'LINGUISTIC'})
    // DIMINUTIVE is an exclusive linguistic term for FULL paradigms
    cy.get('[data-cy=paradigm]').contains('DIMINUTIVE')
  })
})

describe('paradigms can be toggled by the show more/less button', () => {
  it('shows basic, full, linguistic, and basic paradigm in sequence', () => {
    cy.visitLemma('nipâw')
    // "Something is happening now" is an exclusive user friendly tag for BASIC paradigms
    cy.get('[data-cy=paradigm]').contains('Something is happening now')

    cy.get('[data-cy=paradigm-toggle-button]').click()
    // s/he/they is an exclusive user friendly tag for FULL paradigms
    cy.get('[data-cy=paradigm]').contains('s/he/they')
    // somehow I have to add these cy.wait for the test to pass, javascript a bit slow?
    // If there is not enough wait, you'll get error "cy.click() failed because this element is detached from the DOM"
    cy.wait(500)
    cy.get('[data-cy=paradigm-toggle-button]').click()
    // 2p is an exclusive linguistic term for LINGUISTIC paradigms
    cy.wait(500)
    cy.get('[data-cy=paradigm]').contains('2p')

    cy.get('[data-cy=paradigm-toggle-button]').click()
    cy.wait(500)
    // now are we back to basic?
    cy.get('[data-cy=paradigm]').contains('Something is happening now')

  })
})

describe('Paradigm labels', () => {
  let lemma = 'nipâw'
  let englishLabel = 'they'
  let nehiyawewinLabel = 'wiyanaw'
  let linguisticLabel = '3s'

  beforeEach(() => {
    // As of 2021-06-02: paradigm label switching is only available to
    // logged-in users.
    cy.login()
  })

  it('should only be available for logged-in users', () => {
    // Undo the beforeEach() that logs in:
    // (I wanted to make deleting this code as easy as possible)
    cy.visit(Cypress.env('admin_url')).get('[href*="logout"]').click()

    // Visit the same page, logged-out:
    cy.visitLemma(lemma, { 'paradigm-size': 'FULL'})
    cy.log(`If the next assertion **fails**,
      that should mean the **paradigm label switcher is publicly available**.
      If so, please **DELETE THIS TEST CASE AND the \`beforeEach()\`**
      immediately above this test.
    `)
    cy.get('[data-cy=open-paradigm-label-switcher]')
      .should('not.exist')
  })

  it('should appear in plain English by default', () => {
    cy.visitLemma(lemma, { 'paradigm-size': 'FULL'})

    cy.get('[data-cy=paradigm]')
      .contains('th[scope=row]', englishLabel)
  })

  it('should appear in nêhiyawêwin (Plains Cree)', () => {
    cy.visitLemma(lemma, { 'paradigm-size': 'FULL'})

    cy.get('[data-cy=open-paradigm-label-switcher]')
      .click()
    cy.get('[data-cy=paradigm-label-options]')
      .contains(/nêhiyawêwin/i)
      .click()

    cy.get('[data-cy=paradigm]')
      .contains('th[scope=row]', nehiyawewinLabel)
  })

  it('should appear using lingustic terminology', () => {
    cy.visitLemma(lemma, { 'paradigm-size': 'FULL'})

    cy.get('[data-cy=open-paradigm-label-switcher]')
      .click()
    cy.get('[data-cy=paradigm-label-options]')
      .contains(/linguistic/i)
      .click()

    cy.get('[data-cy=paradigm]')
      .contains('th[scope=row]', linguisticLabel)
  })
})
