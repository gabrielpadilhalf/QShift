const clickWeekday = (label) => {
  cy.get('.mol-employee-profile__weekday-buttons')
    .contains('button', label)
    .click();
};

const weekdayBtn = (label) =>
  cy.get('.mol-employee-profile__weekday-buttons').contains('button', label);

// Navega para a tela de edição de um funcionário pelo nome
const openEmployeeEdit = (name) => {
  cy.visit('/staff');
  cy.contains(name)
    .closest('.mol-employee-card')
    .within(() => {
      cy.get('button').first().click();
    });
  cy.url().should('include', '/availability');
};

describe('US-13 — Dias Preferenciais de Funcionário', () => {
  let token;
  let employeeId;
  const employeeName = 'QShift PrefDays Test';

  // ── SETUP: cria funcionário de teste via API ──────────────────────────────
  before(() => {
    cy.fixture('mockData').then((data) => {
      // 1. Tenta logar — se o usuário existir, limpa resíduos e o próprio usuário
      cy.request({
        method: 'POST',
        url: `${data.apiBase}/auth/login`,
        body: { email: data.testUser.email, password: data.testUser.password },
        failOnStatusCode: false,
      }).then((loginRes) => {
        if (loginRes.status === 200) {
          const existingToken = loginRes.body.access_token;
          cy.deleteEmployeeByNameViaApi(employeeName, existingToken);
          cy.request({
            method: 'DELETE',
            url: `${data.apiBase}/users/me`,
            headers: { Authorization: `Bearer ${existingToken}` },
            failOnStatusCode: false,
          });
        }
      });

      // 2. Registra o usuário via UI (garante que existe ao rodar isolado)
      cy.visit('/register');
      cy.get('#email').type(data.testUser.email);
      cy.get('#confirm-email').type(data.testUser.email);
      cy.get('#password').type(data.testUser.password);
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/login');

      // 3. Loga via API e cria o funcionário de teste
      cy.request({
        method: 'POST',
        url: `${data.apiBase}/auth/login`,
        body: { email: data.testUser.email, password: data.testUser.password },
      }).then((res) => {
        token = res.body.access_token;

        cy.request({
          method: 'POST',
          url: `${data.apiBase}/employees`,
          headers: { Authorization: `Bearer ${token}` },
          body: { name: employeeName, active: true },
        }).then((empRes) => {
          employeeId = empRes.body.id;
        });
      });
    });
  });

  beforeEach(() => {
    cy.fixture('mockData').then((data) => {
      cy.loginViaApi(data.testUser.email, data.testUser.password);
    });
    cy.on('window:alert', () => true);
  });

  // ── TEARDOWN ──────────────────────────────────────────────────────────────
  after(() => {
    cy.fixture('mockData').then((data) => {
      cy.request({
        method: 'POST',
        url: `${data.apiBase}/auth/login`,
        body: { email: data.testUser.email, password: data.testUser.password },
        failOnStatusCode: false,
      }).then((res) => {
        if (res.status !== 200 || !employeeId) return;
        cy.request({
          method: 'DELETE',
          url: `${data.apiBase}/employees/${employeeId}`,
          headers: { Authorization: `Bearer ${res.body.access_token}` },
          failOnStatusCode: false,
        });
      });
    });
  });

  // ── CENÁRIO 1: Definição de dias preferenciais ────────────────────────────

  it('Cenário 1 — deve persistir segunda-feira e quarta-feira como dias preferenciais', () => {
    openEmployeeEdit(employeeName);

    // Garante que nenhum dia está selecionado inicialmente
    cy.get('.mol-employee-profile__weekday-buttons button').each(($btn) => {
      cy.wrap($btn).should('not.have.class', 'mol-employee-profile__weekday-btn--selected');
    });

    // Seleciona MON (index 0) e WED (index 2)
    clickWeekday('MON');
    clickWeekday('WED');

    // Confirma o visual dos botões antes de salvar
    weekdayBtn('MON').should('have.class', 'mol-employee-profile__weekday-btn--selected');
    weekdayBtn('WED').should('have.class', 'mol-employee-profile__weekday-btn--selected');
    weekdayBtn('TUE').should('not.have.class', 'mol-employee-profile__weekday-btn--selected');

    // Salva
    cy.get('button').contains('Save').click();
    cy.url().should('include', '/staff');
    cy.contains(employeeName).should('be.visible');

    // Verifica persistência via API: preferred_weekdays deve ter [0, 2]
    cy.fixture('mockData').then((data) => {
      cy.request({
        method: 'GET',
        url: `${data.apiBase}/employees/${employeeId}`,
        headers: { Authorization: `Bearer ${token}` },
      }).then((res) => {
        expect(res.body.preferred_weekdays).to.deep.equal([0, 2]);
      });
    });
  });

  // ── CENÁRIO 2: Visualização das preferências salvas ───────────────────────

  it('Cenário 2 — ao reabrir a edição, MON e WED devem aparecer selecionados', () => {
    // Abre a edição novamente (sem interagir antes)
    openEmployeeEdit(employeeName);

    // MON (0) e WED (2) devem estar pré-selecionados
    weekdayBtn('MON').should('have.class', 'mol-employee-profile__weekday-btn--selected');
    weekdayBtn('WED').should('have.class', 'mol-employee-profile__weekday-btn--selected');

    // Os outros cinco dias não devem estar selecionados
    ['TUE', 'THU', 'FRI', 'SAT', 'SUN'].forEach((label) => {
      weekdayBtn(label).should('not.have.class', 'mol-employee-profile__weekday-btn--selected');
    });
  });

  // ── CENÁRIO 3: Alteração parcial ──────────────────────────────────────────

  it('Cenário 3 — deve remover apenas WED mantendo MON selecionado', () => {
    openEmployeeEdit(employeeName);

    // Confirma estado atual: MON e WED selecionados (vem do Cenário 1)
    weekdayBtn('MON').should('have.class', 'mol-employee-profile__weekday-btn--selected');
    weekdayBtn('WED').should('have.class', 'mol-employee-profile__weekday-btn--selected');

    // Remove apenas WED (toggle — clicando de novo)
    clickWeekday('WED');

    // WED deve ser desmarcado; MON continua selecionado
    weekdayBtn('MON').should('have.class', 'mol-employee-profile__weekday-btn--selected');
    weekdayBtn('WED').should('not.have.class', 'mol-employee-profile__weekday-btn--selected');

    // Salva a alteração parcial
    cy.get('button').contains('Save').click();
    cy.url().should('include', '/staff');

    // Verifica persistência via API: preferred_weekdays deve ter apenas [0]
    cy.fixture('mockData').then((data) => {
      cy.request({
        method: 'GET',
        url: `${data.apiBase}/employees/${employeeId}`,
        headers: { Authorization: `Bearer ${token}` },
      }).then((res) => {
        expect(res.body.preferred_weekdays).to.deep.equal([0]);
      });
    });

    // Reabre a edição e confirma que apenas MON aparece selecionado
    openEmployeeEdit(employeeName);
    weekdayBtn('MON').should('have.class', 'mol-employee-profile__weekday-btn--selected');
    weekdayBtn('WED').should('not.have.class', 'mol-employee-profile__weekday-btn--selected');
  });
});
