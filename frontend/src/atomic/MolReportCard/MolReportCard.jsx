import { AtmText } from '../AtmText/index.js';

/**
 * MolReportCard – a clickable card on the Reports page
 */
export function MolReportCard({ card, onClick }) {
  const Icon = card.icon;
  return (
    <div
      onClick={() => onClick(card)}
      className="bg-slate-800 rounded-lg p-6 w-64 border border-slate-700 hover:border-indigo-500 transition-all duration-200 overflow-hidden cursor-pointer"
    >
      <Icon size={40} className="text-blue-400 mb-4" />
      <AtmText as="p" size="4xl" weight="bold" color="muted" className="mb-2">{card.value}</AtmText>
      <AtmText as="p" size="sm" color="faint">{card.title}</AtmText>
    </div>
  );
}
