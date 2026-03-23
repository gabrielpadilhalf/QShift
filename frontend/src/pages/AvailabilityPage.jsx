import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Save, X } from 'lucide-react';
import { ObjAppLayout as BaseLayout } from '../atomic/ObjAppLayout';
import { MolPageHeader } from '../atomic/MolPageHeader';
import { MolEmployeeProfile } from '../atomic/MolEmployeeProfile';
import { MolAvailabilityTable } from '../atomic/MolAvailabilityTable';
import { MolAvailabilityThead } from '../atomic/MolAvailabilityThead';
import { Button } from '../atomic/AtmButton/index.js';
import { AvailabilityApi, StaffApi } from '../services/api.js';
import { daysOfWeek } from '../constants/constantsOfTable.js';
import { MolLoadingPage } from '../atomic/MolLoadingPage';

function AvailabilityPage({ selectEditEmployee, setSelectEditEmployee, isLoading, setIsLoading }) {
  const navigate = useNavigate();
  const hours = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);
  const [name, setName] = useState(selectEditEmployee?.name || '');
  const [isActive, setIsActive] = useState(selectEditEmployee?.active ?? true);
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [paintMode, setPaintMode] = useState(true);
  const [error, setError] = useState(null);

  const initializeAvailability = () => {
    const initial = {};
    daysOfWeek.forEach((day) => {
      initial[day] = {};
      hours.forEach((hour) => { initial[day][hour] = false; });
    });
    return initial;
  };

  const [availability, setAvailability] = useState(() => initializeAvailability());

  const updateAvaibility = (schemas) => {
    const updateAvailability = initializeAvailability();
    schemas.forEach((schema) => {
      let start_time = parseInt(schema.start_time.split(':')[0]);
      let end_time = schema.end_time;
      if (end_time === '23:59:59') { end_time = 24; } else { end_time = parseInt(schema.end_time.split(':')[0]); }
      const weekday = daysOfWeek[schema.weekday];
      Array.from({ length: end_time - start_time }).forEach(() => {
        const slotsTime = `${start_time.toString().padStart(2, '0')}:00`;
        start_time = start_time + 1;
        updateAvailability[weekday][slotsTime] = true;
      });
    });
    setAvailability(updateAvailability);
  };

  useEffect(() => {
    if (!selectEditEmployee?.id) return;
    async function fetchEmployee() {
      try {
        const ListSchemas = await AvailabilityApi.getAvailabilityEmployee(selectEditEmployee.id);
        updateAvaibility(ListSchemas);
      } catch (err) {
        console.error(err);
        alert('Error loading employee data. Please check the console.');
        navigate('/staff');
      } finally { setIsLoading(false); }
    }
    fetchEmployee();
  }, [selectEditEmployee?.id]);

  const handleMouseDown = (day, hour) => {
    setIsMouseDown(true);
    const newValue = !availability[day][hour];
    setPaintMode(newValue);
    toggleCell(day, hour, newValue);
  };

  const handleMouseEnter = (day, hour) => {
    if (isMouseDown) toggleCell(day, hour, paintMode);
  };

  const handleMouseUp = () => setIsMouseDown(false);

  const toggleCell = (day, hour, value) => {
    setAvailability((prev) => ({ ...prev, [day]: { ...prev[day], [hour]: value } }));
  };

  const handleCancel = () => {
    setSelectEditEmployee(null);
    navigate('/staff');
  };

  const convertAvailabilityToSchemas = () => {
    const SlotsDay = [];
    daysOfWeek.forEach((day, index) => {
      let slotsActive = [];
      let slotPrevious = false;
      const daySlots = availability[day];
      SlotsDay[index] = [];
      Object.entries(daySlots).forEach(([hourLabel, slot]) => {
        const hour = `${hourLabel}:00`;
        if (slot) { slotsActive.push(hour); }
        else if (!slot && slotPrevious) {
          SlotsDay[index].push({ start_time: slotsActive[0], end_time: hour });
          slotsActive = [];
        }
        slotPrevious = slot;
      });
      if (slotPrevious && slotsActive.length > 0) {
        SlotsDay[index].push({ start_time: slotsActive[0], end_time: '23:59:59' });
      }
    });
    const availabilitySchemas = [];
    SlotsDay.forEach((schemas, day) => {
      availabilitySchemas[day] = [];
      schemas.forEach((slot, index) => {
        availabilitySchemas[day][index] = { weekday: day, start_time: slot.start_time, end_time: slot.end_time };
      });
    });
    return availabilitySchemas;
  };

  const handleSave = async () => {
    if (!name.trim()) { setError('Employee name is required'); return; }
    setError(null);
    setIsLoading(true);
    try {
      const availabilitySchemas = convertAvailabilityToSchemas();
      let employeeId = selectEditEmployee?.id;
      if (!employeeId) {
        const newEmployee = await AvailabilityApi.addNewEmployee({ name, active: isActive });
        employeeId = newEmployee.id;
      } else {
        await StaffApi.updateEmployeeData(employeeId, { name, active: isActive });
      }
      try {
        await AvailabilityApi.replaceAllAvailabilities(employeeId, availabilitySchemas);
        setSelectEditEmployee(null);
        navigate('/staff');
      } catch (err) {
        console.error('Error saving availabilities:', err);
        await StaffApi.deleteEmployee(employeeId);
        alert('Error saving availabilities. Please try again.');
        setIsLoading(false);
      }
    } catch (err) {
      console.error('Error saving:', err);
      setError(err.response?.data?.detail || 'Error saving employee. Please try again.');
      setIsLoading(false);
    }
  };

  if (isLoading) return (
    <BaseLayout currentPage={5} showSidebar={false}>
      <MolLoadingPage />
    </BaseLayout>
  );

  return (
    <BaseLayout showSidebar={false} currentPage={5}>
      <MolPageHeader title="Employee availability" icon={Calendar} />

      <div className="space-y-6" onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp}>
        <MolEmployeeProfile
          name={name}
          setName={setName}
          isActive={isActive}
          setIsActive={setIsActive}
          error={error}
        />

        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <MolAvailabilityThead />
          <MolAvailabilityTable
            hours={hours}
            availability={availability}
            onMouseDown={handleMouseDown}
            onMouseEnter={handleMouseEnter}
          />
        </div>

        <div className="flex justify-end gap-3">
          <Button onClick={handleCancel} variant='secondary' size='lg'>
            <X size={24} className="text-white" />
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!name.trim()} variant='primary' className="disabled:bg-slate-700 disabled:cursor-not-allowed" size='lg'>
            <Save size={24} className="text-white" />
            Save
          </Button>
        </div>
      </div>
    </BaseLayout>
  );
}

export default AvailabilityPage;
