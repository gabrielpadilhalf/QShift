import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      alert('Session expired. Please log in again.');
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export const ShiftConfigApi = {
  createShift: async (week_id, shiftData) => {
    try {
      return await api.post(`/weeks/${week_id}/shifts`, shiftData);
    } catch (error) {
      console.error('Error creating a shift:', error);
      throw error;
    }
  },

  submitWeekData: async (week) => {
    try {
      return await api.post('/weeks', week);
    } catch (error) {
      console.error('Error creating a week:', error);
      throw error;
    }
  },
};

export const StaffApi = {
  getAll: async () => {
    return await api.get('/employees');
  },

  updateEmployeeData: async (employee_id, employeeData) => {
    try {
      return await api.patch(`/employees/${employee_id}`, employeeData);
    } catch (error) {
      console.error('Error updating employee:', error);
      throw error;
    }
  },

  deleteEmployee: async (employee_id) => {
    try {
      return await api.delete(`/employees/${employee_id}`);
    } catch (error) {
      console.error('Error removing employee:', error);
      throw error;
    }
  },
};

export const AvailabilityApi = {
  getAvailabilityEmployee: async (employeeId) => {
    try {
      const response = await api.get(`/employees/${employeeId}/availabilities`);
      return response.data;
    } catch (error) {
      console.error('Error receiving availability:', error);
      throw error;
    }
  },

  updateEmployeeAvailability: async (employeeId, availabilityId, availability) => {
    try {
      const response = await api.patch(
        `/employees/${employeeId}/availabilities/${availabilityId}`,
        availability,
      );
      return response.data;
    } catch (error) {
      console.error('Error updating availability:', error);
      throw error;
    }
  },

  createEmployeeAvailability: async (employeeId, availability) => {
    try {
      const response = await api.post(`/employees/${employeeId}/availabilities`, availability);
      return response.data;
    } catch (error) {
      console.error('Error creating availability:', error);
      console.error('Payload sent:', availability);
      console.error('Response:', error.response?.data);
      throw error;
    }
  },

  deleteEmployeeAvailability: async (employeeId, availabilityId) => {
    try {
      await api.delete(`/employees/${employeeId}/availabilities/${availabilityId}`);
      return { success: true };
    } catch (error) {
      console.error('Error deleting availability:', error);
      throw error;
    }
  },

  updateEmployeeAvailability: async (employeeId, availabilityId, availability) => {
    try {
      const response = await api.patch(
        `/employees/${employeeId}/availabilities/${availabilityId}`,
        availability,
      );
      return response.data;
    } catch (error) {
      console.error('Error updating availability:', error);
      throw error;
    }
  },

  replaceAllAvailabilities: async (employeeId, availabilities) => {
    try {
      const current = await AvailabilityApi.getAvailabilityEmployee(employeeId);
      if (current && current.length > 0) {
        await Promise.all(
          current.map((av) => AvailabilityApi.deleteEmployeeAvailability(employeeId, av.id)),
        );
      }
      const created = [];
      availabilities.forEach((schemasDay) => {
        schemasDay.forEach(async (schema) => {
          const newAv = await AvailabilityApi.createEmployeeAvailability(employeeId, schema);
          created.push(newAv);
        });
      });
      return created;
    } catch (error) {
      console.error('Error replacing availabilities:', error);
      throw error;
    }
  },

  addNewEmployee: async (employeeData) => {
    try {
      const response = await api.post('/employees', employeeData);
      return response.data;
    } catch (error) {
      console.error('Error creating employee:', error);
      console.error('Response:', error.response?.data);
      throw error;
    }
  },
};

export const GeneratedScheduleApi = {
  deleteSchedule: async (week_id) => {
    try {
      return await api.delete(`/weeks/${week_id}`);
    } catch (error) {
      console.error('Error deleting schedule week:', error);
      throw error;
    }
  },

  createSchedulePreviewJob: async (shift_vector) => {
    try {
      return await api.post(`/preview-schedule`, shift_vector);
    } catch (error) {
      console.error('Error creating schedule preview job:', error);
      throw error;
    }
  },

  getScheduleGenerationJob: async (job_id) => {
    try {
      return await api.get(`/schedule-generation-jobs/${job_id}`);
    } catch (error) {
      console.error('Error fetching schedule generation job:', error);
      throw error;
    }
  },

  getGeneratedSchedule: async (week_id) => {
    try {
      return await api.get(`/weeks/${week_id}/schedule`);
    } catch (error) {
      console.error('Error fetching schedule:', error);
      throw error;
    }
  },

  approvedSchedule: async (week_id, schedule) => {
    try {
      return await api.post(`/weeks/${week_id}/schedule`, schedule);
    } catch (error) {
      console.error('Error sending approved schedule:', error);
      throw error;
    }
  },

  deleteShiftsSchedule: async (week_id) => {
    try {
      return await api.delete(`/weeks/${week_id}/schedule`);
    } catch (error) {
      console.error('Error deleting schedule shift list:', error);
      throw error;
    }
  },
};

export const LoginApi = {
  authenticateUser: async (email, password) => {
    try {
      return await api.post('/auth/login', { email, password });
    } catch (error) {
      console.error('Error sending login data:', error);
      throw error;
    }
  },
};

export const RegisterApi = {
  registerUser: async (email, password) => {
    try {
      return await api.post('/users', { email, password });
    } catch (error) {
      console.error('Error sending registration data:', error);
      throw error;
    }
  },
};

export const CalendarApi = {
  getWeeks: async () => {
    return await api.get('/weeks');
  },
};

export const ReportsApi = {
  getWeeks: async () => {
    return await api.get('/weeks');
  },
};

export const EmployeeReportsApi = {
  getEmployeeYearStats: async (employee_id, year) => {
    try {
      return await api.get(`/employees/${employee_id}/report/${year}`);
    } catch (error) {
      console.error('Error fetching employee annual report:', error);
      throw error;
    }
  },

  getEmployeeMonthStats: async (employee_id, month, year) => {
    try {
      return await api.get(`/employees/${employee_id}/report/${year}/${month}`);
    } catch (error) {
      console.error('Error fetching employee monthly report:', error);
      throw error;
    }
  },
};
