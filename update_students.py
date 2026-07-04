import os

filepath = "c:/Users/shahd/Downloads/ss/students.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add a Profile Modal HTML after the Student Modal
modal_marker = '<!-- Add/Edit Student Modal -->'
start_idx = content.find(modal_marker)
if start_idx == -1:
    print("Could not find modal marker")
    exit()

profile_modal_html = """<!-- Student Profile Modal -->
<div class="modal" id="profileModal">
    <div class="modal-content" style="max-width: 800px;">
        <div class="modal-header">
            <h3><i class="fas fa-id-card"></i> الملف الشخصي للطالب</h3>
            <button class="close-modal" id="closeProfileModal">&times;</button>
        </div>
        <div class="modal-body">
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <!-- Basic Info Card -->
                <div style="flex: 1; min-width: 300px; background: #f8f9fa; border-radius: 16px; padding: 20px; border: 1px solid #e9ecef;">
                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px; border-bottom: 2px solid #dee2e6; padding-bottom: 15px;">
                        <div style="width: 60px; height: 60px; background: var(--primary-blue); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                            <i class="fas fa-user-graduate"></i>
                        </div>
                        <div>
                            <h3 id="profName" style="color: var(--dark-blue); margin: 0; font-size: 20px;">-</h3>
                            <div style="color: var(--gray); font-size: 13px; margin-top: 4px;">كود: <strong id="profCode">-</strong></div>
                        </div>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 12px; font-size: 14px;">
                        <div><i class="fas fa-phone" style="color: var(--gray); width: 20px;"></i> الهاتف: <strong id="profPhone">-</strong></div>
                        <div><i class="fas fa-school" style="color: var(--gray); width: 20px;"></i> المدرسة/الجامعة: <strong id="profSchool">-</strong></div>
                        <div><i class="fas fa-birthday-cake" style="color: var(--gray); width: 20px;"></i> العمر: <strong id="profAge">-</strong></div>
                        <div><i class="fas fa-building" style="color: var(--gray); width: 20px;"></i> القسم: <strong id="profDept">-</strong></div>
                        <div><i class="fas fa-users" style="color: var(--gray); width: 20px;"></i> الجروب الحالي: <strong id="profGroup">-</strong></div>
                        <div><i class="fas fa-book" style="color: var(--gray); width: 20px;"></i> الكورس الحالي: <strong id="profCourse">-</strong></div>
                    </div>
                </div>

                <!-- Payments & Progress Card -->
                <div style="flex: 1; min-width: 300px; display: flex; flex-direction: column; gap: 20px;">
                    <div style="background: white; border-radius: 16px; padding: 20px; border: 1px solid #e9ecef; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                        <h4 style="color: var(--dark-blue); margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;"><i class="fas fa-history"></i> السجل المالي</h4>
                        <div style="max-height: 180px; overflow-y: auto;">
                            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                                <thead>
                                    <tr style="background: var(--light-gray); color: var(--dark);">
                                        <th style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">المستوى</th>
                                        <th style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">المبلغ المدفوع</th>
                                        <th style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">المتبقي</th>
                                        <th style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">التاريخ</th>
                                    </tr>
                                </thead>
                                <tbody id="profPaymentsBody">
                                    <!-- Populated via JS -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <div style="background: white; border-radius: 16px; padding: 20px; border: 1px solid #e9ecef; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                        <h4 style="color: var(--dark-blue); margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;"><i class="fas fa-plus-circle"></i> الإضافات المدفوعة (AddOns)</h4>
                        <ul id="profAddonsList" style="list-style: none; padding: 0; margin: 0; font-size: 13px; display: flex; flex-direction: column; gap: 8px;">
                            <!-- Populated via JS -->
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn-cancel" id="closeProfileBtn">إغلاق</button>
        </div>
    </div>
</div>
"""
content = content[:start_idx] + profile_modal_html + content[start_idx:]

# Update the render function to add the "View" button
old_render = """<button class="btn-icon btn-edit" onclick="editStudent(${s.id})"><i class="fas fa-edit"></i></button>
                            <button class="btn-icon btn-delete" onclick="deleteStudent(${s.id})"><i class="fas fa-trash"></i></button>"""
new_render = """<button class="btn-icon btn-view" onclick="viewProfile(${s.id})" title="عرض البروفايل"><i class="fas fa-eye"></i></button>
                            <button class="btn-icon btn-edit" onclick="editStudent(${s.id})" title="تعديل"><i class="fas fa-edit"></i></button>
                            <button class="btn-icon btn-delete" onclick="deleteStudent(${s.id})" title="حذف"><i class="fas fa-trash"></i></button>"""
content = content.replace(old_render, new_render)

# Add API call variables
js_vars_start = content.find('let allStudents = [];')
content = content[:js_vars_start] + 'let allPayments = [];\n    let allCourses = [];\n    let allAddOns = [];\n    ' + content[js_vars_start:]

# Update loadData to fetch payments, courses, addons
old_loadData = """allStudents = await apiCall('getAllStudents');
            groups = await apiCall('getAllGroups');"""
new_loadData = """const [sRes, gRes, pRes, cRes, aRes] = await Promise.all([
                apiCall('getAllStudents'),
                apiCall('getAllGroups'),
                apiCall('getAllPayments'),
                apiCall('getAllCourses'),
                apiCall('getAllAddOns')
            ]);
            allStudents = sRes || [];
            groups = gRes || [];
            allPayments = pRes || [];
            allCourses = cRes || [];
            allAddOns = aRes || [];"""
content = content.replace(old_loadData, new_loadData)

# Add Profile Logic JS
js_end = content.find('window.editStudent = editStudent;')
profile_js = """
    function viewProfile(id) {
        const student = allStudents.find(s => s.id == id);
        if (!student) return;
        
        // Basic Info
        document.getElementById('profName').textContent = student.name || '-';
        document.getElementById('profCode').textContent = student.code || '-';
        document.getElementById('profPhone').textContent = student.phone || '-';
        document.getElementById('profSchool').textContent = student.school || '-';
        document.getElementById('profAge').textContent = student.age || '-';
        
        const deptNames = {1: 'تقنية المعلومات (IT)', 2: 'اللغات (LANG)', 3: 'إدارة الأعمال (BUS)', 4: 'التصميم (GD)'};
        document.getElementById('profDept').textContent = deptNames[student.deptId] || '-';
        
        const group = groups.find(g => g.id == student.groupId);
        document.getElementById('profGroup').textContent = group ? group.name : 'بدون جروب';
        
        let courseName = '-';
        if (group && group.courseId) {
            const course = allCourses.find(c => c.id == group.courseId);
            if (course) courseName = course.name;
        }
        document.getElementById('profCourse').textContent = courseName;
        
        // Financial History
        const studentPayments = allPayments.filter(p => p.studentId == id);
        studentPayments.sort((a, b) => new Date(b.paymentDate) - new Date(a.paymentDate)); // Newest first
        
        const payBody = document.getElementById('profPaymentsBody');
        if (studentPayments.length > 0) {
            payBody.innerHTML = studentPayments.map(p => `
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">مستوى ${p.levelNumber || 1}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; color: var(--success); font-weight: bold;">${p.amountPaid || 0} ج.م</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; color: ${p.remainingBalance > 0 ? 'var(--danger)' : 'var(--success)'};">${p.remainingBalance || 0} ج.م</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">${p.paymentDate ? new Date(p.paymentDate).toLocaleDateString('ar-EG') : '-'}</td>
                </tr>
            `).join('');
        } else {
            payBody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 15px; color: var(--gray);">لا يوجد سجل مالي</td></tr>`;
        }
        
        // AddOns Logic
        // We will look at studentPayments to see which AddOns they bought.
        // Assuming addons are stored as comma separated IDs in p.addons? 
        // Let's aggregate all unique addons from all their payments.
        let paidAddonIds = new Set();
        studentPayments.forEach(p => {
            if (p.addonsPaid) {
                let ids = p.addonsPaid.split(',').map(aid => parseInt(aid.trim()));
                ids.forEach(aid => { if(!isNaN(aid)) paidAddonIds.add(aid); });
            }
        });
        
        const addList = document.getElementById('profAddonsList');
        if (paidAddonIds.size > 0) {
            addList.innerHTML = Array.from(paidAddonIds).map(aid => {
                const addon = allAddOns.find(a => a.id == aid);
                if (addon) {
                    return `<li><i class="fas fa-check-circle" style="color: var(--success); margin-left: 8px;"></i> ${addon.name} <span style="color: var(--gray); font-size: 11px;">(${addon.price} ج.م)</span></li>`;
                }
                return '';
            }).join('');
        } else {
            addList.innerHTML = `<li style="color: var(--gray); text-align: center;">لم يتم دفع إضافات</li>`;
        }
        
        document.getElementById('profileModal').classList.add('show');
    }
    
    document.getElementById('closeProfileModal').addEventListener('click', () => {
        document.getElementById('profileModal').classList.remove('show');
    });
    document.getElementById('closeProfileBtn').addEventListener('click', () => {
        document.getElementById('profileModal').classList.remove('show');
    });
    
    window.viewProfile = viewProfile;
"""
content = content[:js_end] + profile_js + content[js_end:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated students.html with Profile Modal")
