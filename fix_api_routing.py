import re

with open('code.gs', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix save handlers in code.gs
replacements = {
    "savePayment(params.data || params)": "savePayment(params.paymentData || params.data || params)",
    "saveBooking(params.data || params)": "saveBooking(params.bookingData || params.data || params)",
    "saveFloor(params.data || params)": "saveFloor(params.floorData || params.data || params)",
    "saveCourse(params.data || params)": "saveCourse(params.courseData || params.data || params)",
    "saveAddOn(params.data || params)": "saveAddOn(params.addonData || params.data || params)",
    "saveStudent(params.data || params)": "saveStudent(params.studentData || params.data || params)",
    "saveTrainer(params.data || params)": "saveTrainer(params.trainerData || params.data || params)",
    "saveDepartment(params.data || params)": "saveDepartment(params.deptData || params.data || params)",
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('code.gs', 'w', encoding='utf-8') as f:
    f.write(content)
