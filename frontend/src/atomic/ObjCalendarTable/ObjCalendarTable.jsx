import { MolCalendarThead } from '../MolCalendarThead';
import { MolCalendarWeekRow } from '../MolCalendarRow';
import { Table, TBody } from '../AtmTable/index.js';

function getMonthCalendar(year, month) {
  const firstDay = new Date(year, month - 1, 1);
  const lastDay = new Date(year, month, 0);
  const weeks = [];
  let currentWeek = [];
  const startDayOfWeek = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1;

  for (let i = 0; i < startDayOfWeek; i++) {
    currentWeek.push(new Date(year, month - 1, -startDayOfWeek + 1 + i));
  }
  for (let day = 1; day <= lastDay.getDate(); day++) {
    currentWeek.push(new Date(year, month - 1, day));
    if (currentWeek.length === 7) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
  }
  if (currentWeek.length > 0) {
    const remaining = 7 - currentWeek.length;
    for (let i = 1; i <= remaining; i++) {
      currentWeek.push(new Date(year, month, i));
    }
    weeks.push(currentWeek);
  }
  return weeks;
}

/**
 * ObjCalendarTable – full calendar table composed of MolCalendarThead + MolCalendarWeekRow[]
 */
export function ObjCalendarTable({
  currentMonth,
  currentYear,
  selectedDays,
  selectedWeek,
  onToggleDay,
  onToggleWeek,
  generatedWeeks,
}) {
  const weeks = getMonthCalendar(currentYear, currentMonth);

  const handleDayClick = (date, week, weekIdx) => {
    const isThisWeekSelected = selectedWeek === weekIdx + 1;
    if (!isThisWeekSelected) {
      onToggleWeek(week, weekIdx);
    } else {
      onToggleDay(date, true);
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-slate-800 rounded-lg overflow-hidden border border-slate-700 overflow-x-auto">
        <Table>
          <MolCalendarThead />
          <TBody>
            {weeks.map((week, weekIdx) => (
              <MolCalendarWeekRow
                key={weekIdx}
                week={week}
                weekIdx={weekIdx}
                currentMonth={currentMonth}
                selectedWeek={selectedWeek}
                selectedDays={selectedDays}
                generatedWeeks={generatedWeeks}
                onToggleWeek={onToggleWeek}
                onDayClick={handleDayClick}
              />
            ))}
          </TBody>
        </Table>
      </div>
    </div>
  );
}
