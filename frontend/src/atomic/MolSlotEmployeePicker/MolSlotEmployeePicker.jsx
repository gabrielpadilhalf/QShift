import { AtmText } from "../AtmText/Text.jsx";
import { SelectableButton, Button } from "../AtmButton/index.js";
import { AtmAvatar } from "../AtmAvatar/index.js";
import { Check } from "lucide-react";

/**
 * MolSlotEmployeesPicker – employee selector for a time slot
 */
export function MolSlotEmployeesPicker({ day, slot, assignedEmployees, employeeList, onToggleEmployee, onClose }) {
    return (
        <div className="p-6">
            <div className="text-sm text-slate-400 mb-4">
                {day} | {slot.startTime} - {slot.endTime} {' '}
                <AtmText as="span" size="sm" color="muted" className="">
                    ({assignedEmployees.length}/{slot.minEmployees} employees)
                </AtmText>
            </div>
            <div className="space-y-2 max-h-96 overflow-y-auto mb-6">
                {employeeList
                    .filter((emp) => emp.active)
                    .map((emp) => {
                        const isSelected = assignedEmployees.some((assignedEmp) => assignedEmp.id === emp.id);
                        return (
                            <SelectableButton
                                key={emp.id}
                                selected={isSelected}
                                onClick={() => onToggleEmployee(emp, slot, day)}
                                size='md'
                                fullWidth={true}
                            >
                                <div className={`p-1.5 rounded-md ${isSelected ? 'bg-white/20' : 'bg-slate-700 group-hover:bg-slate-600'}`}>
                                    <AtmAvatar name={emp.name} active={emp.active} size='sm' />
                                </div>
                                <div className="flex items-center justify-between">
                                    <AtmText as="span" size="md" color="white" className="font-medium max-w-full break-all leading-none">{emp.name}</AtmText>
                                </div>
                                {isSelected && <Check size={20} className='ml-auto' />}
                            </SelectableButton>
                        );
                    })}
            </div>
            <Button onClick={onClose} fullWidth variant='primary' size='lg'>
                Finish
            </Button>
        </div>
    );
}