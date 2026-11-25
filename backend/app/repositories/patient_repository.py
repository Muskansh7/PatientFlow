
from app.schemas import PatientCreate, PatientUpdate



class PatientRepository:
    def get_all_records(self):
        return list(self._patients.values())

    def __init__(self):
        self._patients = {}
        self._history = {}
        self._next_id = 1

    def create(self, patient: PatientCreate):
        data = patient.model_dump()
        data["id"] = self._next_id

        self._patients[self._next_id] = data
        self._next_id += 1

        return data

    def get_all(
        self,
        search=None,
        ward=None,
        department=None,
        doctor=None,
        status=None,
        sort_by="id",
        sort_order="asc",
        page=1,
        page_size=10
    ):
        patients = list(self._patients.values())

        if search:
            patients = [
                p for p in patients
                if search.lower() in p["name"].lower()
            ]

        if ward:
            patients = [
                p for p in patients
                if p["ward"].lower() == ward.lower()
            ]

        if department:
            patients = [
                p for p in patients
                if p["department"].lower() == department.lower()
            ]

        if doctor:
            patients = [
                p for p in patients
                if p["doctor"].lower() == doctor.lower()
            ]

        if status:
            patients = [
                p for p in patients
                if p["status"] == status
            ]

        total = len(patients)

        patients.sort(
            key=lambda p: p.get(sort_by),
            reverse=sort_order == "desc"
        )

        start = (page - 1) * page_size
        end = start + page_size

        return {
            "items": patients[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    def get_by_id(self, patient_id: int):
        return self._patients.get(patient_id)

    def update(self, patient_id: int, patient: PatientUpdate):
        existing = self._patients.get(patient_id)

        if existing is None:
            return None

        updates = patient.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        existing.update(updates)

        return existing

    def delete(self, patient_id: int):
        return self._patients.pop(patient_id, None)

    def discharge(self, patient_id: int):
        patient = self._patients.get(patient_id)

        if patient is None:
            return None

        patient["status"] = "Discharged"

        return patient

    
    def add_history(self, patient_id, action, details):
        from datetime import datetime

        event = {
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        self._history.setdefault(patient_id, []).append(event)

        return event

    def get_history(self, patient_id):
        return self._history.get(patient_id, [])


patient_repository = PatientRepository()
