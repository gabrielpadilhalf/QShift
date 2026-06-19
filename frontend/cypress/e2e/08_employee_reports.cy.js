describe('Employee Reports: consistência de dados com o backend', () => {
  let createdEmployeeIds = [];
  let scheduleCreated = false;

  // ── SETUP: registro → funcionários → escala aprovada via API ─────────────
  before(() => {
    cy.fixture('mockData').then((data) => {
      cy.clearTemplatesDB();

      // 1. Limpa estado residual de runs anteriores
      cy.request({
        method: 'POST',
        url: `${data.apiBase}/auth/login`,
        body: { email: data.testUser.email, password: data.testUser.password },
        failOnStatusCode: false,
      }).then((loginRes) => {
        if (loginRes.status === 200) {
          const token = loginRes.body.access_token;
          data.employees.forEach((emp) => {
            cy.deleteEmployeeByNameViaApi(emp.name, token);
          });
          cy.request({
            method: 'DELETE',
            url: `${data.apiBase}/users/me`,
            headers: { Authorization: `Bearer ${token}` },
            failOnStatusCode: false,
          });
        }
      });

      // 2. Registra o usuário de teste via UI
      cy.visit('/register');
      cy.get('#email').type(data.testUser.email);
      cy.get('#confirm-email').type(data.testUser.email);
      cy.get('#password').type(data.testUser.password);
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/login');

      // 3. Login e criação de toda a estrutura de dados via API
      cy.request({
        method: 'POST',
        url: `${data.apiBase}/auth/login`,
        body: { email: data.testUser.email, password: data.testUser.password },
      }).then((loginRes) => {
        const token = loginRes.body.access_token;
        const headers = { Authorization: `Bearer ${token}` };

        // 3a. Cria funcionários com disponibilidade full-week
        data.employees.forEach((emp) => {
          cy.request({
            method: 'POST',
            url: `${data.apiBase}/employees`,
            headers,
            body: { name: emp.name, active: true, weekly_workload_hours: emp.workload },
          }).then((empRes) => {
            const empId = empRes.body.id;
            createdEmployeeIds.push(empId);
            [0, 1, 2, 3, 4, 5, 6].forEach((weekday) => {
              cy.request({
                method: 'POST',
                url: `${data.apiBase}/employees/${empId}/availabilities`,
                headers,
                body: { weekday, start_time: '06:00', end_time: '22:00' },
                failOnStatusCode: false,
              });
            });
          });
        });

        // 3b. Calcula a segunda-feira da semana atual
        const today = new Date();
        const dayOfWeek = today.getDay(); // 0=Dom, 1=Seg...
        const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
        const monday = new Date(today);
        monday.setDate(today.getDate() + daysToMonday);
        const mondayStr = monday.toISOString().split('T')[0];

        // 3c. Cria a semana para o mês atual (necessário para aparecer no report)
        cy.request({
          method: 'POST',
          url: `${data.apiBase}/weeks`,
          headers,
          body: { start_date: mondayStr, open_days: [0, 1, 2, 3, 4, 5] },
        }).then((weekRes) => {
          const weekId = weekRes.body.id;

          // 3d. Define os turnos da semana
          const shiftsToCreate = [];
          [0, 1, 2, 3, 4].forEach((weekday) => {
            shiftsToCreate.push({ weekday, start_time: '08:00', end_time: '12:00', min_staff: 2 });
            shiftsToCreate.push({ weekday, start_time: '11:00', end_time: '14:00', min_staff: 1 });
            shiftsToCreate.push({ weekday, start_time: '15:00', end_time: '19:00', min_staff: 2 });
          });
          shiftsToCreate.push({ weekday: 5, start_time: '09:00', end_time: '12:00', min_staff: 2 });
          shiftsToCreate.push({ weekday: 5, start_time: '13:00', end_time: '16:00', min_staff: 1 });
          shiftsToCreate.push({ weekday: 5, start_time: '16:00', end_time: '20:00', min_staff: 2 });

          // 3e. Cria todos os turnos e coleta seus IDs
          const shiftIds = [];
          shiftsToCreate.forEach((shift) => {
            cy.request({
              method: 'POST',
              url: `${data.apiBase}/weeks/${weekId}/shifts`,
              headers,
              body: shift,
            }).then((shiftRes) => {
              shiftIds.push(shiftRes.body.id);
            });
          });

          // 3f. Envia as atribuições → isso "aprova" a escala no backend
          cy.then(() => {
            const schedulePayload = {
              shifts: shiftIds.map((shiftId, idx) => ({
                shift_id: shiftId,
                // Distribui funcionários em round-robin pelos turnos
                employee_ids: [createdEmployeeIds[idx % createdEmployeeIds.length]],
              })),
            };

            cy.request({
              method: 'POST',
              url: `${data.apiBase}/weeks/${weekId}/schedule`,
              headers,
              body: schedulePayload,
            }).then(() => {
              scheduleCreated = true;
              cy.log(`✅ Escala aprovada via API para a semana de ${mondayStr}`);
            });
          });
        });
      });
    });
  });

  // ── beforeEach: autentica via API antes de cada teste ─────────────────────
  beforeEach(() => {
    cy.fixture('mockData').then((data) => {
      cy.loginViaApi(data.testUser.email, data.testUser.password);
    });
  });

  const loadEmployeesToSession = () => {
    cy.intercept('GET', '**/employees').as('loadEmployees');
    cy.visit('/staff');
    cy.wait('@loadEmployees').then((interception) => {
      if (interception.response.statusCode === 200 && interception.response.body.length > 0) {
        cy.window().then((win) => {
          win.sessionStorage.setItem('employees', JSON.stringify(interception.response.body));
        });
      }
    });
  };

  // ── Teste 1: navegação correta Reports → card Employees → /employee-reports
  it('deve navegar do card Employees em Reports para a página Employee Reports', () => {
    const alertStub = cy.stub();
    cy.on('window:alert', alertStub);

    loadEmployeesToSession();

    // Vai para /reports (página intermediária obrigatória no fluxo do app)
    cy.visit('/reports');
    cy.contains('Reports and Analysis').should('be.visible');

    // Clica no card "Employees" → deve navegar para /employee-reports
    cy.contains('Employees').click({ force: true });
    cy.url().should('include', '/employee-reports');
    cy.contains('Employees Reports').should('be.visible');

    // Confirma que alert() nunca foi chamado (bug corrigido)
    cy.then(() => {
      expect(alertStub).not.to.have.been.called;
    });
  });

  // ── Teste 2: dados consistentes com o backend (sem cache stale) ───────────
  it('deve chamar a API novamente ao retornar para Employee Reports na mesma sessão', () => {
    loadEmployeesToSession();

    // 1ª visita a /employee-reports
    cy.intercept('GET', '**/employees/*/report/**').as('firstFetch');
    cy.visit('/reports');
    cy.contains('Employees').click({ force: true });
    cy.url().should('include', '/employee-reports');
    cy.wait('@firstFetch');

    // Navega para outra página (simula mudança de contexto na mesma sessão)
    loadEmployeesToSession();

    // 2ª visita — a API deve ser chamada novamente (sem cache sessionStorage bloqueando)
    cy.intercept('GET', '**/employees/*/report/**').as('secondFetch');
    cy.visit('/reports');
    cy.contains('Employees').click({ force: true });
    cy.url().should('include', '/employee-reports');

    cy.wait('@secondFetch').then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });

  // ── Teste 3: horas exibidas com no máximo 2 casas decimais ───────────────
  it('não deve exibir horas com mais de 2 casas decimais', () => {
    loadEmployeesToSession();

    cy.intercept('GET', '**/employees/*/report/**').as('reportFetch');
    cy.visit('/reports');
    cy.contains('Employees').click({ force: true });
    cy.url().should('include', '/employee-reports');
    cy.wait('@reportFetch');

    // Nenhum número com 3+ casas decimais deve aparecer na tela
    cy.get('body').invoke('text').then((text) => {
      const hasExcessiveDecimals = /\d+\.\d{3,}/.test(text);
      expect(hasExcessiveDecimals).to.be.false;
    });
  });

  // ── TEARDOWN: remove dados criados pelo teste ─────────────────────────────
  after(() => {
    cy.fixture('mockData').then((data) => {
      cy.request({
        method: 'POST',
        url: `${data.apiBase}/auth/login`,
        body: { email: data.testUser.email, password: data.testUser.password },
        failOnStatusCode: false,
      }).then((res) => {
        if (res.status !== 200) return;
        const token = res.body.access_token;

        // Remove funcionários criados
        data.employees.forEach((emp) => {
          cy.deleteEmployeeByNameViaApi(emp.name, token);
        });

        // Remove o usuário de teste
        cy.request({
          method: 'DELETE',
          url: `${data.apiBase}/users/me`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false,
        });
      });
    });
  });
});
