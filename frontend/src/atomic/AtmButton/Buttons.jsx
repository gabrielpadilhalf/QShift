import { tv } from 'tailwind-variants';

// ─── Base button TV definitions ──────────────────────────────────────────────

/**
 * Button – blue navigation/action button (Back, Next, Save, Edit, etc.)
 */
export const ButtonTv = tv({
  base: 'flex justify-center items-center gap-2 rounded-lg transition-colors',
  variants: {
    fullWidth: {
      true: 'w-full',
      false: '',
    },
    responsive: {
      true: 'w-full sm:w-auto',
      false: '',
    },
    disabled: {
      true: 'opacity-50',
      false: '',
    },
    size: {
      col: 'px-4',
      sm: 'px-2 py-2',
      md: 'px-4 py-3 font-medium',
      lg: 'px-6 py-3 font-medium',
    },
    variant: {
      primary: 'bg-blue-600 hover:bg-blue-700 text-white',
      secondary: 'bg-slate-700 hover:bg-slate-600 text-white',
      outline: 'border border-slate-500 text-slate-300 hover:bg-slate-800',
      ghost: 'text-slate-400 hover:text-white',
      danger: 'bg-red-600 hover:bg-red-700 text-white',
      columnDelete: 'bg-slate-800 hover:bg-red-600 text-slate-400 hover:text-white',
      success: 'bg-green-600 hover:bg-green-700 text-white',
      periodNav: 'p-2',
      logout: 'text-slate-300 hover:bg-red-600 hover:text-white gap-3',
    },
  },
  compoundVariants: [
    { variant: 'periodNav', disabled: true, className: 'opacity-50 cursor-not-allowed' },
    { variant: 'periodNav', disabled: false, className: 'hover:bg-slate-700' },
  ],
  defaultVariants: { fullWidth: false, responsive: false, size: '', variant: 'primary', disabled: false },
});

export function Button({ onClick, children, fullWidth, responsive, size, variant, disabled, className = '', ...props }) {
  return (
    <button
      onClick={onClick}
      className={ButtonTv({ fullWidth, responsive, size, variant, disabled, class: className })}
      {...props}
    >
      {children}
    </button>
  );
}

// ─── CalendarDayButton: selected/disabled/currentMonth ────────────
const calendarDayTv = tv({
  base: 'w-16 px-6 py-3 text-center rounded-lg transition',
  variants: {
    selected: { true: '', false: '' },
    disabled: { true: '', false: '' },
    currentMonth: { true: '', false: '' },
  },
  compoundVariants: [
    { selected: true, class: 'bg-blue-600 text-white font-semibold' },
    { selected: false, currentMonth: true, disabled: false, class: 'text-slate-200 hover:bg-slate-700' },
    { selected: false, currentMonth: false, class: 'text-slate-500' },
    { selected: false, disabled: true, class: 'text-slate-400 cursor-not-allowed' },
  ],
  defaultVariants: { selected: false, disabled: false, currentMonth: true },
});

export function CalendarDayButton({ onClick, selected, disabled, currentMonth, children, className = '', ...props }) {
  return (
    <button onClick={onClick} className={calendarDayTv({ selected, disabled, currentMonth, class: className })} {...props}>
      {children}
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * SelectableButton – buttons that can be selected (employee list in modals)
 */
export const selectableButtonTv = tv({
  base: 'flex rounded-lg text-left items-center gap-3 group transition-all',
  variants: {
    selected: {
      true: 'bg-blue-600 text-white shadow-md',
      false: 'text-slate-300 hover:bg-slate-700/50',
    },
    fullWidth: {
      true: 'w-full',
      false: '',
    },
    size: {
      sm: 'px-2 py-1',
      md: 'px-4 py-2',
      lg: 'px-6 py-4',
    },
  },
  defaultVariants: { selected: false, size: 'md', fullWidth: false },
});

export function SelectableButton({ onClick, children, selected, size, fullWidth, className = '', ...props }) {
  return (
    <button
      onClick={onClick}
      className={selectableButtonTv({ selected, size, fullWidth, class: className })}
      {...props}
    >
      {children}
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * LinkButton – inline text link button (blue, underline on hover)
 */
export const linkButtonTv = tv({
  base: 'text-blue-400 hover:text-blue-300 font-medium hover:underline transition-colors',
});

export function LinkButton({ onClick, children, className = '', type = 'button', ...props }) {
  return (
    <button type={type} onClick={onClick} className={linkButtonTv({ class: className })} {...props}>
      {children}
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * AccordionButton – collapsible section header button (full width, flex between)
 */
export const accordionButtonTv = tv({
  base: 'w-full flex items-center justify-between p-4 bg-slate-800 hover:bg-slate-700 transition-colors',
});

export function AccordionButton({ onClick, children, className = '', ...props }) {
  return (
    <button onClick={onClick} className={accordionButtonTv({ class: className })} {...props}>
      {children}
    </button>
  );
}
