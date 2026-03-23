/**
 * AtmCheckbox – styled checkbox with active/inactive label
 */
export function AtmCheckbox({ checked, onChange, activeLabel = 'Active', inactiveLabel = 'Inactive', className = '' }) {
  return (
    <label className={`flex items-center gap-3 cursor-pointer group ${className}`}>
      <div className="relative">
        <input
          type="checkbox"
          checked={checked}
          onChange={onChange}
          className="w-5 h-5 rounded border-2 border-slate-600 bg-slate-900 checked:bg-indigo-600 checked:border-indigo-600 cursor-pointer transition-colors focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-800"
        />
        {checked && (
          <svg
            className="absolute top-0.5 left-0.5 w-4 h-4 text-white pointer-events-none"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>
      <span className={`text-sm font-medium transition-colors ${checked ? 'text-green-400' : 'text-slate-500'}`}>
        {checked ? activeLabel : inactiveLabel}
      </span>
    </label>
  );
}
