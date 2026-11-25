
from fastapi import APIRouter, HTTPException, Query, Response
from app.schemas import PatientCreate, PatientUpdate, PatientResponse, PatientListResponse
from app.services.patient_service import patient_service
from app.repositories.patient_repository import patient_repository

router = APIRouter()


@router.post("/", response_model=PatientResponse, status_code=201)
def create_patient(patient: PatientCreate):
    try:
        return patient_service.create_patient(patient)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int):
    try:
        patient_service.delete_patient(patient_id)
        return Response(status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=PatientListResponse)
def get_patients(
    search: str | None = None,
    ward: str | None = None,
    department: str | None = None,
    doctor: str | None = None,
    status: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    try:
        return patient_service.get_all_patients(
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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int):
    try:
        return patient_service.get_patient(patient_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientUpdate):
    try:
        return patient_service.update_patient(patient_id, patient)
    except ValueError as e:
        raise HTTPException(status_code=404 if str(e) == "Patient not found" else 400, detail=str(e))





@router.patch("/{patient_id}/discharge", response_model=PatientResponse)
def discharge_patient(patient_id: int):
    try:
        return patient_service.discharge_patient(patient_id)
    except ValueError as e:
        raise HTTPException(status_code=404 if str(e) == "Patient not found" else 400, detail=str(e))


@router.get("/{patient_id}/history")
def get_patient_history(patient_id: int):
    patient = patient_repository.get_by_id(patient_id)

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient_repository.get_history(patient_id)
