import { ObjAppLayout as BaseLayout } from '../atomic/ObjAppLayout';
import { MolPageHeader } from '../atomic/MolPageHeader';
import { ObjScheduleTable } from '../atomic/ObjScheduleTable';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GeneratedScheduleApi, ShiftConfigApi } from '../services/api.js';
import { daysOfWeek, scheduleEmpty } from '../constants/constantsOfTable.js';
import { Button } from '../atomic/AtmButton/index.js';
import { MolLoadingPage } from '../atomic/MolLoadingPage';

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
      <div className="p-3">
        <ObjScheduleTable
          scheduleData={scheduleData}
          setScheduleData={setScheduleData}
          employeeList={employees}
          week={weekData}
          editMode={editMode}
        />

        {!editMode ? (
          <div className="flex flex-col-reverse sm:flex-row mt-4 gap-3 sm:gap-0">
            <div className="flex-1 justify-center sm:justify-start flex w-full sm:w-auto">
              <Button onClick={handleCancel} responsive variant='secondary' size='lg'>Cancel</Button>
            </div>
            <div className="justify-end flex flex-col sm:flex-row flex-1 w-full sm:w-auto gap-2 sm:gap-0">
              <div className="w-full sm:w-auto px-0 sm:px-2 py-1.5">
                <Button onClick={handleEdit} responsive variant='primary' size='lg'>Edit</Button>
              </div>
              <div className="w-full sm:w-auto px-0 sm:px-2 py-1.5">
                <Button onClick={handleApproved} responsive variant='success' size='lg'>Approved</Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex mt-4">
            <div className="flex-1 justify-center sm:justify-end flex w-full">
              <div className="w-full sm:w-auto px-0 sm:px-40 py-1.5">
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
