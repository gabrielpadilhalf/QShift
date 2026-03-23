import { AtmDivider } from '../AtmDivider/index.js';
import { AtmText } from '../AtmText/index.js';

/**
 * MolPageHeader – page header with icon + title + children slot + divider
 */
export function MolPageHeader({ title, icon: Icon, children }) {
  return (
    <div className="mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          {Icon && <Icon size={32} className="text-blue-400" />}
          <AtmText as="h1" size="2xl" weight="bold">{title}</AtmText>
        </div>
        {children}
      </div>
      <AtmDivider />
    </div>
  );
}
