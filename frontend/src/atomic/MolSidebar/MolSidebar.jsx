import { X, LogOut, CalendarRange, BarChart3 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button, SelectableButton } from '../AtmButton/index.js';
import { AtmText } from '../AtmText/index.js';

const navItems = [
  { icon: CalendarRange, label: 'Create Schedule', path: '/staff', indexPage: 1 },
  { icon: BarChart3, label: 'Reports', path: '/reports', indexPage: 3 },
];

/**
 * MolSidebar – sidebar navigation + logout button
 */
export function MolSidebar({ currentPage, onClose }) {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  return (
    <div className="w-48 bg-slate-800 border-r border-slate-700 flex flex-col p-4 h-full">
      <div className="flex justify-between items-center mb-6 lg:hidden">
        <AtmText as="h2" size="xl" weight="bold">Menu</AtmText>
        <Button onClick={onClose} variant='ghost'>
          <X size={24} />
        </Button>
      </div>
      <div className="flex-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.indexPage;
          return (
            <SelectableButton
              key={item.path}
              selected={isActive}
              onClick={() => {
                navigate(item.path);
                onClose && onClose();
              }}
              className='mb-2'
              fullWidth={true}
            >
              <Icon size={20} />
              <AtmText size="sm" weight="medium">{item.label}</AtmText>
            </SelectableButton>
          );
        })}
      </div>
      <Button onClick={logout} variant='logout' fullWidth={true} size='md'>
        <LogOut size={20} />
        <AtmText size="sm" weight="medium">Logout</AtmText>
      </Button>
    </div>
  );
}
