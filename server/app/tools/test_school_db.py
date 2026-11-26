
from app.tools.school_db import (
    search_students,
    get_student_attendance,
    get_student_fees,
    search_employees,
)
from app.tools.school_data import get_collection
from app.tools.school_db import get_student_transport_details
from app.tools.school_db import get_student_fee_payments


TENANT_ID = "TENANT_001"


# 1. Search student
print("\n========== STUDENT SEARCH ==========")

students = search_students(
    search_query="Aarav",
    tenant_id=TENANT_ID
)
for student in students:
    print(student)


# 2. Student attendance
if students:
    student_id = students[0]["student_id"]

    print("\n========== ATTENDANCE ==========")

    attendance = get_student_attendance(
        student_id=student_id,
        tenant_id=TENANT_ID
    )

    for record in attendance:
        print(record)


# 3. Student fees
if students:
    print("\n========== FEES ==========")

    fees = get_student_fees(
        student_id=student_id,
        tenant_id=TENANT_ID
    )

    for invoice in fees:
        print(invoice)


# 4. Employee search
# print("\n========== EMPLOYEE SEARCH ==========")

employees = search_employees(
    search_query="teacher",
    tenant_id=TENANT_ID
)

students = get_collection("students")


print("\n========== FEE PAYMENT HISTORY ==========")

payments = get_student_fee_payments(
    student_id="STU001",
    tenant_id=TENANT_ID
)

for payment in payments:
    print(payment)

if not payments:
    print("No payment records found.")