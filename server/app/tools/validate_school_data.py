
import json
from pathlib import Path


# ==========================================
# 1. LOAD JSON DATA
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

JSON_FILE = BASE_DIR / "data" / "school_saas_demo_seed.json"


def load_school_data():

    if not JSON_FILE.exists():
        raise FileNotFoundError(
            f"JSON file not found: {JSON_FILE}"
        )

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    print("JSON FILE LOADED SUCCESSFULLY")

    return data


# ==========================================
# 2. CHECK COLLECTION COUNTS
# ==========================================

def check_collection_counts(data):

    print("\n========== COLLECTION COUNTS ==========")

    for collection, records in data.items():

        if isinstance(records, list):
            print(f"{collection}: {len(records)} records")


# ==========================================
# 3. CHECK UNIQUE IDS
# ==========================================

def check_unique_ids(data):

    print("\n========== UNIQUE ID VALIDATION ==========")

    id_fields = {
        "organizations": "tenant_id",
        "branches": "branch_id",
        "students": "student_id",
        "employees": "employee_id",
        "classes": "class_id",
        "sections": "section_id",
        "subjects": "subject_id",
        "class_subjects": "class_subject_id",
        "class_assignments": "assignment_id",
        "fee_structures": "fee_structure_id",
        "fee_invoices": "invoice_id",
        "fee_payments": "payment_id",
        "attendance": "attendance_id",
        "vehicles": "vehicle_id",
        "transport_routes": "route_id",
        "transport_assignments": "transport_assignment_id"
    }

    for collection, id_field in id_fields.items():

        records = data.get(collection, [])

        ids = [
            record.get(id_field)
            for record in records
        ]

        if len(ids) != len(set(ids)):
            print(f"FAILED: Duplicate IDs in {collection}")
        else:
            print(f"PASSED: {collection}")


# ==========================================
# 4. CHECK RELATIONSHIPS
# ==========================================

def check_relationships(data):

    print("\n========== RELATIONSHIP VALIDATION ==========")

    errors = []

    def check_reference(
        collection,
        field,
        valid_ids,
        record_id
    ):

        value = record_id.get(field)

        if value is not None and value not in valid_ids:
            errors.append(
                f"{collection}: Invalid {field} = {value}"
            )

    organizations = {
        record["tenant_id"]
        for record in data["organizations"]
    }

    branches = {
        record["branch_id"]
        for record in data["branches"]
    }

    outlets = {
        record["outlet_id"]
        for record in data["branches"]
    }

    students = {
        record["student_id"]
        for record in data["students"]
    }

    employees = {
        record["employee_id"]
        for record in data["employees"]
    }

    classes = {
        record["class_id"]
        for record in data["classes"]
    }

    sections = {
        record["section_id"]
        for record in data["sections"]
    }

    subjects = {
        record["subject_id"]
        for record in data["subjects"]
    }

    fee_structures = {
        record["fee_structure_id"]
        for record in data["fee_structures"]
    }

    invoices = {
        record["invoice_id"]
        for record in data["fee_invoices"]
    }

    vehicles = {
        record["vehicle_id"]
        for record in data["vehicles"]
    }

    routes = {
        record["route_id"]
        for record in data["transport_routes"]
    }

    # Students
    for record in data["students"]:

        for field, valid_ids in [
            ("tenant_id", organizations),
            ("branch_id", branches),
            ("outlet_id", outlets),
            ("class_id", classes),
            ("section_id", sections)
        ]:
            check_reference("students", field, valid_ids, record)

    # Employees
    for record in data["employees"]:

        for field, valid_ids in [
            ("tenant_id", organizations),
            ("branch_id", branches),
            ("outlet_id", outlets)
        ]:
            check_reference("employees", field, valid_ids, record)

    # Sections
    for record in data["sections"]:

        check_reference("sections", "class_id", classes, record)

    # Class subjects
    for record in data["class_subjects"]:

        for field, valid_ids in [
            ("class_id", classes),
            ("subject_id", subjects),
            ("branch_id", branches),
            ("tenant_id", organizations),
            ("teacher_employee_id", employees)
        ]:
            check_reference("class_subjects", field, valid_ids, record)

    # Class assignments
    for record in data["class_assignments"]:

        for field, valid_ids in [
            ("class_id", classes),
            ("section_id", sections),
            ("class_incharge_employee_id", employees),
            ("branch_id", branches),
            ("tenant_id", organizations)
        ]:
            check_reference("class_assignments", field, valid_ids, record)

    # Fee invoices
    for record in data["fee_invoices"]:

        for field, valid_ids in [
            ("student_id", students),
            ("fee_structure_id", fee_structures),
            ("branch_id", branches),
            ("tenant_id", organizations)
        ]:
            check_reference("fee_invoices", field, valid_ids, record)

    # Fee payments
    for record in data["fee_payments"]:

        for field, valid_ids in [
            ("student_id", students),
            ("invoice_id", invoices),
            ("branch_id", branches),
            ("tenant_id", organizations)
        ]:
            check_reference("fee_payments", field, valid_ids, record)

    # Attendance
    for record in data["attendance"]:

        for field, valid_ids in [
            ("student_id", students),
            ("class_id", classes),
            ("section_id", sections),
            ("marked_by_employee_id", employees),
            ("branch_id", branches),
            ("tenant_id", organizations)
        ]:
            check_reference("attendance", field, valid_ids, record)

    # Transport routes
    for record in data["transport_routes"]:

        for field, valid_ids in [
            ("vehicle_id", vehicles),
            ("driver_employee_id", employees),
            ("helper_employee_id", employees),
            ("branch_id", branches),
            ("tenant_id", organizations)
        ]:
            check_reference("transport_routes", field, valid_ids, record)

    # Transport assignments
    for record in data["transport_assignments"]:

        for field, valid_ids in [
            ("student_id", students),
            ("route_id", routes),
            ("branch_id", branches),
            ("tenant_id", organizations)
        ]:
            check_reference("transport_assignments", field, valid_ids, record)

    if errors:

        print("\nRELATIONSHIP VALIDATION FAILED")

        for error in errors:
            print(error)

    else:

        print("ALL RELATIONSHIPS ARE VALID")

    return errors


# ==========================================
# 5. RUN VALIDATION
# ==========================================

def main():

    data = load_school_data()

    check_collection_counts(data)

    check_unique_ids(data)

    errors = check_relationships(data)

    print("\n========== FINAL RESULT ==========")

    if errors:
        print("DATA VALIDATION FAILED")
    else:
        print("DATA VALIDATION SUCCESSFUL")


if __name__ == "__main__":
    main()
