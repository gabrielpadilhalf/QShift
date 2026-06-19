import { ObjAppLayout as BaseLayout } from '../atomic/ObjAppLayout';
import { MolPageHeader } from '../atomic/MolPageHeader';
import { ObjScheduleTable } from '../atomic/ObjScheduleTable';
import {
  CalendarRange,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  FileSpreadsheet,
  ArrowLeft,
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GeneratedScheduleApi, AvailabilityApi } from '../services/api.js';
import { exportToExcel } from '../utils/exportSchedule.js';
import { months, daysOfWeek, scheduleEmpty } from '../constants/constantsOfTable.js';
import { Button } from '../atomic/AtmButton/index.js';
import { AtmText } from '../atomic/AtmText/index.js';
import { MolLoadingPage } from '../atomic/MolLoadingPage';
import './ScheduleRecordsPage.css';

function ScheduleRecordsPage({
  employees,
  setEmployees,
  isLoading,
  setIsLoading,
  weeksList,
  setWeeksList,
  weekRecords,
  setWeekRecords,
  currentIdxWeek,
  setCurrentIdxWeek,
}) {
  const navigate = useNavigate();
  const [editMode, setEditMode] = useState(false);
  const [scheduleData, setScheduleData] = useState(scheduleEmpty);
  const [schedulesCache, setSchedulesCache] = useState({});
  const [availabilities, setAvailabilities] = useState([]);

  useEffect(() => {
    async function fetchAvails() {
      try {
        const response = await AvailabilityApi.getAllAvailabilities();
        setAvailabilities(response);
      } catch (error) {
        console.error('Error fetching availabilities:', error);
      }
    }
    fetchAvails();
  }, []);

  const convertScheduleData = (shifts) => {
    let scheduleModified = {
      Monday: [], Tuesday: [], Wednesday: [], Thursday: [], Friday: [], Saturday: [], Sunday: [],
    };
    shifts.forEach((shift) => {
      const dayName = daysOfWeek[shift.weekday];
      scheduleModified[dayName].push({
        id: shift.shift_id,
        startTime: shift.start_time.slice(0, 5),
        endTime: shift.end_time.slice(0, 5),
        minEmployees: shift.min_staff,
        employees: shift.employees.map((emp) => ({ id: emp.employee_id, name: emp.name })),
      });
    });
    daysOfWeek.forEach((day) => {
      scheduleModified[day].sort((a, b) => {
        if (a.startTime < b.startTime) return -1;
        if (a.startTime > b.startTime) return 1;
        if (a.endTime < b.endTime) return -1;
        if (a.endTime > b.endTime) return 1;
        return 0;
      });
    });
    return scheduleModified;
  };

  const formatWeekPeriod = (week) => {
    if (!week || !week.start_date) return '';
    const [y, m, d] = week.start_date.split('-').map(Number);
    const startDate = new Date(y, m - 1, d);
    const endDate = new Date(startDate.getTime() + 6 * 24 * 60 * 60 * 1000);
    const startMonth = months[startDate.getMonth()];
    const endMonth = months[endDate.getMonth()];
    if (startMonth === endMonth)
      return `${startDate.getDate()}-${endDate.getDate()} ${startMonth} ${startDate.getFullYear()}`;
    return `${startDate.getDate()} ${startMonth} - ${endDate.getDate()} ${endMonth} ${startDate.getFullYear()}`;
  };

  useEffect(() => {
    async function generateSchedule() {
      if (!weekRecords && currentIdxWeek != 0) { navigate('/reports'); return; }
      if (schedulesCache[weekRecords?.id]) { setScheduleData(schedulesCache[weekRecords.id]); return; }
      try {
        const response = await GeneratedScheduleApi.getGeneratedSchedule(weekRecords.id);
        if (response.data) {
          const convertedData = convertScheduleData(response.data.shifts);
          setScheduleData(convertedData);
          setSchedulesCache((prev) => ({ ...prev, [weekRecords.id]: convertedData }));
        }
      } catch (error) {
        console.error('Error receiving schedule:', error);
      } finally { setIsLoading(false); }
    }
    generateSchedule();
  }, [weekRecords?.id, weeksList, navigate]);

  const previousWeek = () => {
    if (weeksList && weeksList.length - 1 > currentIdxWeek) {
      setWeekRecords(weeksList[currentIdxWeek + 1]);
      setCurrentIdxWeek(currentIdxWeek + 1);
      setEditMode(false);
    }
  };

  const nextWeek = () => {
    if (currentIdxWeek > 0) {
      setWeekRecords(weeksList[currentIdxWeek - 1]);
      setCurrentIdxWeek(currentIdxWeek - 1);
      setEditMode(false);
    }
  };

  const handleEdit = () => setEditMode(!editMode);

  const handleShiftsSchedule = () => {
    const shiftsSchedule = { shifts: [] };
    daysOfWeek.forEach((day) => {
      if (scheduleData[day]) {
        scheduleData[day].forEach((shift) => {
          shiftsSchedule.shifts.push({
            shift_id: shift.id,
            employee_ids: shift.employees.map((employee) => employee.id),
          });
        });
      }
    });
    return shiftsSchedule;
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      const shiftsSchedule = handleShiftsSchedule();
      await GeneratedScheduleApi.deleteShiftsSchedule(weekRecords.id);
      setSchedulesCache((prev) => ({ ...prev, [weekRecords.id]: scheduleData }));
      await GeneratedScheduleApi.approvedSchedule(weekRecords.id, shiftsSchedule);
      setEditMode(false);
    } catch (error) {
      console.error('Error saving schedule:', error);
      throw error;
    } finally { setIsLoading(false); }
    setEditMode(false);
  };

  const handleBack = () => navigate('/reports');

  const handleExportCSV = () => {
    if (!scheduleData || !weekRecords) { alert('No schedule data to export'); return; }
    try {
      exportToExcel(scheduleData, weekRecords, employees);
    } catch (error) {
      console.error('Error exporting to CSV:', error);
      alert('Error exporting schedule to CSV. Please try again.');
    }
  };

  const handleDeleteSchedule = async () => {
    setIsLoading(true);
    try {
      await GeneratedScheduleApi.deleteSchedule(weekRecords.id);
      setSchedulesCache((prev) => { const u = { ...prev }; delete u[weekRecords.id]; return u; });
      if (weeksList.length === 1) {
        setWeekRecords(null); setCurrentIdxWeek(0); navigate('/reports');
      } else {
        const newWeeksList = weeksList.filter((week) => week.id !== weekRecords.id);
        setWeeksList(newWeeksList);
        if (currentIdxWeek === 0) { setWeekRecords(newWeeksList[0]); }
        else { setWeekRecords(newWeeksList[currentIdxWeek - 1]); setCurrentIdxWeek(currentIdxWeek - 1); }
      }
    } catch (error) {
      console.log('Error deleting schedule:', error);
      throw error;
    } finally { setEditMode(false); setIsLoading(false); }
  };

  const isPrevDisabled = !weeksList || weeksList.length - 1 <= currentIdxWeek;
  const isNextDisabled = currentIdxWeek <= 0;

  if (isLoading) return (
    <BaseLayout currentPage={8} showSidebar={false}>
      <MolLoadingPage />
    </BaseLayout>
  );

  return (
    <BaseLayout showSidebar={false} showSelectionPanel={true} selectionPanelData={null} currentPage={8}>
      <MolPageHeader title="Schedule Records" icon={CalendarRange}>
        <div className="schedule-records__header-nav">
          <div className="schedule-records__week-nav">
            <Button onClick={previousWeek} variant="periodNav" disabled={isPrevDisabled} title="Previous week">
              <ChevronLeft className='schedule-records__nav-icon' />
            </Button>
            <div className={`schedule-records__week-label-wrapper ${weekRecords ? 'schedule-records__week-label-wrapper--has-records' : ''}`}>
              <AtmText size="lg" weight="medium" color="muted" className="schedule-records__week-label">
                {formatWeekPeriod(weekRecords)}
              </AtmText>
            </div>
            <Button onClick={nextWeek} variant="periodNav" disabled={isNextDisabled} title="Next week">
              <ChevronRight className='schedule-records__nav-icon' />
            </Button>
          </div>
          <AtmText size="sm" color="muted" className="schedule-records__week-count">
            {weeksList && weeksList.length > 0 ? `Week ${currentIdxWeek + 1} of ${weeksList.length}` : ''}
          </AtmText>
        </div>
      </MolPageHeader>

      <div>
        {!weeksList || weeksList.length <= 0 ? (
          <div className="schedule-records__empty">
            <div className="schedule-records__empty-text">
              <AtmText as="p" size="lg" color="muted">No weekly schedule created</AtmText>
            </div>
          </div>
        ) : (
          <>
            {editMode && (
              <div className="schedule-records__edit-warning">
                <AlertTriangle size={24} className="text-yellow-400" />
                <AtmText as="p" size="sm" color="yellow" className="schedule-records__edit-warning-text">
                  Editing mode is active. Remember to save your changes.
                </AtmText>
              </div>
            )}
            <ObjScheduleTable
              scheduleData={scheduleData}
              setScheduleData={setScheduleData}
              employeeList={employees}
              week={weekRecords}
              editMode={editMode}
              availabilities={availabilities}
            />
          </>
        )}

        {!editMode ? (
          <div className="schedule-records__actions">
            <div className="schedule-records__actions-left">
              <div className="schedule-records__action-item">
                <Button onClick={handleBack} responsive variant='primary' size='lg'>Back</Button>
              </div>
            </div>
            {weeksList && weeksList.length > 0 && (
              <div className="schedule-records__actions-right">
                <div className="schedule-records__action-item">
                  <Button onClick={handleExportCSV} responsive variant='success' size='lg'>
                    <FileSpreadsheet size={20} />
                    Export CSV
                  </Button>
                </div>
                <div className="schedule-records__action-item">
                  <Button onClick={handleEdit} responsive variant='primary' size='lg'>Edit</Button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="schedule-records__edit-actions">
            <div className="schedule-records__edit-delete-wrapper">
              <div className="schedule-records__edit-delete-item">
                <Button onClick={handleDeleteSchedule} responsive variant='danger' size='lg'>Delete</Button>
              </div>
            </div>
            <div className="schedule-records__edit-save-wrapper">
              <div className="schedule-records__edit-save-item">
                <Button onClick={handleSave} responsive variant='primary' size='lg'>Save</Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </BaseLayout>
  );
}

export default ScheduleRecordsPage;
