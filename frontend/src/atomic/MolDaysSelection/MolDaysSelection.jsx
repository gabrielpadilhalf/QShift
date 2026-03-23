import { AtmText } from '../AtmText/index.js';

/**
 * MolDaysSelection – displays selected days as chips
 */
export function MolDaysSelection({ selectedDays }) {
  const hasSelection = selectedDays && selectedDays.length > 0;

  return (
    <div className="space-y-3">
      <AtmText as="h3" size="xs" weight="semibold" color="muted" className="uppercase tracking-wider flex items-center gap-2">
        Selected Days
      </AtmText>
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 min-h-[100px]">
        {hasSelection ? (
          <div className="flex flex-wrap gap-2">
            {selectedDays.map((d) => (
              <div
                key={d.toISOString()}
                className="w-8 h-8 flex items-center justify-center bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-lg text-sm font-medium"
                title={d.toDateString()}
              >
                {d.getDate()}
              </div>
            ))}
          </div>
        ) : (
          <AtmText size="sm" color="faint" className="h-full flex items-center justify-center italic">
            No days selected
          </AtmText>
        )}
      </div>
    </div>
  );
}
