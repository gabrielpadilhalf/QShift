import { AtmText } from '../AtmText/index.js';

/**
 * MolWeekSelection – displays selected week summary (from / until)
 */
export function MolWeekSelection({ startDate, selectedDays }) {
  const formatDate = (date) => {
    if (!date) return '-';
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getEndDate = (start) => {
    if (!start) return null;
    const date = new Date(start);
    date.setDate(date.getDate() + 6);
    return date;
  };

  const hasSelection = selectedDays && selectedDays.length > 0;

  return (
    <div className="space-y-3 mt-4">
      <AtmText as="h3" size="xs" weight="semibold" color="muted" className="uppercase tracking-wider flex items-center gap-2">
        Week Selection
      </AtmText>
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="p-4 space-y-4">
          <div>
            <AtmText as="p" size="xs" color="faint" className="mb-1">Week of</AtmText>
            <AtmText as="p" weight="medium">
              {hasSelection ? formatDate(startDate) : 'No selection'}
            </AtmText>
          </div>
          <div className="border-t border-slate-700 pt-3">
            <AtmText as="p" size="xs" color="faint" className="mb-1">Until</AtmText>
            <AtmText as="p" weight="medium">
              {hasSelection ? formatDate(getEndDate(startDate)) : '-'}
            </AtmText>
          </div>
        </div>
      </div>
    </div>
  );
}
