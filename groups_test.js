
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';
    
    let currentUser = null;
    let allGroups = [];
    let allDepartments = [];
    let allCourses = [];
    let allTrainers = [];

    // Toast Notification
    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<span>${message}</span>`;
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
            showToast(error.message || 'حدث خطأ في الاتصال بالخادم', 'error');
            throw error;
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        const userStr = sessionStorage.getItem('loggedInUser');
        if (!userStr) { window.location.href = 'index.html'; return; }
        try { currentUser = JSON.parse(userStr); } catch(e) { window.location.href = 'index.html'; return; }
        
        document.getElementById('userName').textContent = currentUser.fullName || currentUser.username;
        const roleNames = {1: 'مدير النظام', 2: 'محاسب'};
        document.getElementById('userRole').textContent = roleNames[currentUser.roleId] || 'مستخدم';
        
        setupEventListeners();
        loadData();
    });

    function setupEventListeners() {
        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.toggle('open'));
        document.getElementById('logoutBtn').addEventListener('click', () => { sessionStorage.removeItem('loggedInUser'); window.location.href = 'index.html'; });
        
        document.getElementById('searchBtn').addEventListener('click', () => filterAndRender());
        document.getElementById('searchInput').addEventListener('keyup', () => filterAndRender());
        
        document.getElementById('deptFilter').addEventListener('change', () => { populateFilterDropdowns(); filterAndRender(); });
        document.getElementById('programFilter').addEventListener('change', () => filterAndRender());
        
        // Modal Events
        document.getElementById('addGroupBtn').addEventListener('click', openAddModal);
        document.getElementById('closeModal').addEventListener('click', closeModal);
        document.getElementById('cancelModal').addEventListener('click', closeModal);
        document.getElementById('saveGroupBtn').addEventListener('click', saveGroup);
        
        // Form Cascading
        document.getElementById('formDept').addEventListener('change', () => populateFormDropdowns());
    }

    async function loadData() {
        showLoading(true);
        try {
            const [gRes, dRes, cRes, tRes] = await Promise.all([
                apiCall('getAllGroups'),
                apiCall('getAllDepartments'),
                apiCall('getAllCourses'),
                apiCall('getAllTrainers')
            ]);
            allGroups = gRes || [];
            allDepartments = dRes || [];
            allCourses = cRes || [];
            allTrainers = tRes || [];
            
            populateBaseDropdowns();
            populateFilterDropdowns();
            filterAndRender();
        } catch (error) { console.error(error); }
        showLoading(false);
    }
    
    function populateBaseDropdowns() {
        // Filters
        const deptFilter = document.getElementById('deptFilter');
        const formDept = document.getElementById('formDept');
        
        let deptHtmlFilter = '<option value="all">الكل</option>';
        let deptHtmlForm = '<option value="">اختر القسم</option>';
        
        allDepartments.forEach(d => {
            deptHtmlFilter += `<option value="${d.id}">${d.name}</option>`;
            deptHtmlForm += `<option value="${d.id}">${d.name}</option>`;
        });
        
        deptFilter.innerHTML = deptHtmlFilter;
        formDept.innerHTML = deptHtmlForm;
        
        // Form Trainers
        const formTrainer = document.getElementById('formTrainer');
        let trainerHtml = '<option value="">بدون مدرب</option>';
        allTrainers.forEach(t => trainerHtml += `<option value="${t.id}">${t.name}</option>`);
        formTrainer.innerHTML = trainerHtml;
    }

    function populateFilterDropdowns() {
        const deptId = document.getElementById('deptFilter').value;
        const programFilter = document.getElementById('programFilter');
        
        // Program logic: Filter courses by department
        let filteredCourses = allCourses;
        if (deptId !== 'all') {
            filteredCourses = filteredCourses.filter(c => c.deptId == deptId);
        }
        
        let programHtml = '<option value="all">الكل</option>';
        filteredCourses.forEach(c => programHtml += `<option value="${c.id}">${c.courseName || c.name}</option>`);
        programFilter.innerHTML = programHtml;
    }
    
    function populateFormDropdowns() {
        const deptId = document.getElementById('formDept').value;
        const formProgram = document.getElementById('formProgram');
        
        let filteredCourses = allCourses;
        if (deptId) {
            filteredCourses = filteredCourses.filter(c => c.deptId == deptId);
        }
        
        let programHtml = '<option value="">اختر البرنامج</option>';
        filteredCourses.forEach(c => programHtml += `<option value="${c.id}">${c.courseName || c.name}</option>`);
        programFilter.innerHTML = programHtml;
    }

    function filterAndRender() {
        const search = document.getElementById('searchInput').value.toLowerCase();
        const deptId = document.getElementById('deptFilter').value;
        const progId = document.getElementById('programFilter').value;
        
        let filtered = allGroups.filter(g => {
            const matchesSearch = g.name.toLowerCase().includes(search);
            const matchesDept = deptId === 'all' || g.deptId == deptId;
            const matchesProg = progId === 'all' || g.courseId == progId;
            return matchesSearch && matchesDept && matchesProg;
        });
        
        const tbody = document.getElementById('groupsTableBody');
        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">لا توجد بيانات</td></tr>';
            return;
        }
        
        tbody.innerHTML = filtered.map(g => {
            const dept = allDepartments.find(d => d.id == g.deptId) || {};
            const course = allCourses.find(c => c.id == g.courseId) || {};
            const trainer = allTrainers.find(t => t.id == g.trainerId) || {};
            const statusBadge = g.status === 'Inactive' 
                ? '<span style="color:var(--danger);font-weight:bold;">غير نشط</span>' 
                : '<span style="color:var(--success);font-weight:bold;">نشط</span>';
                
            return `
                <tr>
                    <td>${g.id}</td>
                    <td><strong>${g.name}</strong></td>
                    <td>${dept.name || '-'}</td>
                    <td>${course.courseName || course.name || '-'}</td>
                    <td>${trainer.name || '-'}</td>
                    <td>${g.capacity || '-'}</td>
                    <td>${statusBadge}</td>
                    <td class="action-buttons">
                        <button class="btn-icon btn-edit" onclick="editGroup(${g.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon btn-delete" onclick="deleteGroup(${g.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function openAddModal() {
        document.getElementById('modalTitle').textContent = 'إضافة جروب جديد';
        document.getElementById('groupForm').reset();
        document.getElementById('groupId').value = '';
        populateFormDropdowns();
        document.getElementById('groupModal').classList.add('show');
    }

    function editGroup(id) {
        const group = allGroups.find(g => g.id == id);
        if (!group) return;
        
        document.getElementById('modalTitle').textContent = 'تعديل الجروب';
        document.getElementById('groupId').value = group.id;
        document.getElementById('formDept').value = group.deptId || '';
        
        populateFormDropdowns(); // Populate courses based on department
        
        setTimeout(() => {
            document.getElementById('formProgram').value = group.courseId || '';
        }, 50);
        
        document.getElementById('formGroupName').value = group.name || '';
        document.getElementById('formTrainer').value = group.trainerId || '';
        document.getElementById('formCapacity').value = group.capacity || '';
        document.getElementById('formStatus').value = group.status || 'Active';
        
        if (group.startDate) {
            const date = new Date(group.startDate);
            if (!isNaN(date.getTime())) {
                document.getElementById('formStartDate').value = date.toISOString().split('T')[0];
            }
        }
        
        document.getElementById('groupModal').classList.add('show');
    }

    function closeModal() {
        document.getElementById('groupModal').classList.remove('show');
    }

    async function saveGroup() {
        const id = document.getElementById('groupId').value;
        const deptId = document.getElementById('formDept').value;
        const courseId = document.getElementById('formProgram').value;
        const name = document.getElementById('formGroupName').value;
        
        if (!deptId || !courseId || !name) {
            showToast('الرجاء تعبئة جميع الحقول المطلوبة', 'error');
            return;
        }
        
        const data = {
            id: id || null,
            deptId: parseInt(deptId, 10),
            level: parseInt(level, 10),
            courseId: parseInt(courseId, 10),
            name: name,
            trainerId: parseInt(document.getElementById('formTrainer').value, 10) || null,
            capacity: parseInt(document.getElementById('formCapacity').value, 10) || null,
            status: document.getElementById('formStatus').value,
            startDate: document.getElementById('formStartDate').value || new Date()
        };
        
        showLoading(true);
        try {
            await apiCall('saveGroup', { groupData: data });
            showToast('تم الحفظ بنجاح', 'success');
            closeModal();
            loadData();
        } catch (e) { }
        showLoading(false);
    }

    async function deleteGroup(id) {
        if (!confirm('هل أنت متأكد من حذف الجروب؟')) return;
        showLoading(true);
        try {
            await apiCall('deleteGroup', { groupId: id });
            showToast('تم الحذف بنجاح', 'success');
            loadData();
        } catch (e) { }
        showLoading(false);
    }

    function showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) overlay.classList.add('show');
        else overlay.classList.remove('show');
    }

