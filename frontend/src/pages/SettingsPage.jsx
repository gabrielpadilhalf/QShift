import { Settings } from 'lucide-react';
import { ObjAppLayout } from '../atomic/ObjAppLayout';
import { MolPageHeader } from '../atomic/MolPageHeader';
import { AtmText } from '../atomic/AtmText/index.js';

function SettingsPage() {
  return (
    <ObjAppLayout currentPage={4}>
      <MolPageHeader title="System Settings" icon={Settings} />
      <div className="space-y-4">
        <AtmText size="sm" color="muted">Configurations under development...</AtmText>
      </div>
    </ObjAppLayout>
  );
}

export default SettingsPage;
