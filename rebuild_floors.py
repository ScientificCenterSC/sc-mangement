with open('floors.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the script tag and cut everything from there to the end
idx = content.index('<script>')
html_part = content[:idx]

new_script = """<script>
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';
    
    let currentUser = null;
    let allFloors = [];
    let allHalls = [];
    let currentTab = 'floors';

    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    function showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) overlay.classList.add('show');
        else overlay.classList.remove('show');
    }

    async function apiCall(action, data = {}) {
        try {
            const response = await fetch(SCRIPT_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                body: JSON.stringify({ action, ...data })
            });
            const result = await response.json();
            if (result.success === false) throw new Error(result.message || 'خطأ');
            return result.data !== undefined ? result.data : result;
        } catch (error) {
            showToast(error.message || 'خطأ في الاتصال', 'error');
            throw error;
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        const userStr = sessionStorage.getItem('loggedInUser');
        if (!userStr) { window.location.href = 'index.html'; return; }
        try { currentUser = JSON.parse(userStr); } catch(e) { window.location.href = 'index.html'; return; }
        
        document.getElementById('userName').textContent = currentUser.fullName || currentUser.username;
        const roleNames = {1:'مدير النظام',2:'محاسب',3:'مدير دور',4:'مسؤول حجوزات',5:'مشاهد'};
        document.getElementById('userRole').textContent = roleNames[currentUser.roleId] || 'مستخدم';

        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.toggle('open'));
        document.getElementById('logoutBtn').addEventListener('click', () => { sessionStorage.removeItem('loggedInUser'); window.location.href = 'index.html'; });
        document.getElementById('searchBtn').addEventListener('click', () => filterAndRender());
        document.getElementById('searchInput').addEventListener('keypress', e => { if(e.key==='Enter') filterAndRender(); });
        document.getElementById('addBtn').addEventListener('click', () => openAddModal());

        loadData();
    });

    window.switchTab = function(tab) {
        currentTab = tab;
        document.getElementById('tab-floors').style.background = tab === 'floors' ? 'var(--primary-blue)' : 'white';
        document.getElementById('tab-floors').style.color = tab === 'floors' ? 'white' : 'var(--dark-blue)';
        document.getElementById('tab-halls').style.background = tab === 'halls' ? 'var(--primary-blue)' : 'white';
        document.getElementById('tab-halls').style.color = tab === 'halls' ? 'white' : 'var(--dark-blue)';
        document.getElementById('floorsView').style.display = tab === 'floors' ? 'block' : 'none';
        document.getElementById('hallsView').style.display = tab === 'halls' ? 'block' : 'none';
        document.getElementById('addBtnText').textContent = tab === 'floors' ? 'إضافة دور جديد' : 'إضافة قاعة جديدة';
        filterAndRender();
    };

    async function loadData() {
        showLoading(true);
        try {
            const [fRes, hRes] = await Promise.all([
                apiCall('getAllFloors'),
                apiCall('getAllHalls')
            ]);
            allFloors = fRes || [];
            allHalls = hRes || [];
            
            const floorSelect = document.getElementById('hallFloorId');
            floorSelect.innerHTML = '<option value="">اختر الدور...</option>';
            allFloors.forEach(f => {
                floorSelect.innerHTML += `<option value="${f.id}">${f.name}</option>`;
            });
            
            filterAndRender();
        } catch (error) {
            console.error('Error:', error);
        }
        showLoading(false);
    }
    
    function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        
        if (currentTab === 'floors') {
            let filtered = allFloors.filter(s => !searchTerm || (s.name && s.name.toLowerCase().includes(searchTerm)));
            const tbody = document.getElementById('floorsTableBody');
            if (!filtered.length) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--gray)">لا توجد أدوار</td></tr>';
                return;
            }
            tbody.innerHTML = filtered.map(f => `
                <tr>
                    <td>${f.id}</td>
                    <td><strong>${f.name}</strong></td>
                    <td><div style="width:20px;height:20px;background:${f.color||'#ccc'};border-radius:50%;display:inline-block;"></div></td>
                    <td><span class="badge ${f.status==='Active'?'badge-success':'badge-danger'}">${f.status==='Active'?'نشط':'غير نشط'}</span></td>
                    <td><div class="action-buttons">
                        <button class="btn-icon btn-edit" onclick="editFloor(${f.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon btn-delete" onclick="confirmDeleteFloor(${f.id})"><i class="fas fa-trash"></i></button>
                    </div></td>
                </tr>
            `).join('');
        } else {
            let filtered = allHalls.filter(s => !searchTerm || (s.name && s.name.toLowerCase().includes(searchTerm)));
            const tbody = document.getElementById('hallsTableBody');
            if (!filtered.length) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:30px;color:var(--gray)">لا توجد قاعات</td></tr>';
                return;
            }
            tbody.innerHTML = filtered.map(h => {
                const floor = allFloors.find(f => f.id == h.floorId);
                return `<tr>
                    <td>${h.id}</td>
                    <td><strong>${h.name}</strong></td>
                    <td>${floor ? floor.name : '-'}</td>
                    <td>${h.type === 'theory' ? 'نظري' : 'عملي'}</td>
                    <td>${h.capacity || '-'}</td>
                    <td><span class="badge ${h.status==='Active'?'badge-success':'badge-danger'}">${h.status==='Active'?'نشط':'غير نشط'}</span></td>
                    <td><div class="action-buttons">
                        <button class="btn-icon btn-edit" onclick="editHall(${h.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon btn-delete" onclick="confirmDeleteHall(${h.id})"><i class="fas fa-trash"></i></button>
                    </div></td>
                </tr>`;
            }).join('');
        }
    }

    function openAddModal() {
        if (currentTab === 'floors') {
            document.getElementById('floorModalTitle').textContent = 'إضافة دور جديد';
            document.getElementById('floorId').value = '';
            document.getElementById('floorName').value = '';
            document.getElementById('floorColor').value = '#4a8fe0';
            document.getElementById('floorStatus').value = 'Active';
            document.getElementById('floorModal').classList.add('show');
        } else {
            document.getElementById('hallModalTitle').textContent = 'إضافة قاعة جديدة';
            document.getElementById('hallId').value = '';
            document.getElementById('hallName').value = '';
            document.getElementById('hallFloorId').value = '';
            document.getElementById('hallType').value = 'theory';
            document.getElementById('hallCapacity').value = '20';
            document.getElementById('hallStatus').value = 'Active';
            document.getElementById('hallModal').classList.add('show');
        }
    }

    window.closeModal = function(modalId) {
        document.getElementById(modalId).classList.remove('show');
    };

    window.editFloor = function(id) {
        const f = allFloors.find(x => x.id == id);
        if (!f) return;
        document.getElementById('floorModalTitle').textContent = 'تعديل الدور';
        document.getElementById('floorId').value = f.id;
        document.getElementById('floorName').value = f.name;
        document.getElementById('floorColor').value = f.color || '#4a8fe0';
        document.getElementById('floorStatus').value = f.status || 'Active';
        document.getElementById('floorModal').classList.add('show');
    };

    window.saveFloor = async function() {
        const name = document.getElementById('floorName').value.trim();
        if (!name) { showToast('اسم الدور مطلوب', 'warning'); return; }
        const data = {
            id: document.getElementById('floorId').value || undefined,
            name,
            color: document.getElementById('floorColor').value,
            status: document.getElementById('floorStatus').value
        };
        showLoading(true);
        try {
            await apiCall('saveFloor', { floorData: data });
            showToast('تم الحفظ بنجاح', 'success');
            closeModal('floorModal');
            loadData();
        } catch(e) {}
        showLoading(false);
    };

    window.confirmDeleteFloor = async function(id) {
        if (!confirm('هل أنت متأكد من حذف هذا الدور؟')) return;
        showLoading(true);
        try {
            await apiCall('deleteFloor', { id });
            showToast('تم الحذف بنجاح', 'success');
            loadData();
        } catch(e) {}
        showLoading(false);
    };

    window.editHall = function(id) {
        const h = allHalls.find(x => x.id == id);
        if (!h) return;
        document.getElementById('hallModalTitle').textContent = 'تعديل القاعة';
        document.getElementById('hallId').value = h.id;
        document.getElementById('hallName').value = h.name;
        document.getElementById('hallFloorId').value = h.floorId || '';
        document.getElementById('hallType').value = h.type || 'theory';
        document.getElementById('hallCapacity').value = h.capacity || 20;
        document.getElementById('hallStatus').value = h.status || 'Active';
        document.getElementById('hallModal').classList.add('show');
    };

    window.saveHall = async function() {
        const name = document.getElementById('hallName').value.trim();
        const floorId = document.getElementById('hallFloorId').value;
        if (!name) { showToast('اسم القاعة مطلوب', 'warning'); return; }
        if (!floorId) { showToast('يرجى اختيار الدور', 'warning'); return; }
        const data = {
            id: document.getElementById('hallId').value || undefined,
            name,
            floorId,
            type: document.getElementById('hallType').value,
            capacity: document.getElementById('hallCapacity').value,
            status: document.getElementById('hallStatus').value
        };
        showLoading(true);
        try {
            await apiCall('saveHall', { hallData: data });
            showToast('تم الحفظ بنجاح', 'success');
            closeModal('hallModal');
            loadData();
        } catch(e) {}
        showLoading(false);
    };

    window.confirmDeleteHall = async function(id) {
        if (!confirm('هل أنت متأكد من حذف هذه القاعة؟')) return;
        showLoading(true);
        try {
            await apiCall('deleteHall', { id });
            showToast('تم الحذف بنجاح', 'success');
            loadData();
        } catch(e) {}
        showLoading(false);
    };
</script>

<script src="sidebar.js"></script>
</body>
</html>
"""

new_content = html_part + new_script

with open('floors.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done - floors.html rebuilt")
