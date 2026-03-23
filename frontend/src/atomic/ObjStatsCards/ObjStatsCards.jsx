import { months } from '../../constants/constantsOfTable.js';
import { AtmText } from '../AtmText/Text.jsx';

export function ObjStatsCards({ statsCards, currentMonth, currentYear }) {
  return (
    <div className="flex gap-2 flex-wrap mb-4 justify-center lg:justify-start">
      {statsCards.map((card) => (
        <div
          key={card.key}
          className={`bg-slate-800 rounded-lg p-3 w-40 border border-slate-700 hover:${card.borderColor} transition-colors`}
        >
          <AtmText as="p" size="sm" weight="medium" color="dimmer">{card.label}</AtmText>
          <AtmText as="p" size="4xl" weight="bold" color={card.color} className="max-w-full break-all leading-none">
            {card.value}
          </AtmText>
          <AtmText as="p" size="xs" weight="medium" color="muted">
            {months[currentMonth - 1]} {currentYear}
          </AtmText>
        </div>
      ))}
    </div>
  );
}

