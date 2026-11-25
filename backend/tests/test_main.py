
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import Patient, PatientHistory

TEST_DATABASE_URL = "sqlite:///./test_patientflow.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def clean_test_database():
    Base.metadata.create_all(bind=test_engine)

    db = TestSessionLocal()
    try:
        db.query(PatientHistory).delete()
        db.query(Patient).delete()
        db.commit()
    finally:
        db.close()

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_patient():
    patient = {
        "name": "Rahul Sharma",
        "age": 25,
        "gender": "Male",
        "ward": "General Ward",
        "department": "Cardiology",
        "doctor": "Dr. Amit Verma",
        "admission_date": "2026-11-25",
        "status": "Admitted"
    }

    response = client.post("/api/v1/patients/", json=patient)

    assert response.status_code == 201
    assert response.json()["name"] == "Rahul Sharma"
    assert response.json()["status"] == "Admitted"


def test_create_patient_invalid_age():
    patient = {
        "name": "Rahul Sharma",
        "age": 150,
        "gender": "Male",
        "ward": "General Ward",
        "department": "Cardiology",
        "doctor": "Dr. Amit Verma",
        "admission_date": "2026-11-25",
        "status": "Admitted"
    }

    response = client.post("/api/v1/patients/", json=patient)
    assert response.status_code == 422


def test_invalid_doctor_department():
    patient = {
        "name": "Rahul Sharma",
        "age": 25,
        "gender": "Male",
        "ward": "General Ward",
        "department": "Neurology",
        "doctor": "Dr. Amit Verma",
        "admission_date": "2026-11-25",
        "status": "Admitted"
    }

    response = client.post("/api/v1/patients/", json=patient)

    assert response.status_code == 400
    assert "belongs to Cardiology" in response.json()["detail"]


def test_ward_capacity():
    names = [
        "Test Patient A",
        "Test Patient B",
        "Test Patient C",
        "Test Patient D",
        "Test Patient E"
    ]

    for name in names:
        patient = {
            "name": name,
            "age": 25,
            "gender": "Male",
            "ward": "ICU",
            "department": "Cardiology",
            "doctor": "Dr. Amit Verma",
            "admission_date": "2026-11-25",
            "status": "Admitted"
        }

        response = client.post("/api/v1/patients/", json=patient)
        assert response.status_code == 201

    patient = {
        "name": "Overflow Patient",
        "age": 30,
        "gender": "Male",
        "ward": "ICU",
        "department": "Cardiology",
        "doctor": "Dr. Amit Verma",
        "admission_date": "2026-11-25",
        "status": "Admitted"
    }

    response = client.post("/api/v1/patients/", json=patient)

    assert response.status_code == 400
    assert "ICU is full" in response.json()["detail"]


def test_get_all_patients():
    response = client.get("/api/v1/patients/")

    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert isinstance(response.json()["items"], list)


def test_get_patient_by_id():
    response = client.get("/api/v1/patients/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_update_patient():
    update_data = {
        "age": 26,
        "ward": "General Ward"
    }

    response = client.put("/api/v1/patients/1", json=update_data)

    assert response.status_code == 200
    assert response.json()["age"] == 26
    assert response.json()["ward"] == "General Ward"


def test_discharge_patient():
    response = client.patch("/api/v1/patients/1/discharge")

    assert response.status_code == 200
    assert response.json()["status"] == "Discharged"


def test_delete_patient():
    response = client.delete("/api/v1/patients/1")

    assert response.status_code == 204

    response = client.get("/api/v1/patients/1")
    assert response.status_code == 404


def test_filter_by_ward():
    response = client.get("/api/v1/patients/?ward=ICU")

    assert response.status_code == 200

    for patient in response.json()["items"]:
        assert patient["ward"] == "ICU"


def test_filter_by_department():
    response = client.get("/api/v1/patients/?department=Cardiology")

    assert response.status_code == 200

    for patient in response.json()["items"]:
        assert patient["department"] == "Cardiology"


def test_filter_by_doctor():
    response = client.get("/api/v1/patients/?doctor=Dr.%20Amit%20Verma")

    assert response.status_code == 200

    for patient in response.json()["items"]:
        assert patient["doctor"] == "Dr. Amit Verma"


def test_filter_by_status():
    response = client.get("/api/v1/patients/?status=Admitted")

    assert response.status_code == 200

    for patient in response.json()["items"]:
        assert patient["status"] == "Admitted"



def test_analytics():
    response = client.get("/api/v1/analytics/")

    assert response.status_code == 200
    assert "total_patients" in response.json()
    assert "admitted_patients" in response.json()
    assert "discharged_patients" in response.json()
def test_export_csv():
    response = client.get("/api/v1/exports/patients")

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment; filename=patients.csv" in response.headers["content-disposition"]

    content = response.text
    assert "id,name,age,gender,ward,department,doctor,admission_date,status" in content

