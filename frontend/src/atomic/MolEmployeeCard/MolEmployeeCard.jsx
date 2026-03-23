import { Trash2, Pencil } from 'lucide-react';
import { AtmAvatar } from '../AtmAvatar/index.js';
import { AtmToggle } from '../AtmToggle/index.js';
import { AtmCheckbox } from '../AtmCheckbox/index.js';
import { Button } from '../AtmButton/index.js';
import { AtmText } from '../AtmText/index.js';
import { AtmDivider } from '../AtmDivider/index.js';

/**
 * MolEmployeeCard – employee card with edit, delete, and active toggle buttons
 */
export function MolEmployeeCard({ employee, onEdit, onDelete, onToggleActive }) {
  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 hover:border-indigo-500 transition-all duration-200 p-4 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <AtmAvatar name={employee.name} active={employee.active} />
        <div className="flex gap-6">
          <Button variant="ghost" onClick={() => onEdit(employee.id)}>
            <Pencil className="h-5 w-5" />
          </Button>
          <Button variant="ghost" onClick={() => onDelete(employee)}>
            <Trash2 className="h-5 w-5" />
          </Button>
        </div>
      </div>
      <AtmText as="div" size="lg" weight="medium">
        {employee.name}
      </AtmText>
      <AtmDivider />
      <div className="flex items-center justify-between">
        <div className='flex flex-col'>
          <AtmText size="sm" color="muted">{employee.active ? 'Scheduled' : 'Unscheduled'}</AtmText>
        </div>
        <AtmCheckbox
          checked={employee.active}
          onChange={() => onToggleActive(employee.id, employee.active)}
          activeLabel="Active"
          inactiveLabel="Inactive"
        />
      </div>
    </div>
  );
}