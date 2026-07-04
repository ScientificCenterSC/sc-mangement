import os
import re

filepath = "c:/Users/shahd/Downloads/ss/roles.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# I will find the start of <div class="content-area"> and end of </body>
start_idx = content.find('<div class="content-area">')
end_idx = content.find('</body>')

if start_idx != -1 and end_idx != -1:
    new_content = """<div class="content-area">
            <!-- Toolbar -->
            <div class="toolbar">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="بحث باسم الصلاحية...">
                    <button id="searchBtn"><i class="fas fa-search"></i> بحث</button>
                </div>
                <button class="btn-add" id="addRoleBtn">
                    <i class="fas fa-plus"></i>
                    <span>إضافة صلاحية جديدة</span>
                </button>
            </div>

            <!-- users Table -->
            <div class="users-table-container">
                <table class="users-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>اسم الصلاحية</th>
                            <th>الوصف</th>
                            <th>القاعات المسموحة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="rolesTableBody">
                        <tr>
                            <td colspan="5" style="text-align: center;">جاري التحميل...</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div class="pagination" id="pagination"></div>
        </div>
    </main>
</div>

<!-- Add/Edit user Modal -->
<div class="modal" id="roleModal">
    <div class="modal-content" style="max-width: 800px;">
        <div class="modal-header">
            <h3 id="modalTitle">إضافة صلاحية جديدة</h3>
            <button class="close-modal" id="closeModal">&times;</button>
        </div>
        <div class="modal-body">
            <form id="roleForm">
                <input type="hidden" id="userId" value="">
                <div class="form-row">
                    <div class="form-group">
                        <label>اسم الصلاحية *</label>
                        <input type="text" id="roleName" required placeholder="أدخل اسم الصلاحية">
                    </div>
                    <div class="form-group">
                        <label>الوصف</label>
                        <input type="text" id="roleDesc" placeholder="وصف الصلاحية">
                    </div>
                </div>
                <div class="form-group" style="margin-bottom: 20px;">
                    <label style="border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 10px;">الأدوار (القاعات) المسموح بها</label>
                    <div id="floorsCheckboxes" style="display:flex; gap:15px; flex-wrap:wrap; padding: 10px; background: #f8f9fa; border-radius: 8px;"></div>
                </div>
                <div class="form-group">
                    <label style="border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 10px;">صلاحيات الصفحات</label>
                    <div style="background: #f8f9fa; border-radius: 8px; padding: 10px; max-height: 300px; overflow-y: auto;">
                        <table class="users-table" style="min-width:100%; font-size:13px; background: white;">
                            <thead>
                                <tr>
                                    <th>الصفحة / النظام</th>
                                    <th>عرض (View)</th>
                                    <th>تعديل (Edit)</th>
                                </tr>
                            </thead>
                            <tbody id="permissionsCheckboxes">
                            </tbody>
                        </table>
                    </div>
                </div>
            </form>
        </div>
        <div class="modal-footer">
            <button class="btn-cancel" id="cancelModal">إلغاء</button>
            <button class="btn-save" id="saveRole">حفظ</button>
        </div>
    </div>
</div>

<script>
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';
    
    let currentUser = null;
    let allRoles = [];
    let allPermissions = [];
    let allFloors = [];
    let currentPage = 1;
    const rowsPerPage = 10;
    
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

    const Validators = {
        required: (val) => val !== null && val !== undefined && String(val).trim() !== '',
    };

    function validateForm(rules) {
        let isValid = true;
        for (const [fieldId, checks] of Object.entries(rules)) {
            const el = document.getElementById(fieldId);
            if (!el) continue;
            const val = el.value;
            for (const check of checks) {
                if (!check.fn(val)) {
                    el.style.borderColor = 'var(--danger)';
                    isValid = false;
                    break;
                }
            }
            if (isValid) el.style.borderColor = '#e9ecef';
        }
        return isValid;
    }

    document.addEventListener('DOMContentLoaded', function() {
        const userStr = sessionStorage.getItem('loggedInUser');
        if (!userStr) {
            window.location.href = 'index.html';
            return;
        }
        try { currentUser = JSON.parse(userStr); } 
        catch(e) { window.location.href = 'index.html'; return; }
        
        document.getElementById('userName').textContent = currentUser.fullName || currentUser.username;
        document.getElementById('userRole').textContent = currentUser.roleId == 1 ? 'مدير النظام' : 'مستخدم';
        
        document.getElementById('searchBtn').addEventListener('click', () => searchRoles());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchRoles();
        });
        
        document.getElementById('addRoleBtn').addEventListener('click', () => openAddModal());
        document.getElementById('closeModal').addEventListener('click', () => closeModal());
        document.getElementById('cancelModal').addEventListener('click', () => closeModal());
        document.getElementById('saveRole').addEventListener('click', () => saveRole());
        
        loadData();
    });

    async function loadData() {
        showLoading(true);
        try {
            const [rolesRes, permsRes, floorsRes] = await Promise.all([
                apiCall('getAllRoles'),
                apiCall('getAllPermissions'),
                apiCall('getAllFloors')
            ]);
            allRoles = rolesRes || [];
            allPermissions = permsRes || [];
            allFloors = floorsRes || [];
            
            filterAndRender();
            renderPermissionsCheckboxes();
            renderFloorsCheckboxes();
        } catch (error) {}
        showLoading(false);
    }
    
    function renderPermissionsCheckboxes() {
        const tbody = document.getElementById('permissionsCheckboxes');
        const modules = [...new Set(allPermissions.map(p => p.module))];
        const moduleNames = {
            'dashboard': 'الرئيسية (Dashboard)',
            'students': 'الطلاب (Students)',
            'trainers': 'المدربين (Trainers)',
            'schedule': 'الجدول (Schedule)',
            'payments': 'المدفوعات (Payments)',
            'reports': 'التقارير (Reports)',
            'settings': 'المستخدمين (Users)',
            'departments': 'الأقسام (Departments)',
            'courses': 'الكورسات (Courses)',
            'floors': 'الأدوار (Floors)',
            'roles': 'الصلاحيات (Roles)'
        };
        
        tbody.innerHTML = modules.map(mod => {
            const viewPerm = allPermissions.find(p => p.module === mod && p.action === 'view');
            const editPerm = allPermissions.find(p => p.module === mod && p.action === 'edit');
            
            return `
                <tr>
                    <td><strong>${moduleNames[mod] || mod}</strong></td>
                    <td style="text-align: center;">${viewPerm ? `<input type="checkbox" class="perm-cb" style="transform: scale(1.3); cursor: pointer;" data-id="${viewPerm.id}" id="perm_${viewPerm.id}">` : '-'}</td>
                    <td style="text-align: center;">${editPerm ? `<input type="checkbox" class="perm-cb" style="transform: scale(1.3); cursor: pointer;" data-id="${editPerm.id}" id="perm_${editPerm.id}">` : '-'}</td>
                </tr>
            `;
        }).join('');
    }

    function renderFloorsCheckboxes() {
        const container = document.getElementById('floorsCheckboxes');
        container.innerHTML = allFloors.map(f => `
            <label style="cursor: pointer; display: flex; align-items: center; gap: 5px;">
                <input type="checkbox" class="floor-cb" value="${f.id}" style="transform: scale(1.2);"> 
                ${f.name}
            </label>
        `).join('');
    }
    
    function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        let filtered = [...allRoles];
        
        if (searchTerm) {
            filtered = filtered.filter(s => 
                (s.name && s.name.toLowerCase().includes(searchTerm)) ||
                (s.description && s.description.toLowerCase().includes(searchTerm))
            );
        }
        renderTable(filtered);
    }
    
    function searchRoles() {
        currentPage = 1;
        filterAndRender();
    }
    
    function renderTable(roles) {
        const tbody = document.getElementById('rolesTableBody');
        if (!roles || roles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">لا يوجد صلاحيات</td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }
        
        const totalPages = Math.ceil(roles.length / rowsPerPage);
        const start = (currentPage - 1) * rowsPerPage;
        const paginated = roles.slice(start, start + rowsPerPage);
        
        tbody.innerHTML = paginated.map(s => {
            let floorsStr = '';
            if (s.allowedFloors && s.allowedFloors !== '*') {
                const floorIds = s.allowedFloors.toString().split(',');
                floorsStr = floorIds.map(fid => {
                    const f = allFloors.find(fl => fl.id == fid);
                    return f ? `<span style="background: #e9ecef; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin: 2px; display: inline-block;">${f.name}</span>` : '';
                }).join('');
            } else if (s.allowedFloors === '*') {
                floorsStr = '<span style="background: var(--primary-blue); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">كل الأدوار</span>';
            }
            
            return `
                <tr>
                    <td><strong>${s.id || '-'}</strong></td>
                    <td>${s.name || '-'}</td>
                    <td>${s.description || '-'}</td>
                    <td>${floorsStr || '-'}</td>
                    <td class="action-buttons">
                        <button class="btn-icon btn-edit" onclick="editRole(${s.id})"><i class="fas fa-edit"></i></button>
                        ${s.id != 1 ? `<button class="btn-icon btn-delete" onclick="deleteRole(${s.id})"><i class="fas fa-trash"></i></button>` : ''}
                    </td>
                </tr>
            `;
        }).join('');
        
        renderPagination(totalPages);
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
    
    async function editRole(id) {
        const role = allRoles.find(s => s.id == id);
        if (role) {
            document.getElementById('modalTitle').textContent = 'تعديل الصلاحية';
            document.getElementById('userId').value = role.id;
            document.getElementById('roleName').value = role.name || '';
            document.getElementById('roleDesc').value = role.description || '';
            
            document.querySelectorAll('.perm-cb').forEach(cb => cb.checked = false);
            document.querySelectorAll('.floor-cb').forEach(cb => cb.checked = false);
            
            if (role.allowedFloors) {
                const allowedIds = role.allowedFloors.toString().split(',');
                document.querySelectorAll('.floor-cb').forEach(cb => {
                    if (allowedIds.includes(cb.value) || role.allowedFloors === '*') cb.checked = true;
                });
            }
            
            showLoading(true);
            try {
                const rolePermIds = await apiCall('getRolePermissions', { roleId: role.id });
                (rolePermIds || []).forEach(pid => {
                    const cb = document.getElementById('perm_' + pid);
                    if (cb) cb.checked = true;
                });
            } catch (e) {}
            showLoading(false);
            
            document.getElementById('roleModal').classList.add('show');
        }
    }
    
    function openAddModal() {
        document.getElementById('modalTitle').textContent = 'إضافة صلاحية جديدة';
        document.getElementById('roleForm').reset();
        document.getElementById('userId').value = '';
        document.querySelectorAll('.perm-cb').forEach(cb => cb.checked = false);
        document.querySelectorAll('.floor-cb').forEach(cb => cb.checked = false);
        document.getElementById('roleModal').classList.add('show');
    }
    
    function closeModal() {
        document.getElementById('roleModal').classList.remove('show');
    }
    
    async function saveRole() {
        const rules = {
            roleName: [{ fn: Validators.required, msg: 'الاسم مطلوب' }]
        };
        if (!validateForm(rules)) return;
        
        const selectedFloors = Array.from(document.querySelectorAll('.floor-cb:checked')).map(cb => cb.value).join(',');
        const selectedPerms = Array.from(document.querySelectorAll('.perm-cb:checked')).map(cb => parseInt(cb.getAttribute('data-id')));
        
        const roleData = {
            id: document.getElementById('userId').value || null,
            name: document.getElementById('roleName').value,
            description: document.getElementById('roleDesc').value,
            status: 'Active',
            allowedFloors: selectedFloors
        };
        
        showLoading(true);
        try {
            const res = await apiCall('saveRole', { data: roleData });
            const roleId = res.roleId || roleData.id;
            
            if (roleId) {
                await apiCall('saveRolePermissions', { roleId: roleId, permissionIds: selectedPerms });
            }
            
            showToast('تم الحفظ بنجاح', 'success');
            closeModal();
            loadData();
        } catch (error) {}
        showLoading(false);
    }
    
    async function deleteRole(id) {
        if (id == 1) {
            showToast('لا يمكن حذف صلاحية مدير النظام', 'error');
            return;
        }
        if (confirm('هل أنت متأكد من حذف هذه الصلاحية؟')) {
            showLoading(true);
            try {
                await apiCall('deleteRole', { id: id });
                showToast('تم الحذف بنجاح', 'success');
                loadData();
            } catch (error) {}
            showLoading(false);
        }
    }
    
    function showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) overlay.classList.add('show');
        else overlay.classList.remove('show');
    }
    
    window.editRole = editRole;
    window.deleteRole = deleteRole;
    window.goToPage = goToPage;
</script>
<script src="sidebar.js"></script>
"""
    
    content = content[:start_idx] + new_content + content[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated roles.html completely.")
