import os
import re

filepath = "c:/Users/shahd/Downloads/ss/courses.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix table headers
old_th = """                            <th>ID</th>
                            <th>الاسم الكامل</th>
                            <th>اسم المستخدم</th>
                            <th>الهاتف</th>
                            <th>الصلاحية</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>"""
new_th = """                            <th>ID</th>
                            <th>اسم الكورس</th>
                            <th>القسم</th>
                            <th>سعر المستوى (ج.م)</th>
                            <th>عدد المستويات</th>
                            <th>الإجراءات</th>"""
content = content.replace(old_th, new_th)

# Fix empty state
content = content.replace('<td colspan="7" style="text-align: center;">جاري التحميل...</td>', '<td colspan="6" style="text-align: center;">جاري التحميل...</td>')
content = content.replace('<td colspan="7" style="text-align: center;">لا يوجد مستخدمين</td>', '<td colspan="6" style="text-align: center;">لا توجد كورسات</td>')

# Fix Modal Form
old_form = """                <div class="form-row">
                    <div class="form-group">
                        <label>الاسم الكامل *</label>
                        <input type="text" id="userFullName" required placeholder="أدخل الاسم الكامل">
                    </div>
                    <div class="form-group">
                        <label>اسم المستخدم (للدخول) *</label>
                        <input type="text" id="userNameInput" required placeholder="أدخل اسم المستخدم">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>كلمة المرور *</label>
                        <input type="password" id="userPassword" placeholder="أدخل كلمة المرور">
                    </div>
                    <div class="form-group">
                        <label>رقم الهاتف</label>
                        <input type="tel" id="userPhone" placeholder="أدخل رقم الهاتف">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>الصلاحية *</label>
                        <select id="userRoleSelect" required>
                            <option value="">اختر الصلاحية</option>
                            <option value="1">مدير النظام (Admin)</option>
                            <option value="2">محاسب (Accountant)</option>
                            <option value="3">مدير دور (Floor Manager)</option>
                            <option value="4">مسؤول حجوزات (Booking)</option>
                            <option value="5">مشاهد (Viewer)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>الحالة</label>
                        <select id="userStatus">
                            <option value="true">نشط</option>
                            <option value="false">غير نشط</option>
                        </select>
                    </div>
                </div>"""
new_form = """                <div class="form-row">
                    <div class="form-group">
                        <label>اسم الكورس *</label>
                        <input type="text" id="courseName" required placeholder="أدخل اسم الكورس">
                    </div>
                    <div class="form-group">
                        <label>القسم</label>
                        <select id="courseDeptId"></select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>سعر المستوى الواحد (ج.م) *</label>
                        <input type="number" id="coursePrice" required min="0" placeholder="0.0">
                    </div>
                    <div class="form-group">
                        <label>إجمالي المستويات *</label>
                        <input type="number" id="courseLevels" required min="1" value="1">
                    </div>
                </div>"""
content = content.replace(old_form, new_form)

# Filter
old_filter = """        if (searchTerm) {
            filtered = filtered.filter(s => 
                (s.fullName && s.fullName.toLowerCase().includes(searchTerm)) ||
                (s.username && s.username.toLowerCase().includes(searchTerm)) ||
                (s.phone && s.phone.includes(searchTerm))
            );
        }"""
new_filter = """        if (searchTerm) {
            filtered = filtered.filter(s => 
                (s.name && s.name.toLowerCase().includes(searchTerm)) ||
                (s.deptName && s.deptName.toLowerCase().includes(searchTerm))
            );
        }"""
content = content.replace(old_filter, new_filter)

# Render Rows
old_rows = """        // Render rows
        tbody.innerHTML = paginated.map(s => {
            const roleNames = {1: 'مدير النظام', 2: 'محاسب', 3: 'مدير دور', 4: 'مسؤول حجوزات', 5: 'مشاهد'};
            const roleName = roleNames[s.roleId] || 'مستخدم';
            
            return `
                <tr>
                    <td><strong>${s.id || '-'}</strong></td>
                    <td>${s.fullName || '-'}</td>
                    <td>${s.username || '-'}</td>
                    <td>${s.phone || '-'}</td>
                    <td>${roleName}</td>
                    <td><span class="status-badge status-${s.isActive ? 'active' : 'inactive'}">${s.isActive ? 'نشط' : 'غير نشط'}</span></td>
                    <td class="action-buttons">
                        <button class="btn-icon btn-edit" onclick="edituser(${s.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon btn-delete" onclick="deleteuser(${s.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        }).join('');"""
new_rows = """        // Render rows
        tbody.innerHTML = paginated.map(s => {
            return `
                <tr>
                    <td><strong>${s.id || '-'}</strong></td>
                    <td>${s.name || '-'}</td>
                    <td>${s.deptName || '-'}</td>
                    <td>${s.pricePerLevel || 0} ج.م</td>
                    <td>${s.durationLevels || 1}</td>
                    <td class="action-buttons">
                        <button class="btn-icon btn-edit" onclick="editCourse(${s.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon btn-delete" onclick="deleteCourse(${s.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        }).join('');"""
content = content.replace(old_rows, new_rows)

# Edit modal
old_edit = """            document.getElementById('modalTitle').textContent = 'تعديل بيانات المستخدم';
            document.getElementById('userId').value = user.id;
            document.getElementById('userFullName').value = user.fullName || '';
            document.getElementById('userNameInput').value = user.username || '';
            document.getElementById('userPassword').value = user.password || '';
            document.getElementById('userPhone').value = user.phone || '';
            document.getElementById('userRoleSelect').value = user.roleId || '';
            document.getElementById('userStatus').value = user.isActive ? 'true' : 'false';"""
new_edit = """            document.getElementById('modalTitle').textContent = 'تعديل الكورس';
            document.getElementById('userId').value = user.id;
            document.getElementById('courseName').value = user.name || '';
            document.getElementById('courseDeptId').value = user.deptId || '';
            document.getElementById('coursePrice').value = user.pricePerLevel || 0;
            document.getElementById('courseLevels').value = user.durationLevels || 1;"""
content = content.replace(old_edit, new_edit)

# Save modal
old_save = """        const rules = {
            userFullName: [{ fn: Validators.required, msg: 'الاسم مطلوب' }],
            userNameInput: [{ fn: Validators.required, msg: 'اسم المستخدم مطلوب' }],
            userRoleSelect: [{ fn: Validators.required, msg: 'الصلاحية مطلوبة' }]
        };
        
        if (!validateForm(rules)) return;
        
        const userData = {
            id: document.getElementById('userId').value || null,
            fullName: document.getElementById('userFullName').value,
            username: document.getElementById('userNameInput').value,
            password: document.getElementById('userPassword').value,
            phone: document.getElementById('userPhone').value,
            roleId: parseInt(document.getElementById('userRoleSelect').value, 10),
            isActive: document.getElementById('userStatus').value === 'true'
        };"""
new_save = """        const rules = {
            courseName: [{ fn: Validators.required, msg: 'الاسم مطلوب' }],
            coursePrice: [{ fn: Validators.required, msg: 'السعر مطلوب' }]
        };
        
        if (!validateForm(rules)) return;
        
        const userData = {
            id: document.getElementById('userId').value || null,
            name: document.getElementById('courseName').value,
            deptId: document.getElementById('courseDeptId').value,
            pricePerLevel: document.getElementById('coursePrice').value,
            durationLevels: document.getElementById('courseLevels').value
        };"""
content = content.replace(old_save, new_save)
content = content.replace('تم حفظ بيانات المستخدم بنجاح', 'تم الحفظ بنجاح')
content = content.replace('تم حذف المستخدم بنجاح', 'تم الحذف بنجاح')
content = content.replace('هل أنت متأكد من حذف هذا المستخدم؟', 'هل أنت متأكد من حذف هذا الكورس؟')

content = content.replace('viewuser', 'viewCourse')
content = content.replace('edituser', 'editCourse')
content = content.replace('deleteuser', 'deleteCourse')

# Add dept loading
old_load = """            allCourses = await apiCall('getAllCourses');
            filterAndRender();"""
new_load = """            const [coursesRes, deptsRes] = await Promise.all([
                apiCall('getAllCourses'),
                apiCall('getAllDepartments')
            ]);
            
            // Populate select
            const deptSelect = document.getElementById('courseDeptId');
            deptSelect.innerHTML = '<option value="">بدون قسم</option>' + 
                (deptsRes || []).map(d => `<option value="${d.id}">${d.name}</option>`).join('');
                
            // Map deptName to courses
            allCourses = coursesRes.map(c => {
                const dept = deptsRes.find(d => d.id == c.deptId);
                return { ...c, deptName: dept ? dept.name : '-' };
            });
            
            filterAndRender();"""
content = content.replace(old_load, new_load)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated courses.html")
