import { useState, useMemo } from 'react';
import { daysOfWeek } from '../../constants/constantsOfTable.js';
import { ObjModal } from '../ObjModal';
import { MolSlotEmployeesPicker } from '../MolSlotEmployeePicker/index.js';
import { Table } from '../AtmTable/index.js';
import { MolScheduleTableHeader } from '../MolScheduleHeader';
import { MolScheduleTableBody } from '../MolScheduleBody';

/**
 * ObjScheduleTable – full schedule table with employee selector modal
 */
export function ObjScheduleTable({ scheduleData, setScheduleData, employeeList, week, editMode }) {
  const [showEmployeeSelector, setShowEmployeeSelector] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const maxSlots = Math.max(...daysOfWeek.map((day) => scheduleData[day].length));

  const hendleSelecetedDaysMap = () => {
    if (!week) {
      return { monday: null, tuesday: null, wednesday: null, thursday: null, friday: null, saturday: null, sunday: null };
    }
    const selecetedDaysMap = {};
    const [yearStartDate, monthStartDate, dayStartDate] = week.start_date.split('-').map(Number);
    const startDate = new Date(yearStartDate, monthStartDate - 1, dayStartDate);
    const year = startDate.getFullYear();
    const month = startDate.getMonth();
    const lastDay = new Date(year, month + 1, 0);
    daysOfWeek.forEach((day, index) => {
      selecetedDaysMap[day] =
        index + startDate.getDate() <= lastDay.getDate()
          ? index + startDate.getDate()
          : index + startDate.getDate() - lastDay.getDate();
    });
    return selecetedDaysMap;
  };

  const handleEmployeeSelector = (slot, day) => {
    setShowEmployeeSelector(true);
    setSelectedSlot({ slot, day });
  };

  const onToggleEmployee = (employee, slot, day) => {
    setScheduleData((data) => {
      const newData = { ...data };
      const dayData = [...newData[day]];
      newData[day] = dayData.map((slt) => {
        if (slt.id === slot.id) {
          const isSelected = slt.employees.some((emp) => emp.id === employee.id);
          const updatedEmployees = isSelected
            ? slt.employees.filter((emp) => emp.id !== employee.id)
            : [...slt.employees, employee];
          return { ...slt, employees: updatedEmployees };
        }
        return slt;
      });
      return newData;
    });
  };

  const areEqualSlots = (slots1, slots2) => {
    if (slots1.length !== slots2.length) return false;
    return slots1.every((slot1, index) => {
      const slot2 = slots2[index];
      return slot1.startTime === slot2.startTime && slot1.endTime === slot2.endTime;
    });
  };

  const visibleSlots = useMemo(() => {
    const visible = {};
    let previousSlots = [];
    daysOfWeek.forEach((day) => {
      const currentSlots = scheduleData[day];
      visible[day] = !areEqualSlots(currentSlots, previousSlots);
      previousSlots = currentSlots;
    });
    return visible;
  }, [scheduleData]);

  return (
    <div>
      <div className="bg-slate-800 rounded-lg overflow-hidden border border-slate-700 shadow-xl">
        <div className="overflow-x-auto">
          <Table>
            <MolScheduleTableHeader visibleSlots={visibleSlots} selectedDaysMap={hendleSelecetedDaysMap()} />
            <MolScheduleTableBody
              scheduleData={scheduleData}
              employeeList={employeeList}
              visibleSlots={visibleSlots}
              maxSlots={maxSlots}
              editMode={editMode}
              onSlotClick={handleEmployeeSelector}
            />
          </Table>
        </div>
      </div>
      {showEmployeeSelector && selectedSlot && (
        <ObjModal
          title="Select Employees"
          onClose={() => {
            setShowEmployeeSelector(false);
            setSelectedSlot(null);
          }}
        >
          <MolSlotEmployeesPicker
            day={selectedSlot.day}
            slot={selectedSlot.slot}
            assignedEmployees={scheduleData[selectedSlot.day].find((slt) => slt.id === selectedSlot.slot.id)?.employees || []}
            employeeList={employeeList}
            onToggleEmployee={onToggleEmployee}
            onClose={() => {
              setShowEmployeeSelector(false);
              setSelectedSlot(null);
            }}
          />
        </ObjModal>
      )}
    </div>
  );
}
