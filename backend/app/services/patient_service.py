from app.repositories.patient_repository import patient_repository
from app.schemas import PatientCreate, PatientUpdate
from app.validators import (
    validate_name,
    validate_age,
    validate_admission_date,
    validate_required_text
)


class PatientService:

    WARD_CAPACITY = {
        "General Ward": 10,
        "ICU": 5,
        "Emergency": 8,
        "Pediatric Ward": 6,
        "Private Ward": 4
    }

    DOCTOR_DEPARTMENTS = {
        "Dr. Amit Verma": "Cardiology",
        "Dr. Priya Sharma": "Neurology",
        "Dr. Rajesh Gupta": "Orthopedics",
        "Dr. Neha Singh": "Pediatrics",
        "Dr. Karan Mehta": "General Medicine"
    }

    def validate_doctor_department(self, doctor, department):
        expected_department = self.DOCTOR_DEPARTMENTS.get(doctor)

        if expected_department is None:
            raise ValueError(f"Unknown doctor: {doctor}")

        if expected_department != department:
            raise ValueError(
                f"{doctor} belongs to {expected_department}, not {department}"
            )

    def create_patient(self, patient: PatientCreate):
        validate_name(patient.name)
        validate_age(patient.age)
        validate_admission_date(patient.admission_date)
        validate_required_text(patient.ward, "Ward")
        validate_required_text(patient.department, "Department")
        validate_required_text(patient.doctor, "Doctor")

        self.validate_doctor_department(
            patient.doctor,
            patient.department
        )

        if patient.status == "Admitted":
            self.check_ward_capacity(patient.ward)

        created_patient = patient_repository.create(patient)

        patient_repository.add_history(
            created_patient["id"],
            patient.status,
            f"Patient {patient.status.lower()} in {created_patient['ward']} "
            f"under {created_patient['department']}"
        )

        return created_patient

    def get_all_patients(
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
        allowed_sort_fields = [
            "id",
            "name",
            "age",
            "gender",
            "ward",
            "department",
            "doctor",
            "admission_date",
            "status"
        ]

        if sort_by not in allowed_sort_fields:
            raise ValueError("Invalid sorting field")

        if sort_order not in ["asc", "desc"]:
            raise ValueError("Sort order must be asc or desc")

        if page < 1:
            raise ValueError("Page must be greater than 0")

        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")

        return patient_repository.get_all(
            search=search,
            ward=ward,
            department=department,
            doctor=doctor,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )

    def get_patient(self, patient_id: int):
        patient = patient_repository.get_by_id(patient_id)

        if patient is None:
            raise ValueError("Patient not found")

        return patient

    def update_patient(self, patient_id: int, patient: PatientUpdate):
        existing = patient_repository.get_by_id(patient_id)

        if existing is None:
            raise ValueError("Patient not found")

        updates = patient.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        if "name" in updates:
            validate_name(updates["name"])

        if "age" in updates:
            validate_age(updates["age"])

        if "admission_date" in updates:
            validate_admission_date(updates["admission_date"])

        for field in ["ward", "department", "doctor"]:
            if field in updates:
                validate_required_text(updates[field], field.capitalize())

        target_ward = updates.get("ward", existing["ward"])
        target_department = updates.get(
            "department", existing["department"]
        )
        target_doctor = updates.get("doctor", existing["doctor"])
        target_status = updates.get("status", existing["status"])

        self.validate_doctor_department(
            target_doctor,
            target_department
        )

        if target_status == "Admitted":
            self.check_ward_capacity(
                target_ward,
                exclude_patient_id=patient_id
            )

        updated_patient = patient_repository.update(
            patient_id,
            patient
        )

        if updated_patient is None:
            raise ValueError("Patient not found")

        if updates:
            patient_repository.add_history(
                patient_id,
                "Updated",
                f"Updated fields: {', '.join(updates.keys())}"
            )

        return updated_patient

    def delete_patient(self, patient_id: int):
        patient = patient_repository.get_by_id(patient_id)

        if patient is None:
            raise ValueError("Patient not found")

        patient_repository.delete(patient_id)

        return patient

    def check_ward_capacity(self, ward, exclude_patient_id=None):
        capacity = self.WARD_CAPACITY.get(ward)

        if capacity is None:
            raise ValueError(f"Unknown ward: {ward}")

        patients = patient_repository.get_all_records()

        occupied = sum(
            1 for p in patients
            if p["ward"] == ward
            and p["status"] == "Admitted"
            and p["id"] != exclude_patient_id
        )

        if occupied >= capacity:
            raise ValueError(
                f"{ward} is full. Capacity is {capacity} patients."
            )

    def discharge_patient(self, patient_id: int):
        patient = patient_repository.get_by_id(patient_id)

        if patient is None:
            raise ValueError("Patient not found")

        if patient["status"] == "Discharged":
            raise ValueError("Patient is already discharged")

        discharged_patient = patient_repository.discharge(patient_id)

        patient_repository.add_history(
            patient_id,
            "Discharged",
            f"Patient discharged from {patient['ward']}"
        )

        return discharged_patient


patient_service = PatientService()