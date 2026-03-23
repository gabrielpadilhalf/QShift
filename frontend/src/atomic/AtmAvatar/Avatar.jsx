import { tv } from 'tailwind-variants';

const avatarTv = tv({
    base: 'relative flex items-center justify-center rounded-full bg-slate-600 text-white font-semibold shrink-0',
    variants: {
        size: {
            sm: 'w-6 h-6 text-xs',
            md: 'w-12 h-12 text-base',
            lg: 'w-16 h-16 text-xl',
        },
    },
    defaultVariants: { size: 'md' },
});

const statusDotTv = tv({
    base: 'absolute bottom-0 right-0 rounded-full border-2 border-slate-800',
    variants: {
        size: { sm: 'w-2 h-2', md: 'w-3 h-3', lg: 'w-4 h-4' },
        active: {
            true: 'bg-green-400',
            false: 'bg-slate-500',
        },
    },
    defaultVariants: { size: 'md', active: false },
});

function getInitials(name = '') {
    return name
        .trim()
        .split(' ')
        .filter(Boolean)
        .slice(0, 2)
        .map((w) => w[0].toUpperCase())
        .join('');
}

export function AtmAvatar({ name, active, size, className = '' }) {
    return (
        <div className={avatarTv({ size, class: className })}>
            {getInitials(name)}
            <span className={statusDotTv({ size, active })} />
        </div>
    );
}