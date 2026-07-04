import re

with open('floors.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Tabs and Hall Table
tabs_html = '''
            <div class="tabs" style="display: flex; gap: 10px; margin-bottom: 20px;">
                <button class="tab-btn active" id="tab-floors" onclick="switchTab('floors')" style="padding: 10px 20px; border: none; background: var(--primary-blue); color: white; border-radius: 8px; cursor: pointer;">الأدوار</button>
                <button class="tab-btn" id="tab-halls" onclick="switchTab('halls')" style="padding: 10px 20px; border: none; background: white; color: var(--dark-blue); border-radius: 8px; cursor: pointer;">القاعات</button>
            </div>
            
            <div class="toolbar">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="بحث...">
                    <button id="searchBtn"><i class="fas fa-search"></i> بحث</button>
                </div>
                <button class="btn-add" id="addBtn" onclick="openAddModal()">
                    <i class="fas fa-plus"></i>
                    <span id="addBtnText">إضافة دور جديد</span>
                </button>
            </div>

            <!-- Floors Table -->
            <div class="floors-table-container" id="floorsView">
                <table class="floors-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>اسم الدور</th>
                            <th>اللون المميز</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="floorsTableBody">
                        <tr><td colspan="5" style="text-align: center;">جاري التحميل...</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- Halls Table -->
            <div class="floors-table-container" id="hallsView" style="display: none;">
                <table class="floors-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>اسم القاعة</th>
                            <th>الدور</th>
                            <th>النوع</th>
                            <th>السعة</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="hallsTableBody">
                        <tr><td colspan="7" style="text-align: center;">جاري التحميل...</td></tr>
                    </tbody>
                </table>
            </div>
'''
content = re.sub(r'<div class="toolbar">.*?</button>\s*</div>\s*<!-- Filters removed for Users -->\s*<!-- users Table -->\s*<div class="floors-table-container">.*?</div>\s*<!-- Pagination -->\s*<div class="pagination" id="pagination"></div>', tabs_html, content, flags=re.DOTALL)

# 2. Modals for Floor and Hall
modals_html = '''
<!-- Add/Edit Floor Modal -->
<div class="modal" id="floorModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3 id="floorModalTitle">إضافة دور جديد</h3>
            <button class="close-modal" onclick="closeModal('floorModal')">&times;</button>
        </div>
        <div class="modal-body">
            <form id="floorForm">
                <input type="hidden" id="floorId">
                <div class="form-group">
                    <label>اسم الدور *</label>
                    <input type="text" id="floorName" required placeholder="مثال: الدور الأول">
                </div>
                <div class="form-group">
                    <label>اللون المميز</label>
                    <input type="color" id="floorColor" value="#4a8fe0">
                </div>
                <div class="form-group">
                    <label>الحالة</label>
                    <select id="floorStatus">
                        <option value="Active">نشط</option>
                        <option value="Inactive">غير نشط</option>
                    </select>
                </div>
            </form>
        </div>
        <div class="modal-footer">
            <button class="btn-cancel" onclick="closeModal('floorModal')">إلغاء</button>
            <button class="btn-save" onclick="saveFloor()">حفظ</button>
        </div>
    </div>
</div>

<!-- Add/Edit Hall Modal -->
<div class="modal" id="hallModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3 id="hallModalTitle">إضافة قاعة جديدة</h3>
            <button class="close-modal" onclick="closeModal('hallModal')">&times;</button>
        </div>
        <div class="modal-body">
            <form id="hallForm">
                <input type="hidden" id="hallId">
                <div class="form-group">
                    <label>اسم القاعة *</label>
                    <input type="text" id="hallName" required placeholder="مثال: Hall A">
                </div>
                <div class="form-group">
                    <label>الدور *</label>
                    <select id="hallFloorId" required></select>
                </div>
                <div class="form-group">
                    <label>النوع</label>
                    <select id="hallType">
                        <option value="theory">نظري</option>
                        <option value="practical">عملي (معمل)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>السعة</label>
                    <input type="number" id="hallCapacity" value="20">
                </div>
                <div class="form-group">
                    <label>الحالة</label>
                    <select id="hallStatus">
                        <option value="Active">نشط</option>
                        <option value="Inactive">غير نشط</option>
                    </select>
                </div>
            </form>
        </div>
        <div class="modal-footer">
            <button class="btn-cancel" onclick="closeModal('hallModal')">إلغاء</button>
            <button class="btn-save" onclick="saveHall()">حفظ</button>
        </div>
    </div>
</div>
'''
content = re.sub(r'<!-- Add/Edit user Modal -->\s*<div class="modal" id="floorModal">.*?</div>\s*</div>\s*</div>', modals_html, content, flags=re.DOTALL)

# 3. JS Logic
js_logic = '''
    let currentTab = 'floors';
    let allHalls = [];

    function switchTab(tab) {
        currentTab = tab;
        document.getElementById('tab-floors').style.background = tab === 'floors' ? 'var(--primary-blue)' : 'white';
        document.getElementById('tab-floors').style.color = tab === 'floors' ? 'white' : 'var(--dark-blue)';
        document.getElementById('tab-halls').style.background = tab === 'halls' ? 'var(--primary-blue)' : 'white';
        document.getElementById('tab-halls').style.color = tab === 'halls' ? 'white' : 'var(--dark-blue)';
        
        document.getElementById('floorsView').style.display = tab === 'floors' ? 'block' : 'none';
        document.getElementById('hallsView').style.display = tab === 'halls' ? 'block' : 'none';
        
        document.getElementById('addBtnText').textContent = tab === 'floors' ? 'إضافة دور جديد' : 'إضافة قاعة جديدة';
        filterAndRender();
    }

    async function loadData() {
        showLoading(true);
        try {
            const [fRes, hRes] = await Promise.all([
                apiCall('getAllFloors'),
                apiCall('getAllHalls')
            ]);
            allFloors = fRes || [];
            allHalls = hRes || [];
            
            // Populate floor dropdown in hall modal
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
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">لا توجد أدوار</td></tr>';
                return;
            }
            tbody.innerHTML = filtered.map(f => `
                <tr>
                    <td>${f.id}</td>
                    <td><strong>${f.name}</strong></td>
                    <td><div style="width: 20px; height: 20px; background-color: ${f.color || '#ccc'}; border-radius: 50%;"></div></td>
                    <td><span class="badge ${f.status==='Active'?'badge-success':'badge-danger'}">${f.status === 'Active' ? 'نشط' : 'غير نشط'}</span></td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn-icon btn-edit" onclick="editFloor(${f.id})"><i class="fas fa-edit"></i></button>
                            <button class="btn-icon btn-delete" onclick="deleteFloor(${f.id})"><i class="fas fa-trash"></i></button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } else {
            let filtered = allHalls.filter(s => !searchTerm || (s.name && s.name.toLowerCase().includes(searchTerm)));
            const tbody = document.getElementById('hallsTableBody');
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">لا توجد قاعات</td></tr>';
                return;
            }
            tbody.innerHTML = filtered.map(h => {
                const floor = allFloors.find(f => f.id == h.floorId);
                return `
                <tr>
                    <td>${h.id}</td>
                    <td><strong>${h.name}</strong></td>
                    <td>${floor ? floor.name : '-'}</td>
                    <td>${h.type === 'theory' ? 'نظري' : 'عملي'}</td>
                    <td>${h.capacity}</td>
                    <td><span class="badge ${h.status==='Active'?'badge-success':'badge-danger'}">${h.status === 'Active' ? 'نشط' : 'غير نشط'}</span></td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn-icon btn-edit" onclick="editHall(${h.id})"><i class="fas fa-edit"></i></button>
                            <button class="btn-icon btn-delete" onclick="deleteHall(${h.id})"><i class="fas fa-trash"></i></button>
                        </div>
                    </td>
                </tr>
            `}).join('');
        }
    }

    function openAddModal() {
        if (currentTab === 'floors') {
            document.getElementById('floorModal').classList.add('show');
            document.getElementById('floorModalTitle').textContent = 'إضافة دور جديد';
            document.getElementById('floorId').value = '';
            document.getElementById('floorName').value = '';
            document.getElementById('floorColor').value = '#4a8fe0';
            document.getElementById('floorStatus').value = 'Active';
        } else {
            document.getElementById('hallModal').classList.add('show');
            document.getElementById('hallModalTitle').textContent = 'إضافة قاعة جديدة';
            document.getElementById('hallId').value = '';
            document.getElementById('hallName').value = '';
            document.getElementById('hallFloorId').value = '';
            document.getElementById('hallType').value = 'theory';
            document.getElementById('hallCapacity').value = '20';
            document.getElementById('hallStatus').value = 'Active';
        }
    }

    function closeModal(modalId) {
        document.getElementById(modalId).classList.remove('show');
    }

    function editFloor(id) {
        const f = allFloors.find(x => x.id == id);
        if (f) {
            openAddModal();
            document.getElementById('floorModalTitle').textContent = 'تعديل الدور';
            document.getElementById('floorId').value = f.id;
            document.getElementById('floorName').value = f.name;
            document.getElementById('floorColor').value = f.color || '#4a8fe0';
            document.getElementById('floorStatus').value = f.status || 'Active';
        }
    }

    async function saveFloor() {
        if(!validateForm({ floorName: [{ fn: Validators.required, msg: 'الاسم مطلوب' }] })) return;
        const data = {
            id: document.getElementById('floorId').value || undefined,
            name: document.getElementById('floorName').value,
            color: document.getElementById('floorColor').value,
            status: document.getElementById('floorStatus').value
        };
        showLoading(true);
        const res = await apiCall('saveFloor', { floorData: data });
        if (res.success) {
            closeModal('floorModal');
            loadData();
        } else alert(res.message);
        showLoading(false);
    }

    async function deleteFloor(id) {
        if (!confirm('هل أنت متأكد من الحذف؟')) return;
        showLoading(true);
        const res = await apiCall('deleteFloor', { id });
        if (res.success) loadData();
        else alert(res.message);
        showLoading(false);
    }

    function editHall(id) {
        const h = allHalls.find(x => x.id == id);
        if (h) {
            currentTab = 'halls'; // ensure we open right modal
            openAddModal();
            document.getElementById('hallModalTitle').textContent = 'تعديل القاعة';
            document.getElementById('hallId').value = h.id;
            document.getElementById('hallName').value = h.name;
            document.getElementById('hallFloorId').value = h.floorId || h.floor_id || '';
            document.getElementById('hallType').value = h.type || 'theory';
            document.getElementById('hallCapacity').value = h.capacity || 20;
            document.getElementById('hallStatus').value = h.status || 'Active';
        }
    }

    async function saveHall() {
        if(!validateForm({ 
            hallName: [{ fn: Validators.required, msg: 'الاسم مطلوب' }],
            hallFloorId: [{ fn: Validators.required, msg: 'الدور مطلوب' }]
        })) return;
        
        const data = {
            id: document.getElementById('hallId').value || undefined,
            name: document.getElementById('hallName').value,
            floorId: document.getElementById('hallFloorId').value,
            type: document.getElementById('hallType').value,
            capacity: document.getElementById('hallCapacity').value,
            status: document.getElementById('hallStatus').value
        };
        showLoading(true);
        const res = await apiCall('saveHall', { hallData: data });
        if (res.success) {
            closeModal('hallModal');
            loadData();
        } else alert(res.message);
        showLoading(false);
    }

    async function deleteHall(id) {
        if (!confirm('هل أنت متأكد من الحذف؟')) return;
        showLoading(true);
        const res = await apiCall('deleteHall', { id });
        if (res.success) loadData();
        else alert(res.message);
        showLoading(false);
    }
'''
content = re.sub(r'async function loadData\(\) \{.*?\}\s*function filterAndRender\(\) \{.*?\}', js_logic, content, flags=re.DOTALL)

with open('floors.html', 'w', encoding='utf-8') as f:
    f.write(content)
