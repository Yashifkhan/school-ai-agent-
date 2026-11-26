
from app.tools.school_data import get_collection



def search_students(
    search_query: str,
    tenant_id: str,
    branch_id: str | None = None
) -> list[dict]:
    """
    Search students by name or student ID.
    """

    students = get_collection("students")

    query = search_query.strip().lower()

    if not query:
        return []

    results = []

    for student in students:

        if student.get("tenant_id") != tenant_id:
            continue

        if branch_id and student.get("branch_id") != branch_id:
            continue

        # Read student name fields
        full_name = str(student.get("full_name", "")).lower()
        first_name = str(student.get("first_name", "")).lower()
        last_name = str(student.get("last_name", "")).lower()

        student_id = str(student.get("student_id", "")).lower()

        if (
            query in full_name
            or query in first_name
            or query in last_name
            or query in student_id
        ):
            results.append(student)

    return results


def get_student_by_id(
    student_id: str,
    tenant_id: str,
    branch_id: str | None = None
) -> dict | None:
    """
    Find one student using student ID.
    """

    students = get_collection("students")

    for student in students:

        if student.get("tenant_id") != tenant_id:
            continue

        if branch_id and student.get("branch_id") != branch_id:
            continue

        if student.get("student_id") == student_id:
            return student

    return None


def get_student_attendance(
    student_id: str,
    tenant_id: str,
    branch_id: str | None = None
) -> list[dict]:
    """
    Get attendance records for a student.
    """

    attendance_records = get_collection("attendance")

    results = []

    for record in attendance_records:

        if record.get("tenant_id") != tenant_id:
            continue

        if branch_id and record.get("branch_id") != branch_id:
            continue

        if record.get("student_id") == student_id:
            results.append(record)

    return results


def get_student_fees(
    student_id: str,
    tenant_id: str,
    branch_id: str | None = None
) -> list[dict]:
    """
    Get fee invoices for a student.
    """

    invoices = get_collection("fee_invoices")

    results = []

    for invoice in invoices:

        if invoice.get("tenant_id") != tenant_id:
            continue

        if branch_id and invoice.get("branch_id") != branch_id:
            continue

        if invoice.get("student_id") == student_id:
            results.append(invoice)

    return results


def get_student_fee_payments(
    student_id: str,
    tenant_id: str,
    branch_id: str | None = None
) -> list[dict]:
    """
    Get fee payment records for a student.
    """

    payments = get_collection("fee_payments")

    results = []

    for payment in payments:

        if payment.get("tenant_id") != tenant_id:
            continue

        if branch_id and payment.get("branch_id") != branch_id:
            continue

        if payment.get("student_id") == student_id:
            results.append(payment)

    return results


def search_employees(
    search_query: str,
    tenant_id: str,
    branch_id: str | None = None
) -> list[dict]:
    """
    Search employees by name, ID, or role.
    """

    employees = get_collection("employees")

    query = search_query.strip().lower()

    if not query:
        return []

    results = []

    for employee in employees:

        if employee.get("tenant_id") != tenant_id:
            continue

        if branch_id and employee.get("branch_id") != branch_id:
            continue

        name = str(employee.get("name", "")).lower()
        employee_id = str(employee.get("employee_id", "")).lower()

        roles = employee.get("roles", [])
        role_text = " ".join(str(role).lower() for role in roles)

        if (
            query in name
            or query in employee_id
            or query in role_text
        ):
            results.append(employee)

    return results


def get_student_transport(
    student_id: str,
    tenant_id: str,
    branch_id: str | None = None
) -> list[dict]:
    """
    Get transport assignments for a student.
    """

    assignments = get_collection("transport_assignments")

    results = []

    for assignment in assignments:

        if assignment.get("tenant_id") != tenant_id:
            continue

        if branch_id and assignment.get("branch_id") != branch_id:
            continue

        if assignment.get("student_id") == student_id:
            results.append(assignment)

    return results




def get_student_transport_details(
    student_id: str,
    tenant_id: str,
    branch_id: str | None = None
) -> list[dict]:
    """
    Get complete transport details for a student.
    """

    # Step 1: Find student's transport assignments
    assignments = get_collection("transport_assignments")

    # Step 2: Load routes, vehicles and employees
    routes = get_collection("transport_routes")
    vehicles = get_collection("vehicles")
    employees = get_collection("employees")

    results = []

    for assignment in assignments:

        if assignment.get("tenant_id") != tenant_id:
            continue

        if branch_id and assignment.get("branch_id") != branch_id:
            continue

        if assignment.get("student_id") != student_id:
            continue

        route_id = assignment.get("route_id")

        # Step 3: Find assigned route
        route = next(
            (
                item for item in routes
                if item.get("route_id") == route_id
                and item.get("tenant_id") == tenant_id
                and item.get("branch_id") == assignment.get("branch_id")
            ),
            None
        )

        if not route:
            continue

        # Step 4: Find vehicle
        vehicle_id = route.get("vehicle_id")

        vehicle = next(
            (
                item for item in vehicles
                if item.get("vehicle_id") == vehicle_id
                and item.get("tenant_id") == tenant_id
                and item.get("branch_id") == assignment.get("branch_id")
            ),
            None
        )

        # Step 5: Find driver
        driver_id = route.get("driver_employee_id")

        driver = next(
            (
                item for item in employees
                if item.get("employee_id") == driver_id
                and item.get("tenant_id") == tenant_id
                and item.get("branch_id") == assignment.get("branch_id")
            ),
            None
        )

        # Step 6: Find helper
        helper_id = route.get("helper_employee_id")

        helper = next(
            (
                item for item in employees
                if item.get("employee_id") == helper_id
                and item.get("tenant_id") == tenant_id
                and item.get("branch_id") == assignment.get("branch_id")
            ),
            None
        )

        results.append({
            "assignment": assignment,
            "route": route,
            "vehicle": vehicle,
            "driver": driver,
            "helper": helper
        })

    return results

