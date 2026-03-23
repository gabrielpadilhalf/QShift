// MolScheduleTableBody.jsx
import React from 'react';
import { daysOfWeek } from '../../constants/constantsOfTable.js';
import { AtmText } from '../AtmText/Text.jsx';
import { TBody, TR, TH, TD } from '../AtmTable/index.js';

export function MolScheduleTableBody({ scheduleData, employeeList, visibleSlots, maxSlots, editMode, onSlotClick }) {
    return (
        <TBody>
            {Array.from({ length: maxSlots }).map((_, rowIndex) => (
                <TR key={rowIndex}>
                    {daysOfWeek.map((day) => {
                        const slot = scheduleData[day][rowIndex];
                        const employees = slot?.employees || [];
                        const isUnderStaffed = slot ? employees.length < slot.minEmployees : false;

                        return (
                            <React.Fragment key={day}>
                                {visibleSlots[day] && (
                                    <TD timeSlot={true}>
                                        {slot ? (
                                            <AtmText color='white' size='sm' weight='bold'>
                                                {slot.startTime}-{slot.endTime}
                                            </AtmText>
                                        ) : (
                                            <AtmText color='muted' size='sm'>—</AtmText>
                                        )}
                                    </TD>
                                )}
                                <TD
                                    underStaffed={isUnderStaffed}
                                    clickable={!!(editMode && slot)}
                                    onClick={() => slot && editMode && onSlotClick(slot, day)}
                                >
                                    <div className="min-h-[80px] flex flex-col gap-1">
                                        {slot ? (
                                            <>
                                                {isUnderStaffed && (
                                                    <AtmText color='red' size='xs' weight='medium' className="mb-1">
                                                        {employees.length}/{slot.minEmployees}
                                                    </AtmText>
                                                )}
                                                {employees.length > 0 ? (
                                                    employees.map((emp, i) => (
                                                        <div key={i} className="px-2 py-1 bg-blue-600/50 rounded text-center leading-none">
                                                            <AtmText color='white' size='sm' weight='medium'>
                                                                {emp.name}
                                                            </AtmText>
                                                        </div>
                                                    ))
                                                ) : (
                                                    <div className="text-center py-6">
                                                        <AtmText color='muted' size='sm'>
                                                            {editMode ? 'click' : '—'}
                                                        </AtmText>
                                                    </div>
                                                )}
                                            </>
                                        ) : (
                                            <div className="text-center py-6">
                                                <AtmText color='muted' size='sm'>—</AtmText>
                                            </div>
                                        )}
                                    </div>
                                </TD>
                            </React.Fragment>
                        );
                    })}
                </TR>
            ))}
            <TR dayOff={true}>
                {daysOfWeek.map((day) => {
                    const assignedIds = new Set(
                        scheduleData[day].flatMap((slot) => slot.employees.map((emp) => emp.id))
                    );
                    const onBreak = employeeList.filter((emp) => !assignedIds.has(emp.id));

                    return (
                        <React.Fragment key={day}>
                            {visibleSlots[day] && (
                                <TH>
                                    <AtmText color='muted' size='xs' weight='bold'>
                                        {day === 'Monday' ? 'Day off' : '—'}
                                    </AtmText>
                                </TH>
                            )}
                            <TD dayOff={true}>
                                <AtmText color='muted' size='sm' className='leading-none'>
                                    {onBreak.length > 0 ? onBreak.map((emp) => emp.name).join(', ') : '—'}
                                </AtmText>
                            </TD>
                        </React.Fragment>
                    );
                })}
            </TR>
        </TBody>
    );
}