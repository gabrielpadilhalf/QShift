import { tv } from 'tailwind-variants';

/**
 * Input atom – text, time, and number inputs
 * variant: 'default' | 'time' | 'number'
 */
const inputTv = tv({
  base: 'w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-400/60 transition-colors',
  variants: {
    size: {
      sm: 'px-2 py-1 text-xs',
      md: 'px-4 py-2 text-sm',
    },
    variant: {
      default: '',
      profile: 'bg-slate-900 border-slate-600 focus:border-blue-500 focus:outline-none focus:ring-0',
      auth: 'bg-slate-700 border-slate-500 focus:border-blue-500 focus:outline-none focus:ring-0',
      shiftConfig: 'bg-slate-700 border-slate-600 focus:border-blue-500 focus:outline-none focus:ring-0',
    },
  },
  defaultVariants: { size: 'md', variant: 'default' },
});

export function AtmInput({ size, variant, className = '', ...props }) {
  return (
    <input className={inputTv({ size, variant, class: className })} {...props} />
  );
}

export { inputTv };
