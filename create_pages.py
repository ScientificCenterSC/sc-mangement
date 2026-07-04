import os
import re

directory = "c:/Users/shahd/Downloads/ss"
template_file = os.path.join(directory, "settings.html")

with open(template_file, 'r', encoding='utf-8') as f:
    template = f.read()

# Make departments.html
dept = template.replace('Scientific Center | الإعدادات', 'Scientific Center | الأقسام')
dept = dept.replace('إدارة المستخدمين', 'إدارة الأقسام')
dept = dept.replace('إضافة، تعديل، بحث وحذف المستخدمين', 'إضافة وتعديل الأقسام')
dept = dept.replace('إضافة مستخدم جديد', 'إضافة قسم جديد')
dept = dept.replace('usersTableBody', 'departmentsTableBody')
dept = dept.replace('users-table', 'departments-table')
dept = dept.replace('userModal', 'departmentModal')
dept = dept.replace('userForm', 'departmentForm')
dept = dept.replace('saveuser', 'saveDepartment')
dept = dept.replace('adduserBtn', 'addDepartmentBtn')
dept = dept.replace('allusers', 'allDepartments')
dept = dept.replace('getAllUsers', 'getAllDepartments')
dept = dept.replace('saveUser', 'saveDepartment')
dept = dept.replace('deleteUser', 'deleteDepartment')

with open(os.path.join(directory, "departments.html"), 'w', encoding='utf-8') as f:
    f.write(dept)

# Make floors.html
floors = template.replace('Scientific Center | الإعدادات', 'Scientific Center | الأدوار')
floors = floors.replace('إدارة المستخدمين', 'إدارة الأدوار والقاعات')
floors = floors.replace('إضافة، تعديل، بحث وحذف المستخدمين', 'إضافة وتعديل الأدوار')
floors = floors.replace('إضافة مستخدم جديد', 'إضافة دور جديد')
floors = floors.replace('usersTableBody', 'floorsTableBody')
floors = floors.replace('users-table', 'floors-table')
floors = floors.replace('userModal', 'floorModal')
floors = floors.replace('userForm', 'floorForm')
floors = floors.replace('saveuser', 'saveFloor')
floors = floors.replace('adduserBtn', 'addFloorBtn')
floors = floors.replace('allusers', 'allFloors')
floors = floors.replace('getAllUsers', 'getAllFloors')
floors = floors.replace('saveUser', 'saveFloor')
floors = floors.replace('deleteUser', 'deleteFloor')

with open(os.path.join(directory, "floors.html"), 'w', encoding='utf-8') as f:
    f.write(floors)

# Make courses.html
courses = template.replace('Scientific Center | الإعدادات', 'Scientific Center | الكورسات')
courses = courses.replace('إدارة المستخدمين', 'إدارة الكورسات والإضافات')
courses = courses.replace('إضافة، تعديل، بحث وحذف المستخدمين', 'إضافة وتعديل الكورسات')
courses = courses.replace('إضافة مستخدم جديد', 'إضافة كورس جديد')
courses = courses.replace('usersTableBody', 'coursesTableBody')
courses = courses.replace('users-table', 'courses-table')
courses = courses.replace('userModal', 'courseModal')
courses = courses.replace('userForm', 'courseForm')
courses = courses.replace('saveuser', 'saveCourse')
courses = courses.replace('adduserBtn', 'addCourseBtn')
courses = courses.replace('allusers', 'allCourses')
courses = courses.replace('getAllUsers', 'getAllCourses')
courses = courses.replace('saveUser', 'saveCourse')
courses = courses.replace('deleteUser', 'deleteCourse')

with open(os.path.join(directory, "courses.html"), 'w', encoding='utf-8') as f:
    f.write(courses)

# Make roles.html
roles = template.replace('Scientific Center | الإعدادات', 'Scientific Center | الصلاحيات')
roles = roles.replace('إدارة المستخدمين', 'إدارة الصلاحيات')
roles = roles.replace('إضافة، تعديل، بحث وحذف المستخدمين', 'إضافة وتعديل الصلاحيات')
roles = roles.replace('إضافة مستخدم جديد', 'إضافة صلاحية جديدة')
roles = roles.replace('usersTableBody', 'rolesTableBody')
roles = roles.replace('users-table', 'roles-table')
roles = roles.replace('userModal', 'roleModal')
roles = roles.replace('userForm', 'roleForm')
roles = roles.replace('saveuser', 'saveRole')
roles = roles.replace('adduserBtn', 'addRoleBtn')
roles = roles.replace('allusers', 'allRoles')
roles = roles.replace('getAllUsers', 'getAllRoles')
roles = roles.replace('saveUser', 'saveRole')
roles = roles.replace('deleteUser', 'deleteRole')

with open(os.path.join(directory, "roles.html"), 'w', encoding='utf-8') as f:
    f.write(roles)

print("Created all pages.")
