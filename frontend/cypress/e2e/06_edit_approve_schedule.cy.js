const goToScheduleRecords = () => {
  cy.intercept('GET', '**/employees').as('loadEmployees');
  cy.intercept('GET', '**/employees/availabilities').as('avails');
  cy.visit('/staff');
  cy.wait('@loadEmployees');

  cy.visit('/reports');
  cy.url().should('include', '/reports');
  cy.contains('Reports and Analysis').should('be.visible');
  cy.contains('Generated Scales').click({ force: true });
  cy.url().should('include', '/schedule-records');
  cy.contains('Schedule Records').should('be.visible');
  // Espera o useEffect de fetchAvails completar antes de prosseguir
  cy.wait('@avails');
};

describe('Filtragem de Funcionários por Disponibilidade na Edição de Escala', () => {
  let token;
  let empDispId; // funcionário COM disponibilidade TER 07:00-13:00
  let empIndispId; // funcionário SEM disponibilidade na terça

  const EMP_DISP_NAME = 'EmpDisponivel';
  const EMP_INDISP_NAME = 'EmpIndisponivel';

  // ── SETUP ────────────────────────────────────────────────────────────────
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
          const t = loginRes.body.access_token;
          cy.deleteEmployeeByNameViaApi(EMP_DISP_NAME, t);
          cy.deleteEmployeeByNameViaApi(EMP_INDISP_NAME, t);
          cy.request({
            method: 'DELETE',
            url: `${data.apiBase}/users/me`,
            headers: { Authorization: `Bearer ${t}` },
            failOnStatusCode: false,
          });
        }
      });

      // 2. Registra o usuário via UI
      cy.visit('/register');
      cy.get('#email').type(data.testUser.email);
      cy.get('#confirm-email').type(data.testUser.email);
      cy.get('#password').type(data.testUser.password);
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/login');

      // 3. Loga via API
      cy.request({
        method: 'POST',
        url: `${data.apiBase}/auth/login`,
        body: { email: data.testUser.email, password: data.testUser.password },
      }).then((res) => {
        token = res.body.access_token;
        const headers = { Authorization: `Bearer ${token}` };

        // 4a. Cria EmpDisponivel
        cy.request({
          method: 'POST',
          url: `${data.apiBase}/employees`,
          headers,
          body: { name: EMP_DISP_NAME, active: true },
        }).then((r) => {
          empDispId = r.body.id;
          // 4a-i. Adiciona disponibilidade na terça com janela total
          cy.request({
            method: 'POST',
            url: `${data.apiBase}/employees/${empDispId}/availabilities`,
            headers,
            body: { weekday: 1, start_time: '00:00', end_time: '23:59' },
          }).then(() => {
            // 4b. Cria EmpIndisponivel APÓS confirmar que a disponibilidade de EmpDisponivel foi criada
            cy.request({
              method: 'POST',
              url: `${data.apiBase}/employees`,
              headers,
              body: { name: EMP_INDISP_NAME, active: true },
            }).then((r2) => {
              empIndispId = r2.body.id;
              // 4b-i. Adiciona disponibilidade só na segunda (terça fica sem cobertura)
              cy.request({
                method: 'POST',
                url: `${data.apiBase}/employees/${empIndispId}/availabilities`,
                headers,
                body: { weekday: 0, start_time: '00:00', end_time: '23:59' },
              }).then(() => {
                // 5. Calcula a próxima segunda-feira
                const today = new Date();
                const dayOfWeek = today.getDay();
                const daysToNextMonday = dayOfWeek === 0 ? 1 : 8 - dayOfWeek;
                const monday = new Date(today);
                monday.setDate(today.getDate() + daysToNextMonday);
                const mondayStr = monday.toISOString().split('T')[0];

                // 5b. Remove semanas residuais de runs anteriores
                cy.request({
                  method: 'GET',
                  url: `${data.apiBase}/weeks`,
                  headers,
                }).then((weeksRes) => {
                  const deleteAll = weeksRes.body.map((w) =>
                    cy.request({
                      method: 'DELETE',
                      url: `${data.apiBase}/weeks/${w.id}`,
                      headers,
                      failOnStatusCode: false,
                    })
                  );
                  // 6. Cria semana com seg + ter + sab como dias abertos
                  cy.request({
                    method: 'POST',
                    url: `${data.apiBase}/weeks`,
                    headers,
                    body: { start_date: mondayStr, open_days: [0, 1, 5] },
                  }).then((weekRes) => {
                    const weekId = weekRes.body.id;

                    // 7. Turno Principal (Cenários 1, 2, 3): TER 08:00–12:00
                    cy.request({
                      method: 'POST',
                      url: `${data.apiBase}/weeks/${weekId}/shifts`,
                      headers,
                      body: { weekday: 1, start_time: '08:00', end_time: '12:00', min_staff: 1 },
                    }).then((shiftRes) => {
                      const shiftPrincipalId = shiftRes.body.id;

                      // 8. Turno Vazio (Cenário 4): SAB 08:00–12:00
                      //    Nenhum funcionário tem disponibilidade no sábado (weekday=5)
                      //    O slot ficará sem funcionários atribuídos — lista sempre vazia no picker
                      cy.request({
                        method: 'POST',
                        url: `${data.apiBase}/weeks/${weekId}/shifts`,
                        headers,
                        body: { weekday: 5, start_time: '08:00', end_time: '12:00', min_staff: 1 },
                      }).then((shiftVazioRes) => {
                        const shiftVazioId = shiftVazioRes.body.id;

                        // 9. Aprova escala — o turno do SAB fica sem atribuição (lista vazia)
                        cy.request({
                          method: 'POST',
                          url: `${data.apiBase}/weeks/${weekId}/schedule`,
                          headers,
                          body: {
                            shifts: [
                              { shift_id: shiftPrincipalId, employee_ids: [empDispId] },
                              { shift_id: shiftVazioId, employee_ids: [] },
                            ],
                          },
                        }).then(() => {
                          cy.log(`✅ Setup completo para a semana de ${mondayStr}`);
                        });
                      });
                    });
                  });
                });
              });
            });
          });
        });
      });
    });
  });

  beforeEach(() => {
    cy.fixture('mockData').then((data) => {
      cy.loginViaApi(data.testUser.email, data.testUser.password);
    });
    cy.on('window:alert', () => true);
    cy.on('window:confirm', () => true);
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
        if (res.status !== 200) return;
        const t = res.body.access_token;
        cy.deleteEmployeeByNameViaApi(EMP_DISP_NAME, t);
        cy.deleteEmployeeByNameViaApi(EMP_INDISP_NAME, t);
        cy.request({
          method: 'DELETE',
          url: `${data.apiBase}/users/me`,
          headers: { Authorization: `Bearer ${t}` },
          failOnStatusCode: false,
        });
      });
    });
  });

  // ── CENÁRIO 1: Filtragem por disponibilidade ──────────────────────────────

  it('Cenário 1 — deve exibir apenas EmpDisponivel no slot TER 08:00–12:00', () => {
    goToScheduleRecords();

    cy.get('button').contains('Edit').click();
    cy.contains('Editing mode is active').should('be.visible');

    // Abre o slot do Turno Principal (tem o chip do EmpDisponivel)
    cy.get('td').filter(':has(.mol-schedule-employee-chip)').first().click({ force: true });
    cy.contains('Select Employees').should('be.visible');

    // EmpDisponivel deve estar na lista (disponível na TER 07:00–13:00)
    cy.get('.mol-slot-picker__list').contains(EMP_DISP_NAME).should('exist');

    // EmpIndisponivel NÃO deve estar na lista (sem disponibilidade na TER)
    cy.get('.mol-slot-picker__list').contains(EMP_INDISP_NAME).should('not.exist');

    cy.get('.mol-slot-picker button').contains('Finish').click();
  });

  // ── CENÁRIO 2: Exclusão de funcionário indisponível ───────────────────────

  it('Cenário 2 — EmpIndisponivel não deve aparecer no seletor do turno de terça', () => {
    goToScheduleRecords();

    cy.get('button').contains('Edit').click();
    cy.contains('Editing mode is active').should('be.visible');

    // Abre o slot do Turno Principal
    cy.get('td').filter(':has(.mol-schedule-employee-chip)').first().click({ force: true });
    cy.contains('Select Employees').should('be.visible');

    // Confirma explicitamente que EmpIndisponivel está ausente
    cy.get('.mol-slot-picker__list button').each(($btn) => {
      cy.wrap($btn).invoke('text').should('not.contain', EMP_INDISP_NAME);
    });

    cy.get('.mol-slot-picker button').contains('Finish').click();
  });

  // ── CENÁRIO 3: Salvamento de edição válida ────────────────────────────────

  it('Cenário 3 — ao selecionar EmpDisponivel e salvar, nome aparece no slot', () => {
    goToScheduleRecords();

    cy.get('button').contains('Edit').click();
    cy.contains('Editing mode is active').should('be.visible');

    // Abre o slot do Turno Principal
    cy.get('td').filter(':has(.mol-schedule-employee-chip)').first().click({ force: true });
    cy.contains('Select Employees').should('be.visible');

    // Garante que EmpDisponivel está selecionado (clica para confirmar seleção)
    cy.get('.mol-slot-picker__list').contains('button', EMP_DISP_NAME).click();
    // Reclica para restaurar (toggle on → off → on garante que termina selecionado)
    cy.get('.mol-slot-picker__list').contains('button', EMP_DISP_NAME).click();

    cy.get('.mol-slot-picker button').contains('Finish').click();
    cy.contains('Select Employees').should('not.exist');

    // Salva a escala
    cy.get('button').contains('Save').click();
    cy.contains('Editing mode is active').should('not.exist');

    // O chip do EmpDisponivel deve estar visível na tabela
    cy.get('.mol-schedule-employee-chip').contains(EMP_DISP_NAME).should('be.visible');
  });

  // ── CENÁRIO 4: Ausência de elegíveis ──────────────────────────────────────
  // O Turno Vazio (SAB 08:00–12:00, weekday=5) não tem nenhum funcionário atribuído
  // e nenhum funcionário possui disponibilidade no sábado:
  //   • EmpDisponivel: disponível apenas na terça (weekday=1)
  //   • EmpIndisponivel: disponível apenas na segunda (weekday=0)
  // Ao clicar no slot de sábado em modo de edição, a lista é imediatamente vazia.

  it('Cenário 4 — lista vazia quando nenhum funcionário tem disponibilidade para o slot', () => {
    goToScheduleRecords();

    cy.get('button').contains('Edit').click();
    cy.contains('Editing mode is active').should('be.visible');

    // O slot de sábado não tem nenhum funcionário atribuído → exibe "click" em edit mode
    // O texto "click" é renderizado APENAS em slots válidos sem funcionários
    cy.contains('td', 'click').first().click({ force: true });
    cy.contains('Select Employees').should('be.visible');

    // A lista deve estar imediatamente vazia — nenhum funcionário tem disponibilidade no sábado
    cy.get('.mol-slot-picker__list button').should('not.exist');

    cy.get('.mol-slot-picker button').contains('Finish').click();
    cy.contains('Select Employees').should('not.exist');
  });
});
