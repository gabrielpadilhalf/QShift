import { useState } from 'react';
import { Menu } from 'lucide-react';
import { MolSidebar } from '../MolSidebar';
import { MolWeekSelection } from '../MolWeekSelection';
import { MolDaysSelection } from '../MolDaysSelection';
import { Button } from '../AtmButton/index.js';
import { AtmText } from '../AtmText/index.js';

/**
 * ObjAppLayout – main app shell with optional sidebar and selection panel.
 * Replaces layouts/BaseLayout.jsx.
 *
 * Props:
 *   children         page content
 *   showSidebar?     (default true) show the left sidebar
 *   showSelectionPanel? (default false) show the right selection panel
 *   selectionPanelData? { startDate, selectedDays }
 *   currentPage      number identifying the active nav item
 */
export function ObjAppLayout({
  children,
  showSidebar = true,
  showSelectionPanel = false,
  selectionPanelData,
  currentPage,
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-slate-900 overflow-hidden">
      {/* Mobile top bar */}
      {showSidebar && (
        <div className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-slate-800 border-b border-slate-700 flex items-center px-4 z-40">
          <Button onClick={() => setIsSidebarOpen(true)} variant='ghost'>
            <Menu size={24} />
          </Button>
          <AtmText size="lg" weight="bold" className="ml-4">QShift</AtmText>
        </div>
      )}

      {/* Sidebar */}
      {showSidebar && (
        <>
          {isSidebarOpen && (
            <div
              className="fixed inset-0 bg-black/50 z-40 lg:hidden"
              onClick={() => setIsSidebarOpen(false)}
            />
          )}
          <div
            className={`fixed inset-y-0 left-0 z-50 w-48 transform transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
              }`}
          >
            <MolSidebar currentPage={currentPage} onClose={() => setIsSidebarOpen(false)} />
          </div>
        </>
      )}

      {/* Main content */}
      <div
        className={`flex-1 flex flex-col lg:flex-row lg:pt-0 overflow-auto lg:overflow-hidden ${showSidebar ? 'pt-16' : ''
          }`}
      >
        <div className="flex-1 p-4 w-full lg:overflow-auto">{children}</div>

        {showSelectionPanel && selectionPanelData && (
          <div className="border-t border-slate-700 bg-slate-900/50 lg:h-full lg:overflow-y-auto shrink-0">
            <div className="p-4 w-64 space-y-3 mt-5">
              <MolWeekSelection
                startDate={selectionPanelData.startDate}
                selectedDays={selectionPanelData.selectedDays}
              />
              <MolDaysSelection selectedDays={selectionPanelData.selectedDays} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
