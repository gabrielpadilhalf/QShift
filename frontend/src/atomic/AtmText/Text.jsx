import { tv } from 'tailwind-variants';

/**
 * AtmText – typography variants
 * size: 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '4xl'
 * weight: 'normal' | 'medium' | 'semibold' | 'bold'
 * color: 'white' | 'muted' | 'faint' | 'green' | 'red' | 'blue'
 */
const textTv = tv({
  base: '',
  variants: {
    size: {
      xs: 'text-xs',
      sm: 'text-sm',
      base: 'text-base',
      lg: 'text-lg',
      xl: 'text-xl',
      '2xl': 'text-2xl',
      '4xl': 'text-4xl',
    },
    weight: {
      normal: 'font-normal',
      medium: 'font-medium',
      semibold: 'font-semibold',
      bold: 'font-bold',
    },
    color: {
      white: 'text-white',
      muted: 'text-slate-400',
      faint: 'text-slate-500',
      dimmer: 'text-slate-300',
      green: 'text-green-400',
      red: 'text-red-400',
      blue: 'text-blue-400',
      yellow: 'text-yellow-400',
      purple: 'text-purple-400',
      orange: 'text-orange-400',
    },
    hoverGroupColor: {
      white: 'group-hover:text-white',
      muted: 'group-hover:text-slate-400',
      indigo: 'group-hover:text-indigo-400',
    },
  },
  defaultVariants: {
    size: 'base',
    weight: 'normal',
    color: 'white',
  },
});

export function AtmText({
  as: Tag = 'span',
  size,
  weight,
  color,
  hoverGroupColor,
  className = '',
  children,
  ...props
}) {
  return (
    <Tag className={textTv({ size, weight, color, hoverGroupColor, class: className })} {...props}>
      {children}
    </Tag>
  );
}

export { textTv };
