import os

filepath = "c:/Users/shahd/Downloads/ss/courses.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add tabs and AddOns table to HTML
start_idx = content.find('<div class="content-area">')
end_idx = content.find('<!-- Add/Edit user Modal -->')

new_html = """<div class="content-area">
            <!-- Tabs -->
            <div class="report-tabs" style="display: flex; gap: 10px; margin-bottom: 20px; background: white; padding: 10px; border-radius: 16px;">
                <button class="tab-btn active" id="tabCourses" style="padding: 10px 20px; border: none; background: var(--primary-blue); color: white; border-radius: 10px; cursor: pointer; font-weight: bold;"><i class="fas fa-book"></i> الكورسات</button>
                <button class="tab-btn" id="tabAddOns" style="padding: 10px 20px; border: none; background: transparent; color: var(--dark); border-radius: 10px; cursor: pointer; font-weight: bold;"><i class="fas fa-plus-circle"></i> الإضافات (AddOns)</button>
            </div>

            <!-- Toolbar -->
            <div class="toolbar">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="بحث...">
                    <button id="searchBtn"><i class="fas fa-search"></i> بحث</button>
                </div>
                <button class="btn-add" id="addBtn">
                    <i class="fas fa-plus"></i>
                    <span id="addBtnText">إضافة كورس جديد</span>
                </button>
            </div>

            <!-- Courses Table -->
            <div class="users-table-container" id="coursesSection">
                <table class="users-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>اسم الكورس</th>
                            <th>القسم</th>
                            <th>سعر المستوى (ج.م)</th>
                            <th>عدد المستويات</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="coursesTableBody">
                        <tr><td colspan="6" style="text-align: center;">جاري التحميل...</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- AddOns Table -->
            <div class="users-table-container" id="addonsSection" style="display: none;">
                <table class="users-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>اسم الإضافة</th>
                            <th>سعر الإضافة (ج.م)</th>
                            <th>الكورس المرتبط</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="addonsTableBody">
                        <tr><td colspan="5" style="text-align: center;">جاري التحميل...</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div class="pagination" id="pagination"></div>
        </div>
    </main>
</div>
"""
content = content[:start_idx] + new_html + content[end_idx:]

# Update Modals (Need Course Modal and AddOn Modal)
modal_start_idx = content.find('<!-- Add/Edit user Modal -->')
modal_end_idx = content.find('<script>')

new_modals = """<!-- Course Modal -->
<div class="modal" id="courseModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3 id="courseModalTitle">إضافة كورس جديد</h3>
            <button class="close-modal" id="closeCourseModal">&times;</button>
        </div>
        <div class="modal-body">
            <form id="courseForm">
                <input type="hidden" id="courseId" value="">
                <div class="form-row">
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
                </div>
            </form>
        </div>
        <div class="modal-footer">
            <button class="btn-cancel" id="cancelCourseModal">إلغاء</button>
            <button class="btn-save" id="saveCourseBtn">حفظ</button>
        </div>
    </div>
</div>

<!-- AddOn Modal -->
<div class="modal" id="addonModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3 id="addonModalTitle">إضافة ملحق/إضافة جديدة</h3>
            <button class="close-modal" id="closeAddonModal">&times;</button>
        </div>
        <div class="modal-body">
            <form id="addonForm">
                <input type="hidden" id="addonId" value="">
                <div class="form-group">
                    <label>اسم الإضافة (مثال: مذكرات، رسوم شهادة) *</label>
                    <input type="text" id="addonName" required placeholder="أدخل اسم الإضافة">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>السعر (ج.م) *</label>
                        <input type="number" id="addonPrice" required min="0" placeholder="0.0">
                    </div>
                    <div class="form-group">
                        <label>مرتبط بكورس معين؟ (اختياري)</label>
                        <select id="addonCourseId">
                            <option value="">عام (يظهر لكل الكورسات)</option>
                        </select>
                    </div>
                </div>
            </form>
        </div>
        <div class="modal-footer">
            <button class="btn-cancel" id="cancelAddonModal">إلغاء</button>
            <button class="btn-save" id="saveAddonBtn">حفظ</button>
        </div>
    </div>
</div>
"""
content = content[:modal_start_idx] + new_modals + content[modal_end_idx:]

# JS Rewrite
js_start = content.find('<script>') + 8
js_end = content.find('</script>', js_start)

new_js = """
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';
    
    let currentUser = null;
    let allCourses = [];
    let allDepts = [];
    let allAddOns = [];
    let currentPage = 1;
    const rowsPerPage = 10;
    let currentTab = 'courses';
    
    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    async function apiCall(action, data = {}) {
        try {
            const response = await fetch(SCRIPT_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                body: JSON.stringify({ action, ...data })
            });
            const result = await response.json();
            if (result.success === false) throw new Error(result.message || 'Error');
            return result.data !== undefined ? result.data : result;
        } catch (error) {
            showToast(error.message || 'Error', 'error');
            throw error;
        }
    }

    const Validators = { required: (val) => val !== null && val !== undefined && String(val).trim() !== '' };

    function validateForm(rules) {
        let isValid = true;
        for (const [fieldId, checks] of Object.entries(rules)) {
            const el = document.getElementById(fieldId);
            if (!el) continue;
            for (const check of checks) {
                if (!check.fn(el.value)) {
                    el.style.borderColor = 'var(--danger)';
                    isValid = false; break;
                }
            }
            if (isValid) el.style.borderColor = '#e9ecef';
        }
        return isValid;
    }

    document.addEventListener('DOMContentLoaded', function() {
        const userStr = sessionStorage.getItem('loggedInUser');
        if (!userStr) { window.location.href = 'index.html'; return; }
        currentUser = JSON.parse(userStr);
        document.getElementById('userName').textContent = currentUser.fullName || currentUser.username;
        document.getElementById('userRole').textContent = currentUser.roleId == 1 ? 'مدير النظام' : 'مستخدم';
        
        setupEvents();
        loadData();
    });

    function setupEvents() {
        document.getElementById('tabCourses').addEventListener('click', () => switchTab('courses'));
        document.getElementById('tabAddOns').addEventListener('click', () => switchTab('addons'));
        
        document.getElementById('searchBtn').addEventListener('click', () => filterAndRender());
        document.getElementById('searchInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') filterAndRender(); });
        
        document.getElementById('addBtn').addEventListener('click', () => {
            if(currentTab === 'courses') openCourseModal();
            else openAddonModal();
        });
        
        document.getElementById('closeCourseModal').addEventListener('click', () => closeModals());
        document.getElementById('cancelCourseModal').addEventListener('click', () => closeModals());
        document.getElementById('saveCourseBtn').addEventListener('click', () => saveCourse());
        
        document.getElementById('closeAddonModal').addEventListener('click', () => closeModals());
        document.getElementById('cancelAddonModal').addEventListener('click', () => closeModals());
        document.getElementById('saveAddonBtn').addEventListener('click', () => saveAddon());
    }

    function switchTab(tab) {
        currentTab = tab;
        document.getElementById('tabCourses').style.background = tab === 'courses' ? 'var(--primary-blue)' : 'transparent';
        document.getElementById('tabCourses').style.color = tab === 'courses' ? 'white' : 'var(--dark)';
        document.getElementById('tabAddOns').style.background = tab === 'addons' ? 'var(--primary-blue)' : 'transparent';
        document.getElementById('tabAddOns').style.color = tab === 'addons' ? 'white' : 'var(--dark)';
        
        document.getElementById('coursesSection').style.display = tab === 'courses' ? 'block' : 'none';
        document.getElementById('addonsSection').style.display = tab === 'addons' ? 'block' : 'none';
        
        document.getElementById('addBtnText').textContent = tab === 'courses' ? 'إضافة كورس جديد' : 'إضافة ملحق جديد';
        
        currentPage = 1;
        filterAndRender();
    }

    async function loadData() {
        showLoading(true);
        try {
            const [coursesRes, deptsRes, addonsRes] = await Promise.all([
                apiCall('getAllCourses'),
                apiCall('getAllDepartments'),
                apiCall('getAllAddOns')
            ]);
            allDepts = deptsRes || [];
            allAddOns = addonsRes || [];
            
            const deptSelect = document.getElementById('courseDeptId');
            deptSelect.innerHTML = '<option value="">بدون قسم</option>' + allDepts.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            
            const addonCourseSelect = document.getElementById('addonCourseId');
            addonCourseSelect.innerHTML = '<option value="">عام (يظهر لكل الكورسات)</option>' + (coursesRes || []).map(c => `<option value="${c.id}">${c.name}</option>`).join('');
                
            allCourses = (coursesRes || []).map(c => {
                const dept = allDepts.find(d => d.id == c.deptId);
                return { ...c, deptName: dept ? dept.name : '-' };
            });
            
            filterAndRender();
        } catch (error) {}
        showLoading(false);
    }
    
    function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        
        if (currentTab === 'courses') {
            let filtered = allCourses.filter(s => (s.name && s.name.toLowerCase().includes(searchTerm)) || (s.deptName && s.deptName.toLowerCase().includes(searchTerm)));
            renderCourses(filtered);
        } else {
            let filtered = allAddOns.filter(s => s.name && s.name.toLowerCase().includes(searchTerm));
            renderAddons(filtered);
        }
    }
    
    function renderCourses(data) {
        const tbody = document.getElementById('coursesTableBody');
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">لا توجد بيانات</td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }
        
        const start = (currentPage - 1) * rowsPerPage;
        const paginated = data.slice(start, start + rowsPerPage);
        
        tbody.innerHTML = paginated.map(s => `
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
        `).join('');
        renderPagination(Math.ceil(data.length / rowsPerPage));
    }

    function renderAddons(data) {
        const tbody = document.getElementById('addonsTableBody');
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">لا توجد بيانات</td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }
        
        const start = (currentPage - 1) * rowsPerPage;
        const paginated = data.slice(start, start + rowsPerPage);
        
        tbody.innerHTML = paginated.map(s => {
            const course = allCourses.find(c => c.id == s.courseId);
            return `
            <tr>
                <td><strong>${s.id || '-'}</strong></td>
                <td>${s.name || '-'}</td>
                <td><span style="color:var(--success); font-weight:bold;">${s.price || 0} ج.م</span></td>
                <td>${course ? course.name : '<span style="color:var(--gray);">عام</span>'}</td>
                <td class="action-buttons">
                    <button class="btn-icon btn-edit" onclick="editAddon(${s.id})"><i class="fas fa-edit"></i></button>
                    <button class="btn-icon btn-delete" onclick="deleteAddon(${s.id})"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `}).join('');
        renderPagination(Math.ceil(data.length / rowsPerPage));
    }
    
    function renderPagination(totalPages) {
        const container = document.getElementById('pagination');
        if (totalPages <= 1) { container.innerHTML = ''; return; }
        let html = '';
        for (let i = 1; i <= totalPages; i++) {
            html += `<button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
        }
        container.innerHTML = html;
    }
    
    function goToPage(page) { currentPage = page; filterAndRender(); }
    
    // --- COURSES ---
    function openCourseModal() {
        document.getElementById('courseModalTitle').textContent = 'إضافة كورس جديد';
        document.getElementById('courseForm').reset();
        document.getElementById('courseId').value = '';
        document.getElementById('courseModal').classList.add('show');
    }
    
    function editCourse(id) {
        const user = allCourses.find(s => s.id == id);
        if (user) {
            document.getElementById('courseModalTitle').textContent = 'تعديل الكورس';
            document.getElementById('courseId').value = user.id;
            document.getElementById('courseName').value = user.name || '';
            document.getElementById('courseDeptId').value = user.deptId || '';
            document.getElementById('coursePrice').value = user.pricePerLevel || 0;
            document.getElementById('courseLevels').value = user.durationLevels || 1;
            document.getElementById('courseModal').classList.add('show');
        }
    }
    
    async function saveCourse() {
        const rules = { courseName: [{ fn: Validators.required, msg: 'الاسم مطلوب' }], coursePrice: [{ fn: Validators.required, msg: 'السعر مطلوب' }] };
        if (!validateForm(rules)) return;
        
        const data = {
            id: document.getElementById('courseId').value || null,
            name: document.getElementById('courseName').value,
            deptId: document.getElementById('courseDeptId').value,
            pricePerLevel: document.getElementById('coursePrice').value,
            durationLevels: document.getElementById('courseLevels').value
        };
        showLoading(true);
        try {
            await apiCall('saveCourse', { courseData: data });
            showToast('تم الحفظ بنجاح', 'success');
            closeModals(); loadData();
        } catch (e) {}
        showLoading(false);
    }
    
    async function deleteCourse(id) {
        if (confirm('هل أنت متأكد من حذف هذا الكورس؟')) {
            showLoading(true);
            try { await apiCall('deleteCourse', { id }); showToast('تم الحذف بنجاح', 'success'); loadData(); } catch (e) {}
            showLoading(false);
        }
    }

    // --- ADDONS ---
    function openAddonModal() {
        document.getElementById('addonModalTitle').textContent = 'إضافة ملحق جديد';
        document.getElementById('addonForm').reset();
        document.getElementById('addonId').value = '';
        document.getElementById('addonModal').classList.add('show');
    }

    function editAddon(id) {
        const addon = allAddOns.find(s => s.id == id);
        if (addon) {
            document.getElementById('addonModalTitle').textContent = 'تعديل الملحق';
            document.getElementById('addonId').value = addon.id;
            document.getElementById('addonName').value = addon.name || '';
            document.getElementById('addonPrice').value = addon.price || 0;
            document.getElementById('addonCourseId').value = addon.courseId || '';
            document.getElementById('addonModal').classList.add('show');
        }
    }

    async function saveAddon() {
        const rules = { addonName: [{ fn: Validators.required, msg: 'الاسم مطلوب' }], addonPrice: [{ fn: Validators.required, msg: 'السعر مطلوب' }] };
        if (!validateForm(rules)) return;
        
        const data = {
            id: document.getElementById('addonId').value || null,
            name: document.getElementById('addonName').value,
            price: document.getElementById('addonPrice').value,
            courseId: document.getElementById('addonCourseId').value
        };
        showLoading(true);
        try {
            await apiCall('saveAddOn', { addonData: data });
            showToast('تم الحفظ بنجاح', 'success');
            closeModals(); loadData();
        } catch (e) {}
        showLoading(false);
    }

    async function deleteAddon(id) {
        if (confirm('هل أنت متأكد من حذف هذه الإضافة؟')) {
            showLoading(true);
            try { await apiCall('deleteAddOn', { id }); showToast('تم الحذف بنجاح', 'success'); loadData(); } catch (e) {}
            showLoading(false);
        }
    }

    function closeModals() {
        document.getElementById('courseModal').classList.remove('show');
        document.getElementById('addonModal').classList.remove('show');
    }
    
    function showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) overlay.classList.add('show');
        else overlay.classList.remove('show');
    }
    
    window.editCourse = editCourse; window.deleteCourse = deleteCourse;
    window.editAddon = editAddon; window.deleteAddon = deleteAddon;
    window.goToPage = goToPage;
"""
content = content[:js_start] + new_js + content[js_end:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated courses.html to support AddOns")
