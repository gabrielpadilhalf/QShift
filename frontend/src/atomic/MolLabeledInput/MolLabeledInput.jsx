import { AtmInput } from '../AtmInput/index.js';

/**
 * MolLabeledInput – label + input pairing
 * Used in login, register, and any form field.
 */
export function MolLabeledInput({ label, id, type = 'text', placeholder, value, onChange, required, className = '', inputClass = '', variant = 'default' }) {
  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-slate-300">
          {label}
        </label>
      )}
      <AtmInput
        type={type}
        id={id}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        variant={variant}
        className={inputClass}
      />
    </div>
  );
}
