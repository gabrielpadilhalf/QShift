import { tv } from 'tailwind-variants';

const trackTv = tv({
    base: 'relative inline-flex items-center rounded-full transition-colors duration-200 cursor-pointer shrink-0',
    variants: {
        checked: {
            true: 'bg-green-500',
            false: 'bg-slate-600',
        },
        size: {
            sm: 'w-8 h-4',
            md: 'w-11 h-6',
        },
    },
    defaultVariants: { checked: false, size: 'md' },
});

const thumbTv = tv({
    base: 'inline-block bg-white rounded-full shadow transform transition-transform duration-200',
    variants: {
        checked: {
            true: '',
            false: '',
        },
        size: {
            sm: 'w-3 h-3',
            md: 'w-4 h-4',
        },
    },
    compoundVariants: [
        { size: 'md', checked: true, class: 'translate-x-6' },
        { size: 'md', checked: false, class: 'translate-x-1' },
        { size: 'sm', checked: true, class: 'translate-x-4' },
        { size: 'sm', checked: false, class: 'translate-x-0.5' },
    ],
    defaultVariants: { checked: false, size: 'md' },
});

export function AtmToggle({ checked, onChange, activeLabel = 'Active', inactiveLabel = 'Inactive', size, className = '' }) {
    return (
        <label className={`flex items-center gap-2 cursor-pointer ${className}`}>
            <span className={trackTv({ checked, size })} onClick={onChange}>
                <span className={thumbTv({ checked, size })} />
            </span>
            <span className={`text-sm ${checked ? 'text-green-400' : 'text-slate-400'}`}>
                {checked ? activeLabel : inactiveLabel}
            </span>
        </label>
    );
}