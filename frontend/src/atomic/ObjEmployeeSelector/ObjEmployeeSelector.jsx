import { useState } from 'react';
import { User, ChevronDown, ChevronUp } from 'lucide-react';
import { SelectableButton, AccordionButton } from '../AtmButton/index.js';
import { AtmText } from '../AtmText/index.js';
import { AtmAvatar } from '../AtmAvatar/Avatar.jsx';

/**
 * ObjEmployeeSelector – collapsible employee list panel (EmployeeReportsPage)
 */
export function ObjEmployeeSelector({ employeesList, currentEmployee, onToggleEmployee, month, year }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="bg-slate-800 rounded-lg shadow-xl w-full border border-slate-700 overflow-hidden transition-all duration-300">
      <AccordionButton onClick={() => setIsOpen(!isOpen)}>
        <div className="flex items-center gap-3">
          <div className="bg-blue-600/20 p-2 rounded-lg">
            <User className="text-blue-400" size={20} />
          </div>
          <AtmText as="h3" size="lg" weight="bold" color="dimmer">Employees</AtmText>
        </div>
        {isOpen ? (
          <ChevronUp className="text-slate-400" size={20} />
        ) : (
          <ChevronDown className="text-slate-400" size={20} />
        )}
      </AccordionButton>

      {isOpen && (
        <div className="p-3 border-t border-slate-700 bg-slate-800/50">
          <div className="space-y-1 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
            {employeesList.map((emp) => {
              const isSelected = emp.id === currentEmployee.id;
              return (
                <SelectableButton
                  key={emp.id}
                  selected={isSelected}
                  onClick={() => onToggleEmployee(emp, month, year)}
                  size='md'
                  fullWidth={true}
                >
                  <div className={`p-1.5 rounded-md ${isSelected ? 'bg-white/20' : 'bg-slate-700 group-hover:bg-slate-600'}`}>
                    <AtmAvatar name={emp.name} size='sm' active={emp.active} className={isSelected ? 'text-white' : 'text-slate-400'} />
                  </div>
                  <AtmText size="sm" weight="medium" className="truncate">{emp.name}</AtmText>
                  {isSelected && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-white" />}
                </SelectableButton>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
