import csv
from io import StringIO

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.repositories.patient_repository import patient_repository

router = APIRouter()


@router.get("/patients")
def export_patients_csv():
    patients = patient_repository.get_all_records()

    output = StringIO()

    fields = [
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

    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()

    for patient in patients:
        writer.writerow({
            field: patient.get(field)
            for field in fields
        })

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=patients.csv"
        }
    )