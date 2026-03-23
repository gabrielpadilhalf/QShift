import { ObjAppLayout as BaseLayout } from '../atomic/ObjAppLayout';
import { MolPageHeader } from '../atomic/MolPageHeader';
import { ObjEmployeeSelector } from '../atomic/ObjEmployeeSelector';
import { ObjStatsCards } from '../atomic/ObjStatsCards';
import { ObjChartHeader } from '../atomic/ObjChartHeader';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart3, ArrowLeft } from 'lucide-react';
import {
  METRIC_COLORS,
  STATS_CONFIG,
  METRIC_TITLES,
  COLORS_CHART,
} from '../constants/employeeStatsConfig.js';
import { EmployeeReportsApi } from '../services/api.js';
import { ObjBarChart } from '../atomic/ObjBarChart';
import { months } from '../constants/constantsOfTable.js';
import { Button } from '../atomic/AtmButton/index.js';
import { AtmText } from '../atomic/AtmText/index.js';
import { MolLoadingPage } from '../atomic/MolLoadingPage';

function EmployeeReportsPage({
  isLoading,
  setIsLoading,
  employeesList,
  currentEmployee,
  setCurrentEmployee,
}) {
  const navigate = useNavigate();
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [selectedMetric, setSelectedMetric] = useState('daysWorked');
  const [employeeYearStats, setEmployeeYearStats] = useState(null);
  const [statsCards, setStatsCards] = useState([]);

  const convertEmployeeStatsFormat = (stats) => ({
    name: stats.name,
    monthsData: stats.months_data.map((monthData) => ({
      hoursWorked: monthData.hours_worked,
      daysOff: monthData.num_days_off,
      daysWorked: monthData.num_days_worked,
      monrningShifts: monthData.num_morning_shifts,
      afternoonShifts: monthData.num_afternoon_shifts,
      nightShifts: monthData.num_night_shifts,
    })),
  });

  const createStatsCards = (employeeStatsFormatted) =>
    STATS_CONFIG.map((config) => ({
      ...config,
      ...METRIC_COLORS[config.key],
      value: config.suffix
        ? `${employeeStatsFormatted.monthsData[currentMonth - 1][config.key]}${config.suffix}`
        : employeeStatsFormatted.monthsData[currentMonth - 1][config.key],
    }));

  useEffect(() => {
    if (!currentEmployee) {
      if (employeesList.length > 0) { setCurrentEmployee(employeesList[0]); }
      else { alert('No employees available. Redirecting to Reports page.'); navigate('/reports'); return; }
    }
    async function fetchEmployeeStats() {
      const cacheKey = `employee_stats_${currentEmployee.id}_${currentYear}`;
      try {
        const cachedData = sessionStorage.getItem(cacheKey);
        if (cachedData) {
          const f = JSON.parse(cachedData);
          setEmployeeYearStats(f);
          setStatsCards(createStatsCards(f));
          setIsLoading(false);
          return;
        }
      } catch (error) { console.warn('Error reading from sessionStorage:', error); }
      try {
        const response = await EmployeeReportsApi.getEmployeeYearStats(currentEmployee.id, currentYear);
        if (response.data) {
          const f = convertEmployeeStatsFormat(response.data);
          setEmployeeYearStats(f);
          setStatsCards(createStatsCards(f));
          try { sessionStorage.setItem(cacheKey, JSON.stringify(f)); } catch (error) { console.warn('Error writing to sessionStorage:', error); }
        }
      } catch (error) { console.error('Error fetching employee statistics:', error); }
      finally { setIsLoading(false); }
    }
    if (currentEmployee) fetchEmployeeStats();
  }, [currentEmployee, currentMonth, currentYear]);

  const handleToggleEmployee = (employee) => setCurrentEmployee(employee);
  const handlePrevMonth = () => { if (currentMonth === 1) { setCurrentMonth(12); setCurrentYear(currentYear - 1); } else setCurrentMonth(currentMonth - 1); };
  const handleNextMonth = () => { if (currentMonth === 12) { setCurrentMonth(1); setCurrentYear(currentYear + 1); } else setCurrentMonth(currentMonth + 1); };
  const handlePrevYear = () => setCurrentYear(currentYear - 1);
  const handleNextYear = () => setCurrentYear(currentYear + 1);
  const handleBack = () => navigate('/reports');

  if (isLoading) return (
    <BaseLayout currentPage={10} showSidebar={false}>
      <MolLoadingPage />
    </BaseLayout>
  );

  return (
    <BaseLayout showSidebar={false} currentPage={10}>
      <MolPageHeader title="Employees Reports" icon={BarChart3} />
      <div className="flex flex-col lg:flex-row gap-4">
        <div className="w-full lg:w-80 shrink-0">
          <ObjEmployeeSelector
            employeesList={employeesList}
            currentEmployee={currentEmployee}
            onToggleEmployee={handleToggleEmployee}
            month={currentMonth}
            year={currentYear}
          />
        </div>

        <div className="flex-1 overflow-hidden">
          <ObjStatsCards statsCards={statsCards} currentMonth={currentMonth} currentYear={currentYear} />

          <ObjChartHeader
            selectedMetric={selectedMetric}
            setSelectedMetric={setSelectedMetric}
            currentMonth={currentMonth}
            currentYear={currentYear}
            onPrevMonth={handlePrevMonth}
            onNextMonth={handleNextMonth}
            onPrevYear={handlePrevYear}
            onNextYear={handleNextYear}
          />

          <div className="mt-1.5 bg-slate-800 rounded-lg border border-slate-700">
            <AtmText as="h3" size="lg" weight="bold" color="white" className="px-6 py-2 border-b border-slate-700">
              {METRIC_TITLES[selectedMetric]} - {currentYear}
            </AtmText>
            <div style={{ height: '400px', padding: '24px' }}>
              {(() => {
                if (!employeeYearStats) {
                  return <AtmText as="p" size="xl" color="muted" className="h-full flex items-center justify-center">No data available</AtmText>;
                }
                const data = {
                  labels: months,
                  datasets: [{
                    label: METRIC_TITLES[selectedMetric],
                    data: employeeYearStats.monthsData.map((monthData) => monthData[selectedMetric]),
                    backgroundColor: months.map((_, index) =>
                      index + 1 === currentMonth
                        ? METRIC_COLORS[selectedMetric].bgActiveHex
                        : METRIC_COLORS[selectedMetric].bgInactiveHex,
                    ),
                  }],
                };
                const options = {
                  responsive: true, maintainAspectRatio: false,
                  scales: {
                    y: { beginAtZero: true, ticks: { color: COLORS_CHART.textColorAxis }, grid: { color: COLORS_CHART.gridColor } },
                    x: { ticks: { color: COLORS_CHART.textColorAxis }, grid: { display: false } },
                  },
                  plugins: {
                    legend: { display: false },
                    tooltip: {
                      backgroundColor: COLORS_CHART.bgChart, displayColors: false,
                      titleColor: METRIC_COLORS[selectedMetric].textColorAxis,
                      bodyColor: METRIC_COLORS[selectedMetric].textColorHex,
                      borderColor: METRIC_COLORS[selectedMetric].borderColorHex, borderWidth: 1,
                    },
                  },
                };
                return <ObjBarChart key={`chart-${selectedMetric}-${currentYear}`} data={data} options={options} />;
              })()}
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 justify-start flex mt-4">
        <Button onClick={handleBack} variant='primary' className="w-full lg:w-auto" size='lg'>
          <ArrowLeft size={24} className="text-white" />
          <AtmText as="p" size="md" weight="bold" color="white">Back</AtmText>
        </Button>
      </div>
    </BaseLayout>
  );
}

export default EmployeeReportsPage;
