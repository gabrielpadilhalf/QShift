import { ObjAppLayout as BaseLayout } from '../atomic/ObjAppLayout';
import { MolPageHeader } from '../atomic/MolPageHeader';
import { ObjScheduleTable } from '../atomic/ObjScheduleTable';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GeneratedScheduleApi, ShiftConfigApi, AvailabilityApi } from '../services/api.js';
import { daysOfWeek, scheduleEmpty } from '../constants/constantsOfTable.js';
import { Button } from '../atomic/AtmButton/index.js';
import { MolLoadingPage } from '../atomic/MolLoadingPage';
import './GeneratedSchedule.css';

function GeneratedSchedule({
  employees,
  setEmployees,
  isLoading,
  setIsLoading,
  weekData,
  setWeekData,
  shiftsData,
  setShiftsData,
  previewSchedule,
  setPreviewSchedule,
}) {
  const navigate = useNavigate();
  const [scheduleData, setScheduleData] = useState(previewSchedule || scheduleEmpty);
  const [editMode, setEditMode] = useState(false);
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

  useEffect(() => {
    if (!previewSchedule || !weekData || employees.length === 0) {
      navigate('/staff');
      return;
    }
    if (isLoading) setIsLoading(false);
  }, [previewSchedule, weekData, navigate]);

  const handleCancel = async () => {
    setWeekData(null);
    setShiftsData(null);
    setPreviewSchedule(null);
    navigate('/staff');
  };

  const handleEdit = () => setEditMode(!editMode);

  const handleShiftsSchedule = (responseShifts) => {
    return {
      shifts: responseShifts.map((respShift) => {
        const day = daysOfWeek[respShift.weekday];
        const previewShift = scheduleData[day]?.find(
          (s) =>
            s.startTime === respShift.start_time.slice(0, 5) &&
            s.endTime === respShift.end_time.slice(0, 5) &&
            s.minEmployees === respShift.min_staff,
        );
        return {
          shift_id: respShift.id,
          employee_ids: previewShift ? previewShift.employees.map((e) => e.id) : [],
        };
      }),
    };
  };

  async function handleApproved() {
    let newWeek = null;
    setIsLoading(true);
    try {
      newWeek = await ShiftConfigApi.submitWeekData(weekData).then((r) => r.data);
      const createdShifts = await Promise.all(
        shiftsData.map((shift) => ShiftConfigApi.createShift(newWeek.id, shift).then((r) => r.data)),
      );
      const shiftsSchedule = handleShiftsSchedule(createdShifts);
      await GeneratedScheduleApi.approvedSchedule(newWeek.id, shiftsSchedule);
      alert('Schedule created successfully!');
      navigate('/staff');
    } catch (error) {
      console.error('Error approving:', error);
      if (newWeek) {
        await GeneratedScheduleApi.deleteSchedule(newWeek.id).catch((e) =>
          console.error('Error deleting week:', e),
        );
      }
      alert('Error approving schedule.');
      setWeekData(null);
      setShiftsData(null);
      setPreviewSchedule(null);
      navigate('/staff');
    }
  }

  if (isLoading) return (
    <BaseLayout currentPage={7} showSidebar={false}>
      <MolLoadingPage />
    </BaseLayout>
  );

  return (
    <BaseLayout showSidebar={false} currentPage={7}>
      <MolPageHeader title="Generated Schedule" />
      <div className="generated-schedule__content">
        <ObjScheduleTable
          scheduleData={scheduleData}
          setScheduleData={setScheduleData}
          employeeList={employees}
          week={weekData}
          editMode={editMode}
          availabilities={availabilities}
        />

        {!editMode ? (
          <div className="generated-schedule__actions">
            <div className="generated-schedule__actions-left">
              <Button onClick={handleCancel} responsive variant='secondary' size='lg'>Cancel</Button>
            </div>
            <div className="generated-schedule__actions-right">
              <div className="generated-schedule__action-item">
                <Button onClick={handleEdit} responsive variant='primary' size='lg'>Edit</Button>
              </div>
              <div className="generated-schedule__action-item">
                <Button onClick={handleApproved} responsive variant='success' size='lg'>Approved</Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="generated-schedule__edit-actions">
            <div className="generated-schedule__edit-save-wrapper">
              <div className="generated-schedule__edit-save-item">
                <Button onClick={handleEdit} responsive variant='primary' size='lg'>Save</Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </BaseLayout>
  );
}

export default GeneratedSchedule;
