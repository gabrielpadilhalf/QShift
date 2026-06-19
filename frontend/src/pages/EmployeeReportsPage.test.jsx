import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import EmployeeReportsPage from './EmployeeReportsPage.jsx';
vi.mock('../services/api.js', () => ({
  EmployeeReportsApi: {
    getEmployeeYearStats: vi.fn(),
  },
}));

import { EmployeeReportsApi } from '../services/api.js';

const mockApiResponse = {
  data: {
    name: 'Alice',
    months_data: Array.from({ length: 12 }, (_, i) => ({
      hours_worked: i === 0 ? 8.333333 : 160,  // mês 1 tem horas fracionadas
      num_days_off: 2,
      num_days_worked: 20,
      num_morning_shifts: 8,
      num_afternoon_shifts: 6,
      num_night_shifts: 6,
    })),
  },
};

const mockEmployee = { id: 42, name: 'Alice' };

// Helper para renderizar o componente com props mínimas
function renderPage({
  employeesList = [mockEmployee],
  currentEmployee = mockEmployee,
  setCurrentEmployee = vi.fn(),
  isLoading = false,
  setIsLoading = vi.fn(),
} = {}) {
  return render(
    <MemoryRouter>
      <EmployeeReportsPage
        isLoading={isLoading}
        setIsLoading={setIsLoading}
        employeesList={employeesList}
        currentEmployee={currentEmployee}
        setCurrentEmployee={setCurrentEmployee}
      />
    </MemoryRouter>,
  );
}

// ── Suite 1: sem funcionários disponíveis ────────────────────────────────────

describe('EmployeeReportsPage — sem funcionários', () => {
  let alertSpy;

  beforeEach(() => {
    alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => { });
  });

  afterEach(() => {
    alertSpy.mockRestore();
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  it('não deve chamar window.alert quando a lista de funcionários estiver vazia', () => {
    renderPage({ employeesList: [], currentEmployee: null });
    expect(alertSpy).not.toHaveBeenCalled();
  });

  it('deve exibir uma mensagem amigável na UI quando não há funcionários', () => {
    renderPage({ employeesList: [], currentEmployee: null });
    // O componente deve renderizar texto informativo em vez de lançar alert()
    expect(
      screen.getByText(/add employees first to view their reports/i),
    ).toBeInTheDocument();
  });
});

// ── Suite 2: dados sempre frescos da API (sem cache stale) ───────────────────

describe('EmployeeReportsPage — busca da API sem cache', () => {
  beforeEach(() => {
    EmployeeReportsApi.getEmployeeYearStats.mockResolvedValue(mockApiResponse);
    sessionStorage.clear();
  });

  afterEach(() => {
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  it('deve chamar a API na primeira montagem do componente', async () => {
    renderPage();
    await waitFor(() => {
      expect(EmployeeReportsApi.getEmployeeYearStats).toHaveBeenCalledTimes(1);
    });
  });

  it('deve chamar a API mesmo quando sessionStorage tem dados do mesmo funcionário/ano', async () => {
    // Simula o cenário do bug: cache stale presente de uma sessão anterior
    const cacheKey = `employee_stats_${mockEmployee.id}_${new Date().getFullYear()}`;
    const staleData = {
      name: 'Alice',
      monthsData: Array.from({ length: 12 }, () => ({
        hoursWorked: 999,
        daysOff: 0,
        daysWorked: 0,
        morningShifts: 0,
        afternoonShifts: 0,
        nightShifts: 0,
      })),
    };
    sessionStorage.setItem(cacheKey, JSON.stringify(staleData));

    renderPage();

    // Com o bug: a API NÃO seria chamada (retornaria do cache)
    // Comportamento esperado pós-fix: a API DEVE ser chamada
    await waitFor(() => {
      expect(EmployeeReportsApi.getEmployeeYearStats).toHaveBeenCalledTimes(1);
    });
  });

  it('não deve exibir 999 horas (dado stale do cache) após novo fetch', async () => {
    const cacheKey = `employee_stats_${mockEmployee.id}_${new Date().getFullYear()}`;
    const staleData = {
      name: 'Alice',
      monthsData: Array.from({ length: 12 }, () => ({
        hoursWorked: 999,
        daysOff: 0,
        daysWorked: 0,
        morningShifts: 0,
        afternoonShifts: 0,
        nightShifts: 0,
      })),
    };
    sessionStorage.setItem(cacheKey, JSON.stringify(staleData));

    renderPage();

    await waitFor(() => {
      expect(EmployeeReportsApi.getEmployeeYearStats).toHaveBeenCalled();
    });

    // O valor 999 (stale) não deve aparecer na tela
    expect(screen.queryByText(/999/)).not.toBeInTheDocument();
  });
});

// ── Suite 3: formatação de horas ─────────────────────────────────────────────

describe('EmployeeReportsPage — formatação de hoursWorked', () => {
  beforeEach(() => {
    EmployeeReportsApi.getEmployeeYearStats.mockResolvedValue(mockApiResponse);
    sessionStorage.clear();
  });

  afterEach(() => {
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  it('deve exibir horas com exatamente duas casas decimais (ex: "8.33h")', async () => {
    // O componente renderiza para o mês atual (janeiro = índice 0 se estivermos em janeiro,
    // mas nos stats cards. Aqui verificamos que nenhum valor com mais de 2 decimais aparece.
    renderPage();

    await waitFor(() => {
      expect(EmployeeReportsApi.getEmployeeYearStats).toHaveBeenCalled();
    });

    // Nenhum texto com mais de 2 casas decimais deve existir na tela
    const allText = document.body.textContent;
    // Regex: número com 3 ou mais casas decimais
    expect(allText).not.toMatch(/\d+\.\d{3,}/);
  });
});
