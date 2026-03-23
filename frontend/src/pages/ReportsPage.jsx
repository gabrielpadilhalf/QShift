import { Users, BarChart3, CalendarDays } from 'lucide-react';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ObjAppLayout as BaseLayout } from '../atomic/ObjAppLayout';
import { MolPageHeader } from '../atomic/MolPageHeader';
import { MolReportCard } from '../atomic/MolReportCard';
import { ReportsApi } from '../services/api.js';
import { MolLoadingPage } from '../atomic/MolLoadingPage';

function ReportsPage({
  weeksList,
  setWeeksList,
  isLoading,
  setIsLoading,
  setWeekRecords,
  currentIdxWeek,
  setCurrentIdxWeek,
  setCurrentEmployee,
  employees,
}) {
  const navigate = useNavigate();

  useEffect(() => {
    setIsLoading(true);
    setCurrentIdxWeek(0);
    async function getWeeks() {
      try {
        const weekResponse = await ReportsApi.getWeeks();
        setWeeksList(weekResponse.data);
      } catch (error) {
        console.error('Error loading API data:', error);
      } finally {
        setIsLoading(false);
      }
    }
    getWeeks();
  }, []);

  const reportCards = [
    { title: 'Employees', value: '', icon: Users },
    { title: 'Generated Scales', value: '', icon: CalendarDays },
  ];

  const handleCard = (card) => {
    if (card.title === 'Generated Scales') {
      setWeekRecords(weeksList[currentIdxWeek]);
      setIsLoading(true);
      navigate('/schedule-records');
    } else if (card.title === 'Employees') {
      setIsLoading(true);
      setCurrentEmployee(employees[0]);
      navigate('/employee-reports');
    }
  };

  if (isLoading) return (
    <BaseLayout currentPage={3} showSidebar={false}>
      <MolLoadingPage />
    </BaseLayout>
  );

  return (
    <BaseLayout currentPage={3} >
      <MolPageHeader title="Reports and Analysis" icon={BarChart3} />
      <div className="flex gap-4 flex-wrap">
        {reportCards.map((card, idx) => (
          <MolReportCard key={idx} card={card} onClick={handleCard} />
        ))}
      </div>
    </BaseLayout>
  );
}

export default ReportsPage;
