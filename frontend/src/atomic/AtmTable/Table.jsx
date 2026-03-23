import { tv } from 'tailwind-variants';

const tableTv = tv({
    slots: {
        table: 'w-full',
        thead: 'bg-slate-700',
        tbody: '',
        th: 'px-4 py-3 text-left border-r border-slate-600',
        tr: 'border-t border-slate-700',
        td: 'px-3 py-3 border-r border-slate-600 last:border-r-0',
    },
    variants: {
        underStaffed: {
            true: { td: 'bg-red-900/50' },
            false: {},
        },
        clickable: {
            true: { td: 'cursor-pointer hover:bg-slate-700' },
            false: {},
        },
        dayOff: {
            true: {
                tr: 'border-t-2 border-slate-600',
                td: 'text-center',
            },
            false: {},
        },
        timeSlot: {
            true: { td: 'bg-slate-750 text-xs' },
            false: {},
        },
        calendarHeader: {
            true: { th: 'text-center border-r-0', tr: 'bg-slate-700/90' },
            false: {},
        },
        calendarBody: {
            true: { tr: 'border-t border-slate-700 transition text-center', td: 'border-r-0 p-2' },
            false: {},
        },
    },
});

export function Table({ className, children, ...props }) {
    return (
        <table className={tableTv().table({ className })} {...props}>
            {children}
        </table>
    );
}
export function THead({ className, children, ...props }) {
    return <thead className={tableTv().thead({ className })} {...props}>{children}</thead>;
}
export function TBody({ className, children, ...props }) {
    return <tbody className={tableTv().tbody({ className })} {...props}>{children}</tbody>;
}
export function TR({ className, children, dayOff, calendarHeader, calendarBody, ...props }) {
    return <tr className={tableTv({ dayOff, calendarHeader, calendarBody }).tr({ className })} {...props}>{children}</tr>;
}
export function TH({ className, children, calendarHeader, ...props }) {
    return <th className={tableTv({ calendarHeader }).th({ className })} {...props}>{children}</th>;
}
export function TD({ className, children, underStaffed, clickable, timeSlot, onClick, dayOff, calendarBody, ...props }) {
    return (
        <td
            onClick={onClick}
            className={tableTv({ underStaffed, clickable, timeSlot, dayOff, calendarBody }).td({ className })}
            {...props}
        >
            {children}
        </td>
    );
}