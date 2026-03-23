import { daysOfWeek } from '../../constants/constantsOfTable.js';
import { AtmText } from '../AtmText/index.js';
import { THead, TH, TR } from '../AtmTable/index.js';

/**
 * MolCalendarThead – calendar table header row with day-of-week labels
 */
export function MolCalendarThead() {
    return (
        <THead>
            <TR calendarHeader={true}>
                {daysOfWeek.map((day) => (
                    <TH key={day} calendarHeader={true}>
                        <AtmText size="sm" weight="bold" color="dimmer">{day}</AtmText>
                    </TH>
                ))}
            </TR>
        </THead>
    );
}