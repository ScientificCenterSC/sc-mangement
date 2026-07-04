const document = { getElementById: (id) => ({ id: id, value: 'all', addEventListener: () => {}, classList: { toggle: () => {}, add: () => {}, remove: () => {} }, innerHTML: '', style: {} }), addEventListener: () => {} }; const window = { location: { search: '' }, addEventListener: () => {} }; const sessionStorage = { getItem: () => JSON.stringify({id: 1, roleId: 1, fullName: 'Test'}), removeItem: () => {} }; const URLSearchParams = class { get() { return null; } }; let fetch = async () => ({ json: async () => ({ success: true, data: [] }) });
    // الرابط الجديد لـ Google Apps Script
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';
    
    let currentUser = null;
    let allPayments = [];
    let allCourses = [];
    let allAddOns = [];
    let allStudents = [];
    let allDepartments = [];
    let departments = [];
    let groups = [];
    let currentPage = 1;
    const rowsPerPage = 10;

    // Toast Notification
    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    // Centralized API Call
    async function apiCall(action, data = {}) {
        try {
            const response = await fetch(SCRIPT_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                body: JSON.stringify({ action, ...data })
            });
            const result = await response.json();
            if (result.success === false) {
                throw new Error(result.message || 'حدث خطأ غير معروف');
            }
            return result.data !== undefined ? result.data : result;
        } catch (error) {
            if (error.message && !error.message.includes('fetch')) {
                showToast(error.message, 'error');
            } else {
                showToast('حدث خطأ في الاتصال بالخادم', 'error');
            }
            throw error;
        }
    }

    // Form Validation
    const Validators = {
        required: (val) => val !== null && val !== undefined && String(val).trim() !== '',
        phone: (val) => !val || /^[0-9]{10,15}$/.test(val.replace(/[\s\-\+]/g, '')),
    };

    function validateForm(rules) {
        let isValid = true;
        for (const [fieldId, checks] of Object.entries(rules)) {
            const el = document.getElementById(fieldId);
            if (!el) continue;
            const val = el.value;
            let fieldValid = true;
            for (const check of checks) {
                if (!check.fn(val)) {
                    fieldValid = false;
                    el.style.borderColor = 'var(--danger)';
                    let errEl = el.parentElement.querySelector('.field-error');
                    if (!errEl) {
                        errEl = document.createElement('div');
                        errEl.className = 'field-error';
                        errEl.style.cssText = 'color: var(--danger); font-size: 11px; margin-top: 4px;';
                        el.parentElement.appendChild(errEl);
                    }
                    errEl.textContent = check.msg;
                    isValid = false;
                    break;
                }
            }
            if (fieldValid) {
                el.style.borderColor = '#e9ecef';
                const errEl = el.parentElement.querySelector('.field-error');
                if (errEl) errEl.remove();
            }
        }
        return isValid;
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        // Check login
        const userStr = sessionStorage.getItem('loggedInUser');
        if (!userStr) {
            window.location.href = 'index.html';
            return;
        }
        
        try {
            currentUser = JSON.parse(userStr);
        } catch(e) {
            sessionStorage.removeItem('loggedInUser');
            window.location.href = 'index.html';
            return;
        }
        
        updateUserUI();
        setupEventListeners();
        loadData();
    });

    function updateUserUI() {
        document.getElementById('userName').textContent = currentUser.fullName || currentUser.username;
        const roleNames = {1: 'مدير النظام', 2: 'محاسب', 3: 'مدير دور', 4: 'مسؤول حجوزات', 5: 'مشاهد'};
        document.getElementById('userRole').textContent = roleNames[currentUser.roleId] || 'مستخدم';
    }

    function setupEventListeners() {
        // Mobile menu toggle
        document.getElementById('menuToggle').addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('open');
        });
        
        // Logout
        document.getElementById('logoutBtn').addEventListener('click', function() {
            sessionStorage.removeItem('loggedInUser');
            window.location.href = 'index.html';
        });
        
        // Search
        document.getElementById('searchBtn').addEventListener('click', () => searchStudents());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchStudents();
        });
        
        // Filters
        const deptF = document.getElementById('deptFilter');
        if (deptF) deptF.addEventListener('change', () => { updateProgramFilters(); updateGroupFilters(); filterAndRender(); });
        
        const grpF = document.getElementById('groupFilter');
        if (grpF) grpF.addEventListener('change', () => filterAndRender());
        
        // Modal
        document.getElementById('addStudentBtn').addEventListener('click', () => openAddModal());
        document.getElementById('closeModal').addEventListener('click', () => closeModal());
        document.getElementById('cancelModal').addEventListener('click', () => closeModal());
        document.getElementById('saveStudent').addEventListener('click', () => saveStudent());
        
        // Close modal on outside click
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('studentModal');
            if (e.target === modal) closeModal();
        });
    }

    async function loadData() {
        showLoading(true);
        
        try {
            const [sRes, gRes, pRes, cRes, aRes, dRes] = await Promise.all([
                apiCall('getAllStudents'),
                apiCall('getAllGroups'),
                apiCall('getAllPayments'),
                apiCall('getAllCourses'),
                apiCall('getAllAddOns'),
                apiCall('getAllDepartments')
            ]);
            allStudents = sRes || [];
            groups = gRes || [];
            allPayments = pRes || [];
            allCourses = cRes || [];
            allAddOns = aRes || [];
            allDepartments = dRes || [];
            updateDepartmentDropdowns();
            
            updateGroupFilters();
            filterAndRender();
        } catch (error) {
            console.error('Error:', error);
            // Error handled in apiCall
        }
        
        showLoading(false);
    }
    
    
    function updateDepartmentDropdowns() {
        const deptFilter = document.getElementById('deptFilter');
        const stDept = document.getElementById('studentDept');
        
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

    function updateProgramFilters() {
        const deptId = document.getElementById('deptFilter')?.value;
        const programFilter = document.getElementById('programFilter');
        
        if (programFilter) {
            let filteredCourses = typeof allCourses !== 'undefined' ? allCourses : [];
            if (deptId !== 'all' && deptId) {
                filteredCourses = filteredCourses.filter(c => c.deptId == deptId);
            }
            let programHtml = '<option value="all">الكل</option>';
            filteredCourses.forEach(c => programHtml += `<option value="${c.id}">${c.courseName || c.name}</option>`);
            programFilter.innerHTML = programHtml;
        }
    }

    function updateGroupFilters() {
        const deptId = document.getElementById('deptFilter')?.value;
        const levelId = document.getElementById('levelFilter')?.value;
        const progId = document.getElementById('programFilter')?.value;
        
        const groupFilter = document.getElementById('groupFilter');
        const studentGroup = document.getElementById('studentGroup');
        
        let filteredGroups = typeof groups !== 'undefined' ? groups : [];
        if (deptId !== 'all' && deptId) filteredGroups = filteredGroups.filter(g => g.deptId == deptId);
        if (levelId !== 'all' && levelId) filteredGroups = filteredGroups.filter(g => String(g.level) === String(levelId));
        if (progId !== 'all' && progId) filteredGroups = filteredGroups.filter(g => g.courseId == progId);
        
        let options = '<option value="all">الكل</option>';
        let modalOptions = '<option value="">بدون جروب</option>';
        
        filteredGroups.forEach(g => {
            options += `<option value="${g.id}">${g.name}</option>`;
            modalOptions += `<option value="${g.id}">${g.name}</option>`;
        });
        
        if(groupFilter) groupFilter.innerHTML = options;
        if(studentGroup) studentGroup.innerHTML = modalOptions;
    }
    
    function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const deptFilter = document.getElementById('deptFilter').value;
        const levelFilter = document.getElementById('levelFilter').value;
        const programFilter = document.getElementById('programFilter').value;
        const groupFilter = document.getElementById('groupFilter').value;
        
        let filtered = [...allStudents];
        
        // Search filter
        if (searchTerm) {
            filtered = filtered.filter(s => 
                s.name?.toLowerCase().includes(searchTerm) ||
                s.code?.toLowerCase().includes(searchTerm) ||
                s.phone?.includes(searchTerm)
            );
        }
        
        // Department filter
        if (deptFilter !== 'all') {
            filtered = filtered.filter(s => s.deptId == deptFilter);
        }
        
        // Level filter - Students don't directly have 'level' in students table but groups do. Let's filter students by group if level or program is selected.
        // Or we just check their assigned group's attributes if they have one.
        if (levelFilter !== 'all' || programFilter !== 'all') {
            filtered = filtered.filter(s => {
                if (!s.groupId) return false;
                const grp = allGroups.find(g => g.id == s.groupId);
                if (!grp) return false;
                if (levelFilter !== 'all' && String(grp.level) !== String(levelFilter)) return false;
                if (programFilter !== 'all' && grp.courseId != programFilter) return false;
                return true;
            });
        }
        
        // Group filter
        if (groupFilter !== 'all') {
            filtered = filtered.filter(s => s.groupId == groupFilter);
        }
        
        renderTable(filtered);
    }
    
    function searchStudents() {
        currentPage = 1;
        filterAndRender();
    }
    
    function renderTable(students) {
        const tbody = document.getElementById('studentsTableBody');
        
        if (!students || students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">لا توجد طلاب<\/td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }
        
        // Pagination
        const totalPages = Math.ceil(students.length / rowsPerPage);
        const start = (currentPage - 1) * rowsPerPage;
        const paginated = students.slice(start, start + rowsPerPage);
        
        // Render rows
        tbody.innerHTML = paginated.map(s => {
            const deptName = {1: 'IT', 2: 'LANG', 3: 'BUS', 4: 'GD'}[s.deptId] || '-';
            const groupName = s.groupName || '-';
            const createdDate = s.createdAt ? new Date(s.createdAt).toLocaleDateString('ar-EG') : '-';
            
            return `
                <tr>
                    <td><strong>${s.code || '-'}<\/strong></td>
                    <td>${s.name || '-'}<\/td>
                    <td>${s.phone || '-'}<\/td>
                    <td>${s.school || '-'}<\/td>
                    <td>${s.age || '-'}<\/td>
                    <td>${deptName}<\/td>
                    <td>${groupName}<\/td>
                    <td>${createdDate}<\/td>
                    <td class="action-buttons">
                        <button class="btn-icon btn-view" onclick="viewStudent(${s.id})"><i class="fas fa-eye"></i></button>
                        <button class="btn-icon btn-edit" onclick="editStudent(${s.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon btn-delete" onclick="deleteStudent(${s.id})"><i class="fas fa-trash"></i></button>
                    <\/td>
                </tr>
            `;
        }).join('');
        
        // Render pagination
        renderPagination(totalPages);
    }
    
    function renderPagination(totalPages) {
        const container = document.getElementById('pagination');
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let html = '';
        for (let i = 1; i <= totalPages; i++) {
            html += `<button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
        }
        container.innerHTML = html;
    }
    
    function goToPage(page) {
        currentPage = page;
        filterAndRender();
    }
    
    function viewStudent(id) {
        window.open(`student_profile.html?id=${id}`, '_blank');
    }

    
    function editStudent(id) {
        const student = allStudents.find(s => s.id == id);
        if (student) {
            document.getElementById('modalTitle').textContent = 'تعديل بيانات الطالب';
            document.getElementById('studentId').value = student.id;
            document.getElementById('studentName').value = student.name || '';
            document.getElementById('studentPhone').value = student.phone || '';
            document.getElementById('studentSchool').value = student.school || '';
            document.getElementById('studentAge').value = student.age || '';
            document.getElementById('studentDept').value = student.deptId || '';
            document.getElementById('studentGroup').value = student.groupId || '';
            document.getElementById('studentModal').classList.add('show');
        }
    }
    
    function openAddModal() {
        document.getElementById('modalTitle').textContent = 'إضافة طالب جديد';
        document.getElementById('studentForm').reset();
        document.getElementById('studentId').value = '';
        document.getElementById('studentModal').classList.add('show');
    }
    
    function closeModal() {
        document.getElementById('studentModal').classList.remove('show');
    }
    
    async function saveStudent() {
        const rules = {
            studentName: [{ fn: Validators.required, msg: 'الاسم مطلوب' }],
            studentPhone: [
                { fn: Validators.required, msg: 'رقم الهاتف مطلوب' },
                { fn: Validators.phone, msg: 'رقم الهاتف غير صالح' }
            ],
            studentDept: [{ fn: Validators.required, msg: 'القسم مطلوب' }]
        };
        
        if (!validateForm(rules)) return;
        
        const studentData = {
            id: document.getElementById('studentId').value || null,
            name: document.getElementById('studentName').value,
            phone: document.getElementById('studentPhone').value,
            school: document.getElementById('studentSchool').value,
            age: parseInt(document.getElementById('studentAge').value, 10) || null,
            deptId: parseInt(document.getElementById('studentDept').value, 10) || null,
            groupId: parseInt(document.getElementById('studentGroup').value, 10) || null
        };
        
        showLoading(true);
        try {
            await apiCall('saveStudent', studentData);
            showToast('تم حفظ بيانات الطالب بنجاح', 'success');
            closeModal();
            loadData();
        } catch (error) {
            // Error handled in apiCall
        }
        showLoading(false);
    }
    
    async function deleteStudent(id) {
        if (confirm('هل أنت متأكد من حذف هذا الطالب؟')) {
            showLoading(true);
            try {
                await apiCall('deleteStudent', { studentId: id });
                showToast('تم حذف الطالب بنجاح', 'success');
                loadData();
            } catch (error) {
                // Error handled in apiCall
            }
            showLoading(false);
        }
    }
    
    function showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) overlay.classList.add('show');
        else overlay.classList.remove('show');
    }
    
    // Make functions global for onclick
    window.viewStudent = viewStudent;
    
    function viewProfile(id) {
        window.location.href = 'student_profile.html?id=' + id;
    }
    
    window.viewProfile = viewProfile;
window.editStudent = editStudent;
    window.deleteStudent = deleteStudent;
    window.goToPage = goToPage;


(async () => { await loadData(); console.log('Done'); })();
