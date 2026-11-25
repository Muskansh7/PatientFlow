from app.repositories.patient_repository import patient_repository


class AnalyticsService:

    def get_dashboard_stats(self):
        patients = patient_repository.get_all_records()

        total = len(patients)

        admitted = sum(
            1 for p in patients
            if p["status"] == "Admitted"
        )

        discharged = sum(
            1 for p in patients
            if p["status"] == "Discharged"
        )

        ward_stats = {}
        department_stats = {}

        for p in patients:
            ward = p["ward"]
            department = p["department"]

            ward_stats.setdefault(ward, {
                "total": 0,
                "admitted": 0,
                "discharged": 0
            })

            department_stats.setdefault(department, 0)

            ward_stats[ward]["total"] += 1
            department_stats[department] += 1

            if p["status"] == "Admitted":
                ward_stats[ward]["admitted"] += 1

            elif p["status"] == "Discharged":
                ward_stats[ward]["discharged"] += 1

        return {
            "total_patients": total,
            "admitted_patients": admitted,
            "discharged_patients": discharged,
            "ward_statistics": ward_stats,
            "department_statistics": department_stats
        }


analytics_service = AnalyticsService()