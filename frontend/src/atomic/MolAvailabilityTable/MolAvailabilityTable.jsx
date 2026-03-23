import { daysOfWeek } from '../../constants/constantsOfTable.js';
import { AtmText } from '../AtmText/index.js';

/**
 * MolAvailabilityTable – drag-to-paint availability grid
 */
export function MolAvailabilityTable({ hours, availability, onMouseDown, onMouseEnter }) {
  return (
    <div className="overflow-x-auto">
      <div className="inline-block min-w-full border border-slate-700 rounded-lg overflow-hidden">
        <div
          className="grid"
          style={{ gridTemplateColumns: `100px repeat(${hours.length}, minmax(40px, 1fr))` }}
        >
          {/* Header: corner */}
          <div className="sticky left-0 top-0 bg-slate-900/40 z-20 border border-slate-700" />
          {/* Header: hours */}
          {hours.map((hour) => (
            <div
              key={hour}
              className="text-center py-3 border border-slate-700 select-none bg-slate-900/40"
            >
              <AtmText size="xs" weight="medium" color="muted">{hour.split(':')[0]}h</AtmText>
            </div>
          ))}

          {/* Rows: days */}
          {daysOfWeek.map((day) => (
            <div key={`label-${day}`} className="contents">
              <div className="sticky left-0 bg-slate-900/40 z-10 py-2 px-3 flex items-center border border-slate-700/50">
                <AtmText size="sm" weight="medium" color="dimmer">{day}</AtmText>
              </div>
              {hours.map((hour) => (
                <div
                  key={`${day}-${hour}`}
                  onMouseDown={() => onMouseDown(day, hour)}
                  onMouseEnter={() => onMouseEnter(day, hour)}
                  className={`h-10 border border-slate-700/30 cursor-pointer transition-colors select-none ${availability[day][hour] ? 'bg-green-500 hover:bg-green-600' : 'bg-slate-900/40 hover:bg-slate-700/50'
                    }`}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
