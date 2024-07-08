from .models import Department, DepartmentUser


def assign_employee_to_dept(employee, department_id, is_head):

    department = Department.objects.get(department_id=department_id)
    department_user = DepartmentUser.objects.create(
        department=department,
        employee=employee,
        is_head=is_head,
    )
    DepartmentUser.objects.filter(
        employee=department_user.employee, is_current=True
    ).exclude(pk=department_user.pk).update(is_current=False)
    return department_user
