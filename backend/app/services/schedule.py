import json
from datetime import datetime, time, timezone
from sqlalchemy import false
from sqlalchemy.orm import Session
from typing import List, Tuple
from uuid import UUID
from urllib import error as urllib_error
from urllib import request as urllib_request
from ortools.sat.python import cp_model

import app.schemas.schedule as schemas
import app.domain.shift as shift_domain
from app.core.config import settings
from app.core.logging import logger


def build_schedule_generation_payload(
    *,
    db: Session,
    user_id: UUID,
    shift_vector: List[schemas.PreviewShiftBase],
) -> schemas.ScheduleGenerationDispatchPayload:
    from app.models import Availability, Employee

    employees = (
        db.query(Employee)
        .filter(Employee.user_id == user_id, Employee.active == True)
        .order_by(Employee.name.asc(), Employee.id.asc())
        .all()
    )
    employee_ids = [employee.id for employee in employees]
    availabilities = (
        db.query(Availability)
        .filter(
            Availability.user_id == user_id,
            Availability.employee_id.in_(employee_ids) if employee_ids else false(),
        )
        .order_by(
            Availability.employee_id.asc(),
            Availability.weekday.asc(),
            Availability.start_time.asc(),
            Availability.end_time.asc(),
        )
        .all()
    )

    return schemas.ScheduleGenerationDispatchPayload(
        shift_vector=shift_vector,
        employees=[
            schemas.ScheduleGenerationEmployeeOut(id=employee.id, name=employee.name)
            for employee in employees
        ],
        availabilities=[
            schemas.ScheduleGenerationAvailabilityOut(
                employee_id=availability.employee_id,
                weekday=availability.weekday,
                start_time=availability.start_time,
                end_time=availability.end_time,
            )
            for availability in availabilities
        ],
    )


def dispatch_schedule_generation_job(
    dispatch_request: schemas.ScheduleGenerationDispatchRequest,
) -> None:
    base_url = settings.SCHEDULE_GENERATOR_BASE_URL.rstrip("/")
    url = f"{base_url}/internal/generate-schedule"
    payload = dispatch_request.model_dump(mode="json")
    body = json.dumps(payload).encode("utf-8")
    request = urllib_request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib_request.urlopen(
            request,
            timeout=settings.SCHEDULE_GENERATOR_TIMEOUT_SECONDS,
        ) as response:
            status_code = getattr(response, "status", response.getcode())
            if status_code >= 400:
                raise RuntimeError(
                    f"schedule generator returned unexpected status {status_code}"
                )
    except (urllib_error.URLError, urllib_error.HTTPError, TimeoutError, OSError) as exc:
        logger.error("Schedule generation dispatch failed for job %s: %s", dispatch_request.job_id, exc)
        raise RuntimeError("unable to dispatch schedule generation job") from exc


def build_schedule_generation_job_schema(
    job,
) -> schemas.ScheduleGenerationJobOut:
    result = None
    if job.result_payload is not None:
        result = schemas.SchedulePreviewOut.model_validate(job.result_payload)

    return schemas.ScheduleGenerationJobOut(
        job_id=job.id,
        status=schemas.ScheduleGenerationJobStatus(job.status),
        result=result,
        error=job.error_message,
    )


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def build_schedule_schema_from_db(week_id: UUID, user_id: UUID, db: Session):
    from app.models.shift import Shift
    from app.models import ShiftAssignment, Employee

    shifts = (
        db.query(Shift).filter(Shift.week_id == week_id, Shift.user_id == user_id).all()
    )
    schedule_shifts_out = []
    shift: Shift
    for shift in shifts:
        assignments = (
            db.query(ShiftAssignment)
            .filter(
                ShiftAssignment.shift_id == shift.id,
                ShiftAssignment.user_id == user_id,
            )
            .all()
        )
        schedule_shift_employees_out = []
        for assignment in assignments:
            employee = (
                db.query(Employee).filter(Employee.id == assignment.employee_id).first()
            )
            schedule_shift_employees_out.append(
                schemas.ScheduleShiftEmployeeOut(
                    employee_id=employee.id, name=str(employee.name)
                )
            )
        schedule_shifts_out.append(
            schemas.ScheduleShiftOut(
                shift_id=shift.id,
                weekday=shift.weekday,
                start_time=shift.start_time,
                end_time=shift.end_time,
                min_staff=shift.min_staff,
                employees=schedule_shift_employees_out,
            )
        )
    return schemas.ScheduleOut(shifts=schedule_shifts_out)


def _time_to_min(t: time) -> int:
    return t.hour * 60 + t.minute


class ScheduleGenerator:
    def __init__(
        self,
        *,
        shift_ids: List[UUID],
        employee_ids: List[UUID],
        employee_names: List[str],
        shift_vector: List[shift_domain.Shift],
        availability_matrix: List[List[bool]],
    ):

        self.shift_ids = shift_ids
        self.employee_ids = employee_ids
        self.employee_names = employee_names
        self.shift_vector = shift_vector
        self.availability_matrix = availability_matrix

        # Preprocessing
        self.num_shifts = len(self.shift_vector)
        self.num_employees = len(self.employee_ids)

        self.weekday = [s.weekday for s in self.shift_vector]  # 0..6
        self.start_time_minutes = [
            _time_to_min(s.start_time) for s in self.shift_vector
        ]
        self.end_time_minutes = [_time_to_min(s.end_time) for s in self.shift_vector]
        self.shift_duration_min = [
            max(0, self.end_time_minutes[i] - self.start_time_minutes[i])
            for i in range(self.num_shifts)
        ]
        self.demand = [s.min_staff for s in self.shift_vector]

        self.min_start = min(self.start_time_minutes)
        self.max_start = max(self.start_time_minutes)

        self.shifts_indices_by_day = {
            d: [i for i in range(self.num_shifts) if self.weekday[i] == d]
            for d in range(7)
        }
        self.num_search_workers = 8

    # Alternative way of initializing the class, using the database directly
    @classmethod
    def from_db(
        cls,
        *,
        db: Session,
        user_id: UUID,
        shift_vector: List[shift_domain.Shift],
    ):
        employee_ids, employee_names = cls._get_employees_for_user(
            db=db, user_id=user_id
        )
        shift_ids = cls._get_shift_ids(db=db, shift_vector=shift_vector)
        return cls(
            shift_ids=shift_ids,
            employee_ids=employee_ids,
            employee_names=employee_names,
            shift_vector=shift_vector,
            availability_matrix=cls._build_availability_matrix(
                db=db, shift_vector=shift_vector, employee_ids=employee_ids
            ),
        )

    @classmethod
    def _get_shift_ids(cls, db: Session, shift_vector: List[shift_domain.Shift]) -> List[UUID]:
        shift_ids = []
        for shift in shift_vector:
            shift_ids.append(shift.id)
        return shift_ids

    @classmethod
    def _get_employees_for_user(
        cls, user_id: UUID, db: Session
    ) -> Tuple[List[UUID], List[str]]:
        from app.models import Employee

        employees = db.query(Employee).filter(Employee.user_id == user_id, Employee.active == True ).all()
        employee_ids = []
        employee_names = []
        for employee in employees:
            employee_ids.append(employee.id)
            employee_names.append(employee.name)
        return employee_ids, employee_names

    @classmethod
    def _build_availability_matrix(
        cls,
        *,
        db: Session,
        shift_vector: List[shift_domain.Shift],
        employee_ids: List[UUID],
    ) -> List[List[bool]]:
        from app.models import Availability

        availability_matrix = [
            [False] * len(shift_vector) for _ in range(len(employee_ids))
        ]
        for i, shift in enumerate(shift_vector):
            for j in range(0, len(employee_ids)):
                availabilities = (
                    db.query(Availability)
                    .filter(Availability.employee_id == employee_ids[j])
                    .all()
                )
                for availability in availabilities:
                    if (
                        availability.weekday == shift.weekday
                        and availability.start_time <= shift.start_time
                        and availability.end_time >= shift.end_time
                    ):
                        availability_matrix[j][i] = True
                        break
        return availability_matrix

    def _check_overlapping(self, t1: int, t2: int) -> bool:
        """Checks if two shifts overlap."""
        if self.weekday[t1] != self.weekday[t2]:
            return False
        return (
            self.end_time_minutes[t1] > self.start_time_minutes[t2]
            and self.end_time_minutes[t2] > self.start_time_minutes[t1]
        ) or (
            self.end_time_minutes[t2] > self.start_time_minutes[t1]
            and self.end_time_minutes[t1] > self.start_time_minutes[t2]
        )

    def _build_feasibility_model(
        self,
    ) -> Tuple[cp_model.CpModel, List[List[cp_model.IntVar]]]:
        """
        Create CP-SAT model with hard constraints:
          - Exact coverage per shift
          - Availability
          - No overlapping shifts per employee
        """
        model = cp_model.CpModel()

        # x[e][t] is 1 if employee e works shift t, and 0 otherwise.
        x = [
            [model.NewBoolVar(f"x[{e},{t}]") for t in range(self.num_shifts)]
            for e in range(self.num_employees)
        ]

        # Availability
        for e in range(self.num_employees):
            for t in range(self.num_shifts):
                if not self.availability_matrix[e][t]:
                    # print(f"Employee {e} is not available for shift {t}.")
                    model.Add(x[e][t] == 0)

        # Not allow that one employee takes two shifts at the same time
        for t1 in range(self.num_shifts):
            for t2 in range(t1 + 1, self.num_shifts):
                if self._check_overlapping(t1, t2):
                    # print(f"Shifts {t1} and {t2} overlap.'")
                    for e in range(self.num_employees):
                        model.Add(x[e][t1] + x[e][t2] <= 1)

        return model, x

    def check_possibility(self) -> bool:
        """Checks if it's possible to build a schedule."""
        if self.num_shifts == 0:
            return True

        if self.num_employees == 0:
            return False

        has_any_availability = any(
            any(row) for row in self.availability_matrix
        )
        if not has_any_availability:
            return False

        model, _x = self._build_feasibility_model()

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15.0
        solver.parameters.num_search_workers = self.num_search_workers
        solver.parameters.stop_after_first_solution = True

        status = solver.Solve(model)
        return status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    def generate_schedule(self) -> schemas.ScheduleOut:
        """
        Lexicographic optimization in a single model:
          0) Penalizes not obeying the required number of employees per shift.
          1) Penalizes differences in total minutes worked per employee.
          2) Fixing (1), penalizes more than one shift by day by person.
        """

        if self.num_shifts == 0:
            return schemas.ScheduleOut(shifts=[])

        model, x = self._build_feasibility_model()
        max_working_time = sum(self.shift_duration_min)

        # Step 0: required number of employees per shift

        max_deviation_from_required_staff = max(self.num_employees, max(self.demand))

        deviation_from_required_staff = {}
        deviation1 = {}
        deviation2 = {}
        for t in range(self.num_shifts):
            deviation_from_required_staff[t] = model.NewIntVar(0, max_deviation_from_required_staff,
                                                               f"deviation_from_required_staff[{t}]")
            deviation1[t] = model.NewIntVar(0, max_deviation_from_required_staff, f"deviation1[{t}]")
            deviation2[t] = model.NewIntVar(0, max_deviation_from_required_staff, f"deviation2[{t}]")
            model.Add(sum(x[e][t] for e in range(self.num_employees)) - self.demand[t] == deviation1[t] - deviation2[t])
            model.Add(deviation_from_required_staff[t] == deviation1[t] + deviation2[t])

        model.Minimize(sum(deviation_from_required_staff.values()))
        solver0 = cp_model.CpSolver()
        solver0.parameters.max_time_in_seconds = 20.0
        solver0.parameters.num_search_workers = self.num_search_workers
        status0 = solver0.Solve(model)

        if status0 != cp_model.OPTIMAL and status0 != cp_model.FEASIBLE:
            print(
                "\033[91mWARNING:\033[0mNo feasible solution found for step 0. Status: ", solver0.StatusName()
            )
        else:
            best0_int = sum(int(solver0.Value(v)) for v in deviation_from_required_staff.values())
            if deviation_from_required_staff:
                model.Add(sum(deviation_from_required_staff.values()) <= best0_int)

        # Step 1: Fairness

        # Total minutes per employee
        H = {
            e: model.NewIntVar(0, max_working_time, f"H[{e}]")
            for e in range(self.num_employees)
        }
        for e in range(self.num_employees):
            model.Add(
                H[e]
                == sum(
                    self.shift_duration_min[t] * x[e][t] for t in range(self.num_shifts)
                )
            )

        total_minutes = sum(
            self.shift_duration_min[t] * int(self.demand[t])
            for t in range(self.num_shifts)
        )
        T = total_minutes // max(1, self.num_employees)

        # We want to minimize the sum of absolute deviations -> sum(|H_e - T|)
        devp = {}
        devm = {}
        dev = {}
        for e in range(self.num_employees):
            devp[e] = model.NewIntVar(0, total_minutes, f"devp[{e}]")
            devm[e] = model.NewIntVar(0, total_minutes, f"devm[{e}]")
            model.Add(H[e] - T == devp[e] - devm[e])
            dev[e] = model.NewIntVar(0, 2 * total_minutes, f"dev[{e}]")
            model.Add(dev[e] == devp[e] + devm[e])

        # Use solution of step 0 as a hint for step 1
        for e in range(self.num_employees):
            for t in range(self.num_shifts):
                model.AddHint(x[e][t], solver0.Value(x[e][t]))

        model.Minimize(sum(dev.values()))
        solver1 = cp_model.CpSolver()
        solver1.parameters.max_time_in_seconds = 20.0
        solver1.parameters.num_search_workers = self.num_search_workers
        status1 = solver1.Solve(model)
        if status1 != cp_model.OPTIMAL and status1 != cp_model.FEASIBLE:
            print(
                "\033[91mWARNING:\033[0mNo feasible solution found for step 1. Status: ", solver1.StatusName()
            )
            chosen_after_1 = solver0
        else:
            chosen_after_1 = solver1
            best_fairness = chosen_after_1.ObjectiveValue()
            fairness_tol = 0.05  # Tolerance to fairness loss during the next step
            model.Add(sum(dev.values()) <= int((1.0 + fairness_tol) * best_fairness))

        # Step 2: penalizes more than one 1 shift by day by person

        over_vars = []
        for e in range(self.num_employees):
            for d in range(7):
                day_shift_indices = self.shifts_indices_by_day[d]
                if not day_shift_indices:
                    continue
                max_day_slots = len(day_shift_indices)

                num_shifts_in_day = model.NewIntVar(
                    0, max_day_slots, f"num_shifts_in_day[{e},{d}]"
                )
                model.Add(num_shifts_in_day == sum(x[e][t] for t in day_shift_indices))

                # Violation variable (to be minimized)
                over = model.NewIntVar(0, max_day_slots, f"over[{e},{d}]")
                model.Add(over >= num_shifts_in_day - 1)
                over_vars.append(over)

        # Use solution of step 1 as a hint for step 2
        for e in range(self.num_employees):
            for t in range(self.num_shifts):
                model.ClearHints()
                model.AddHint(x[e][t], chosen_after_1.Value(x[e][t]))

        obj_over = sum(over_vars) if over_vars else 0
        model.Minimize(obj_over)

        solver2 = cp_model.CpSolver()
        solver2.parameters.max_time_in_seconds = 15.0
        solver2.parameters.num_search_workers = self.num_search_workers
        status2 = solver2.Solve(model)
        if status2 != cp_model.OPTIMAL and status2 != cp_model.FEASIBLE:
            print(
                f"\033[91mWARNING:\033[0mNo feasible solution found for step 2. Status: ", solver2.StatusName()
            )
            chosen_after_2 = solver1
        else:
            chosen_after_2 = solver2

        # Building Schema (ScheduleOut)
        schedule_shifts_out: List[schemas.PreviewScheduleShiftOut] = []
        for t in range(self.num_shifts):
            employees_out: List[schemas.ScheduleShiftEmployeeOut] = []
            for e in range(self.num_employees):
                if chosen_after_2.Value(x[e][t]) == 1:
                    employees_out.append(
                        schemas.ScheduleShiftEmployeeOut(
                            employee_id=self.employee_ids[e],
                            name=self.employee_names[e],
                        )
                    )
            s = self.shift_vector[t]
            schedule_shifts_out.append(
                schemas.PreviewScheduleShiftOut(
                    weekday=s.weekday,
                    start_time=s.start_time,
                    end_time=s.end_time,
                    min_staff=s.min_staff,
                    employees=employees_out,
                )
            )

        return schemas.PreviewScheduleOut(shifts=schedule_shifts_out)
