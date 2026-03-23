import { Plus } from 'lucide-react';
import { AtmText } from '../AtmText/index.js';

/**
 * MolAddEmployeeCard – card to add a new employee
 */
export function MolAddEmployeeCard({ onAdd }) {
    return (
        <button
            onClick={onAdd}
            className="rounded-lg border-2 border-dashed border-slate-700 hover:border-indigo-500 transition-all duration-200 p-4 flex flex-col items-center justify-center gap-3 min-h-[160px] group"
        >
            <div className="w-10 h-10 rounded-full border-2 border-dashed border-slate-600 group-hover:border-indigo-400 flex items-center justify-center transition-colors">
                <Plus className="h-5 w-5 text-slate-500 group-hover:text-indigo-400 transition-colors" />
            </div>
            <AtmText size="sm" color="muted" className="group-hover:text-indigo-400 transition-colors">
                Add New Employee
            </AtmText>
        </button>
    );
}