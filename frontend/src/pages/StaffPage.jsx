import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Plus, ArrowRight, AlertTriangle, X, Trash2 } from 'lucide-react';
import { ObjAppLayout as BaseLayout } from '../atomic/ObjAppLayout';
import { StaffApi } from '../services/api.js';
import { MolPageHeader } from '../atomic/MolPageHeader';
import { MolEmployeeCard } from '../atomic/MolEmployeeCard';
import { Button } from '../atomic/AtmButton/index.js';
import { MolLoadingPage } from '../atomic/MolLoadingPage';
import { ObjModal } from '../atomic/ObjModal';
import { AtmText } from '../atomic/AtmText/index.js';
import { MolAddEmployeeCard } from '../atomic/MolAddEmployeeCard';

function StaffPage({
  selectEditEmployee,
  setSelectEditEmployee,
  isLoading,
  setIsLoading,
  employees,
  setEmployees,
}) {
  const navigate = useNavigate();
  const [deleteConfirmation, setDeleteConfirmation] = useState(null);

  useEffect(() => {
    async function employeeData() {
      setIsLoading(true);
      try {
        const staffResponse = await StaffApi.getAll();
        setEmployees(staffResponse.data);
        sessionStorage.setItem('employees', JSON.stringify(staffResponse.data));
      } catch (error) {
        console.error('Error loading employee data:', error);
      } finally {
        setIsLoading(false);
      }
    }
    employeeData();
  }, []);

  const handleDeleteEmployee = async (employeeId) => {
    try {
      await StaffApi.deleteEmployee(employeeId);
      setEmployees((prevEmployees) => {
        const updatedEmployees = prevEmployees.filter((emp) => emp.id !== employeeId);
        sessionStorage.setItem('employees', JSON.stringify(updatedEmployees));
        return updatedEmployees;
      });
      setDeleteConfirmation(null);
    } catch (error) {
      console.error('Error deleting employee:', error);
      setDeleteConfirmation(null);
    }
  };

  const handleAddEmployee = () => {
    setSelectEditEmployee(null);
    navigate('/availability');
  };

  const handleEditEmployee = (employeeId) => {
    setIsLoading(true);
    const emp = employees.find((e) => e.id === employeeId);
    if (emp) {
      setSelectEditEmployee(emp);
      navigate('/availability');
    }
  };

  const handleToggleActive = async (employeeId, currentStatus) => {
    const emp = employees.find((e) => e.id === employeeId);
    if (emp) {
      const employeeData = { ...emp, active: !currentStatus };
      StaffApi.updateEmployeeData(employeeId, employeeData);
      setEmployees((prevEmployees) => {
        const updatedEmployees = prevEmployees.map((emp) =>
          emp.id === employeeId ? { ...emp, active: !emp.active } : emp,
        );
        sessionStorage.setItem('employees', JSON.stringify(updatedEmployees));
        return updatedEmployees;
      });
    }
  };

  const handleAdvance = () => {
    setIsLoading(true);
    navigate('/calendar');
  };

  if (isLoading) return (
    <BaseLayout currentPage={1} showSidebar={false}>
      <MolLoadingPage />
    </BaseLayout>
  );

  return (
    <BaseLayout currentPage={1}>
      <MolPageHeader title="Employee Management" icon={Users} />

      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {employees.map((employee) => (
            <MolEmployeeCard
              key={employee.id}
              employee={employee}
              onEdit={handleEditEmployee}
              onDelete={setDeleteConfirmation}
              onToggleActive={handleToggleActive}
            />
          ))}
          <MolAddEmployeeCard onAdd={handleAddEmployee} />
        </div>

        {employees.length === 0 ? (
          <div className="text-slate-400 text-center py-12">No employees registered yet</div>
        ) : (
          <div className="flex justify-end">
            <Button onClick={handleAdvance} variant='primary' size='lg'>
              Next
              <ArrowRight size={20} />
            </Button>
          </div>
        )}
      </div>

      {/* Delete confirmation modal */}
      {deleteConfirmation && (
        <ObjModal title="Confirm Delete" onClose={() => setDeleteConfirmation(null)}>
          <div className="space-y-5 p-4">

            <AtmText color="dimmer">
              Deleting this employee will also remove all associated history.
              Are you sure you want to proceed?
            </AtmText>

            <div className="bg-slate-900 rounded-lg border border-slate-700 px-4 py-3">
              <AtmText weight="semibold">
                {deleteConfirmation.name}
              </AtmText>

              <AtmText as='p' size="sm" color="dimmer" className="mt-1">
                This action cannot be undone.
              </AtmText>
            </div>

            <div className="flex items-center justify-end gap-3">
              <Button onClick={() => setDeleteConfirmation(null)} variant='secondary' size='lg'>
                Cancel
              </Button>

              <Button onClick={() => handleDeleteEmployee(deleteConfirmation.id)} variant='danger' size='lg'>
                <Trash2 className="w-4 h-4" />
                Delete
              </Button>
            </div>

          </div>
        </ObjModal>
      )}
    </BaseLayout>
  );
}

export default StaffPage;
