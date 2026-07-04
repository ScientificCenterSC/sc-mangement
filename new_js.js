function renderGroupedView() {
    const container = document.getElementById('groupedStudentsContent');
    if (!container) return;
    
    let html = '';
    allDepartments.forEach(dept => {
        html += <div class="dept-card" onclick="toggleDept('\')">
            <div class="dept-title"><i class="fas fa-building" style="color:var(--gold); margin-left:10px;"></i> \</div>
            <i class="fas fa-chevron-down"></i>
        </div>
        <div class="dept-details" id="dept-details-\">;
        
        const deptCourses = allCourses.filter(c => String(c.departmentId) === String(dept.id));
        if (deptCourses.length === 0) {
            html += <p style="text-align:center; color:var(--gray);">لا يوجد كورسات في هذا القسم</p>;
        } else {
            deptCourses.forEach(course => {
                html += <div class="course-card" onclick="toggleCourse('\')">
                    <div style="font-weight:600; color:var(--dark-blue);"><i class="fas fa-book" style="margin-left:8px;"></i>\</div>
                    <div id="course-details-\" style="display:none; margin-top:10px;">;
                
                const courseGroups = allGroups.filter(g => String(g.courseId) === String(course.id));
                if (courseGroups.length === 0) {
                    html += <p style="text-align:center; color:var(--gray); font-size:13px;">لا يوجد جروبات في هذا الكورس</p>;
                } else {
                    courseGroups.forEach(group => {
                        html += <div class="group-card">
                            <div style="display:flex; justify-content:space-between; align-items:center; cursor:pointer;" onclick="toggleGroup('\')">
                                <span style="font-weight:600;"><i class="fas fa-users" style="margin-left:5px;"></i>\</span>
                                <span><i class="fas fa-chevron-down" style="font-size:12px; color:var(--gray);"></i></span>
                            </div>
                            <div id="group-details-\" style="display:none;" class="group-students-list">
                                <button class="btn-primary" style="margin-bottom:10px; padding:6px 12px; font-size:13px;" onclick="addStudentToGroup('\', '\')">
                                    <i class="fas fa-plus"></i> إضافة طالب لهذا الجروب
                                </button>
                                <table class="data-table" style="width:100%; font-size:13px;">
                                    <thead><tr><th>الكود</th><th>الاسم</th><th>الهاتف</th><th>إجراءات</th></tr></thead>
                                    <tbody id="tbody-group-\">
                                    </tbody>
                                </table>
                            </div>
                        </div>;
                    });
                }
                html += </div></div>;
            });
        }
        html += </div>;
    });
    container.innerHTML = html;
}

window.toggleDept = function(id) {
    const el = document.getElementById('dept-details-' + id);
    if (el) el.style.display = el.style.display === 'none' || el.style.display === '' ? 'block' : 'none';
};
window.toggleCourse = function(id) {
    const el = document.getElementById('course-details-' + id);
    if (el) {
        event.stopPropagation();
        el.style.display = el.style.display === 'none' || el.style.display === '' ? 'block' : 'none';
    }
};
window.toggleGroup = function(id) {
    const el = document.getElementById('group-details-' + id);
    if (el) {
        event.stopPropagation();
        const isOpening = el.style.display === 'none' || el.style.display === '';
        el.style.display = isOpening ? 'block' : 'none';
        if (isOpening) {
            const tbody = document.getElementById('tbody-group-' + id);
            const groupStudents = allStudents.filter(s => String(s.groupId) === String(id));
            if (groupStudents.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:10px;">لا يوجد طلاب في هذا الجروب</td></tr>';
            } else {
                tbody.innerHTML = groupStudents.map(s => <tr>
                    <td>\</td>
                    <td>\</td>
                    <td>\</td>
                    <td><button onclick="editStudent('\')" style="border:none;background:none;color:var(--primary-blue);cursor:pointer;"><i class="fas fa-edit"></i></button></td>
                </tr>).join('');
            }
        }
    }
};

window.addStudentToGroup = function(deptId, groupId) {
    event.stopPropagation();
    openAddModal();
    setTimeout(() => {
        const deptSelect = document.getElementById('studentDept');
        const groupSelect = document.getElementById('studentGroup');
        if (deptSelect) {
            deptSelect.value = deptId;
            deptSelect.dispatchEvent(new Event('change'));
            setTimeout(() => {
                if (groupSelect) {
                    groupSelect.value = groupId;
                }
            }, 100);
        }
    }, 100);
};
