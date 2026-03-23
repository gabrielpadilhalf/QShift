import { AtmInput } from '../AtmInput/index.js';
import { AtmCheckbox } from '../AtmCheckbox/index.js';
import { AtmText } from '../AtmText/index.js';
import { AtmAvatar } from '../AtmAvatar/index.js';

/**
 * MolEmployeeProfile – avatar + name input + active checkbox card
 */
export function MolEmployeeProfile({ name, setName, isActive, setIsActive, error }) {
  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 space-y-4">
      <div className="flex items-center gap-4">
        <AtmAvatar name={name} active={isActive} />
        <div className="flex-1">
          <AtmText as="label" size="sm" weight="medium" color="dimmer" className="block mb-2">
            Employee name
          </AtmText>
          <AtmInput
            type="text"
            value={name}
            maxLength={120}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter the name..."
            variant='profile'
          />
          {error && <AtmText as="p" size="xs" color="red" className="mt-1">{error}</AtmText>}
        </div>
      </div>

      <div className="flex items-center gap-3 pt-2">
        <AtmCheckbox
          checked={isActive}
          onChange={() => setIsActive(!isActive)}
          activeLabel="Active Employee"
          inactiveLabel="Inactive Employee"
        />
      </div>
    </div>
  );
}
