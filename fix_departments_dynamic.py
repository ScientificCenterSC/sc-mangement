import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

# We'll do custom replacements per file because they have different IDs.

# 1. students.html
if 'students.html' in html_files:
    with open('students.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove hardcoded options in filters
    content = re.sub(
        r'<select id="deptFilter">.*?<\/select>',
        '<select id="deptFilter"><option value="all">الكل</option></select>',
        content, flags=re.DOTALL
    )
    
    # Remove hardcoded options in forms
    content = re.sub(
        r'<select id="stDept" required>.*?<\/select>',
        '<select id="stDept" required><option value="">اختر القسم...</option></select>',
        content, flags=re.DOTALL
    )
    
    # Add getAllDepartments to loadData
    if "apiCall('getAllDepartments')" not in content:
        content = content.replace(
            "apiCall('getAllAddOns')",
            "apiCall('getAllAddOns'),\n                apiCall('getAllDepartments')"
        ).replace(
            "const [sRes, gRes, pRes, cRes, aRes]",
            "const [sRes, gRes, pRes, cRes, aRes, dRes]"
        ).replace(
            "allAddOns = aRes || [];",
            "allAddOns = aRes || [];\n            allDepartments = dRes || [];\n            updateDepartmentDropdowns();"
        )
    
    # Add updateDepartmentDropdowns and allDepartments var
    if "let allDepartments = [];" not in content:
        content = content.replace(
            "let allStudents = [];",
            "let allStudents = [];\n    let allDepartments = [];"
        )
        dept_fn = """
    function updateDepartmentDropdowns() {
        const deptFilter = document.getElementById('deptFilter');
        const stDept = document.getElementById('stDept');
        
        let optionsFilter = '<option value="all">الكل</option>';
        let optionsForm = '<option value="">اختر القسم...</option>';
        
        if (typeof allDepartments !== 'undefined') {
            allDepartments.forEach(d => {
                optionsFilter += `<option value="${d.id}">${d.name}</option>`;
                optionsForm += `<option value="${d.id}">${d.name}</option>`;
            });
        }
        
        if (deptFilter) deptFilter.innerHTML = optionsFilter;
        if (stDept) stDept.innerHTML = optionsForm;
    }
"""
        content = content.replace("function updateGroupFilters() {", dept_fn + "\n    function updateGroupFilters() {")
    
    # Render table dynamic dept
    content = re.sub(
        r"const deptNames = \{[^\}]+\};\s*const deptName = deptNames\[[a-zA-Z0-9_.]*\] \|\| '\-';",
        "const dept = allDepartments.find(d => d.id == s.deptId);\n            const deptName = dept ? dept.name : '-';",
        content
    )
    
    with open('students.html', 'w', encoding='utf-8') as f:
        f.write(content)

# 2. courses.html
if 'courses.html' in html_files:
    with open('courses.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(
        r'<select id="deptFilter">.*?<\/select>',
        '<select id="deptFilter"><option value="all">الكل</option></select>',
        content, flags=re.DOTALL
    )
    content = re.sub(
        r'<select id="courseDept" required>.*?<\/select>',
        '<select id="courseDept" required><option value="">اختر القسم...</option></select>',
        content, flags=re.DOTALL
    )
    if "apiCall('getAllDepartments')" not in content:
        content = content.replace(
            "apiCall('getAllGroups')",
            "apiCall('getAllGroups'),\n                apiCall('getAllDepartments')"
        ).replace(
            "const [cRes, gRes]",
            "const [cRes, gRes, dRes]"
        ).replace(
            "groups = gRes || [];",
            "groups = gRes || [];\n            allDepartments = dRes || [];\n            updateDepartmentDropdowns();"
        )
    if "let allDepartments = [];" not in content:
        content = content.replace(
            "let allCourses = [];",
            "let allCourses = [];\n    let allDepartments = [];"
        )
        dept_fn = """
    function updateDepartmentDropdowns() {
        const deptFilter = document.getElementById('deptFilter');
        const courseDept = document.getElementById('courseDept');
        let optionsFilter = '<option value="all">الكل</option>';
        let optionsForm = '<option value="">اختر القسم...</option>';
        if (typeof allDepartments !== 'undefined') {
            allDepartments.forEach(d => {
                optionsFilter += `<option value="${d.id}">${d.name}</option>`;
                optionsForm += `<option value="${d.id}">${d.name}</option>`;
            });
        }
        if (deptFilter) deptFilter.innerHTML = optionsFilter;
        if (courseDept) courseDept.innerHTML = optionsForm;
    }
"""
        content = content.replace("function updateGroupFilters() {", dept_fn + "\n    function updateGroupFilters() {")
        content = content.replace("function filterAndRender() {", dept_fn + "\n    function filterAndRender() {") # fallback

    content = re.sub(
        r"const deptNames = \{[^\}]+\};\s*const deptName = deptNames\[[a-zA-Z0-9_.]*\] \|\| '\-';",
        "const dept = allDepartments.find(d => d.id == c.deptId);\n            const deptName = dept ? dept.name : '-';",
        content
    )
    with open('courses.html', 'w', encoding='utf-8') as f:
        f.write(content)

# 3. schedule.html
if 'schedule.html' in html_files:
    with open('schedule.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Wait, schedule.html filter
    # Actually, schedule.html needs multiple changes including multi-day, filters etc.
    # I will handle schedule.html separately with its own script since it has a lot of rewrites.
    pass

# 4. reports.html
if 'reports.html' in html_files:
    with open('reports.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(
        r'<select id="deptFilter">.*?<\/select>',
        '<select id="deptFilter"><option value="all">جميع الأقسام</option></select>',
        content, flags=re.DOTALL
    )
    
    if "apiCall('getAllDepartments')" not in content:
        content = content.replace(
            "apiCall('getAllHalls')",
            "apiCall('getAllHalls'),\n                apiCall('getAllDepartments')"
        ).replace(
            "const [sRes, tRes, pRes, cRes, gRes, hRes]",
            "const [sRes, tRes, pRes, cRes, gRes, hRes, dRes]"
        ).replace(
            "halls = hRes || [];",
            "halls = hRes || [];\n            allDepartments = dRes || [];\n            updateDepartmentDropdowns();"
        )
    if "let allDepartments = [];" not in content:
        content = content.replace(
            "let students = [];",
            "let students = [];\n    let allDepartments = [];"
        )
        dept_fn = """
    function updateDepartmentDropdowns() {
        const deptFilter = document.getElementById('deptFilter');
        if (!deptFilter) return;
        let options = '<option value="all">جميع الأقسام</option>';
        if (typeof allDepartments !== 'undefined') {
            allDepartments.forEach(d => {
                options += `<option value="${d.id}">${d.name}</option>`;
            });
        }
        deptFilter.innerHTML = options;
    }
"""
        content = content.replace("function updateFilters() {", dept_fn + "\n    function updateFilters() {")

    with open('reports.html', 'w', encoding='utf-8') as f:
        f.write(content)

# 5. trainers.html
if 'trainers.html' in html_files:
    with open('trainers.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(
        r'<select id="deptFilter">.*?<\/select>',
        '<select id="deptFilter"><option value="all">الكل</option></select>',
        content, flags=re.DOTALL
    )
    content = re.sub(
        r'<select id="trainerDept" required>.*?<\/select>',
        '<select id="trainerDept" required><option value="">اختر القسم...</option></select>',
        content, flags=re.DOTALL
    )
    
    if "apiCall('getAllDepartments')" not in content:
        content = content.replace(
            "apiCall('getAllTrainers')",
            "apiCall('getAllTrainers'),\n                apiCall('getAllDepartments')"
        ).replace(
            "const [tRes]",
            "const [tRes, dRes]"
        ).replace(
            "allTrainers = tRes || [];",
            "allTrainers = tRes || [];\n            allDepartments = dRes || [];\n            updateDepartmentDropdowns();"
        )
    if "let allDepartments = [];" not in content:
        content = content.replace(
            "let allTrainers = [];",
            "let allTrainers = [];\n    let allDepartments = [];"
        )
        dept_fn = """
    function updateDepartmentDropdowns() {
        const deptFilter = document.getElementById('deptFilter');
        const trainerDept = document.getElementById('trainerDept');
        let optionsFilter = '<option value="all">الكل</option>';
        let optionsForm = '<option value="">اختر القسم...</option>';
        if (typeof allDepartments !== 'undefined') {
            allDepartments.forEach(d => {
                optionsFilter += `<option value="${d.id}">${d.name}</option>`;
                optionsForm += `<option value="${d.id}">${d.name}</option>`;
            });
        }
        if (deptFilter) deptFilter.innerHTML = optionsFilter;
        if (trainerDept) trainerDept.innerHTML = optionsForm;
    }
"""
        content = content.replace("function filterAndRender() {", dept_fn + "\n    function filterAndRender() {")

    content = re.sub(
        r"const deptNames = \{[^\}]+\};\s*const deptName = deptNames\[[a-zA-Z0-9_.]*\] \|\| '\-';",
        "const dept = allDepartments.find(d => d.id == t.deptId);\n            const deptName = dept ? dept.name : '-';",
        content
    )
    with open('trainers.html', 'w', encoding='utf-8') as f:
        f.write(content)

print("Done updating dynamic departments!")
