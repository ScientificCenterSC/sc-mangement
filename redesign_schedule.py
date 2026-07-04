import os

filepath = "c:/Users/shahd/Downloads/ss/schedule.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find('<div class="content-area">')
end_idx = content.find('<!-- Booking Modal -->')

if start_idx != -1 and end_idx != -1:
    new_html = """<div class="content-area">
            <!-- Filter Bar -->
            <div class="filter-bar" style="display: flex; gap: 15px; background: white; padding: 20px; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); align-items: flex-end; flex-wrap: wrap;">
                <div class="filter-group" style="flex: 1; min-width: 200px;">
                    <label style="display: block; margin-bottom: 8px; color: var(--gray); font-size: 13px;"><i class="fas fa-building"></i> تصفية بالقاعة</label>
                    <select id="hallFilter" style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 10px;">
                        <option value="all">كل القاعات</option>
                    </select>
                </div>
                <div class="filter-group" style="flex: 1; min-width: 200px;">
                    <label style="display: block; margin-bottom: 8px; color: var(--gray); font-size: 13px;"><i class="fas fa-chalkboard-user"></i> تصفية بالمدرب</label>
                    <select id="trainerFilter" style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 10px;">
                        <option value="all">كل المدربين</option>
                    </select>
                </div>
                <button id="applyFilterBtn" style="padding: 12px 24px; background: var(--primary-blue); color: white; border: none; border-radius: 10px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: bold;"><i class="fas fa-filter"></i> تطبيق التصفية</button>
                <button id="addBookingBtn" style="padding: 12px 24px; background: var(--success); color: white; border: none; border-radius: 10px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: bold; margin-right: auto;"><i class="fas fa-plus"></i> حجز جديد</button>
            </div>

            <!-- Board View -->
            <div class="board-container" style="background: white; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; min-width: 1000px;" id="scheduleBoard">
                    <thead id="boardHeader">
                        <!-- Headers injected via JS -->
                    </thead>
                    <tbody id="boardBody">
                        <!-- Rows injected via JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>
"""
    content = content[:start_idx] + new_html + content[end_idx:]

# Rewrite JS functions completely
js_start = content.find('const daysOfWeek = [')
js_end = content.find('window.editBooking = editBooking;')

if js_start != -1 and js_end != -1:
    new_js = """const daysOfWeek = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const daysNames = { Saturday: 'السبت', Sunday: 'الأحد', Monday: 'الاثنين', Tuesday: 'الثلاثاء', Wednesday: 'الأربعاء', Thursday: 'الخميس', Friday: 'الجمعة' };

    document.addEventListener('DOMContentLoaded', function() {
        const userStr = sessionStorage.getItem('loggedInUser');
        if (!userStr) { window.location.href = 'index.html'; return; }
        
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
        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.toggle('open'));
        document.getElementById('logoutBtn').addEventListener('click', () => { sessionStorage.removeItem('loggedInUser'); window.location.href = 'index.html'; });
        
        document.getElementById('applyFilterBtn').addEventListener('click', () => renderBoard());
        document.getElementById('addBookingBtn').addEventListener('click', () => openAddModal());
        document.getElementById('closeModal').addEventListener('click', () => closeModal());
        document.getElementById('cancelModal').addEventListener('click', () => closeModal());
        document.getElementById('saveBooking').addEventListener('click', () => saveBooking());
        document.getElementById('deleteBookingBtn').addEventListener('click', () => deleteBooking());
        
        window.addEventListener('click', (e) => { if (e.target === document.getElementById('bookingModal')) closeModal(); });
    }

    async function loadData() {
        showLoading(true);
        try {
            const [bRes, hRes, tRes, gRes, fRes] = await Promise.all([
                apiCall('getAllBookings'),
                apiCall('getAllHalls'),
                apiCall('getAllTrainers'),
                apiCall('getAllGroups'),
                apiCall('getAllFloors')
            ]);
            allBookings = bRes || [];
            allHalls = hRes || [];
            allTrainers = tRes || [];
            allGroups = gRes || [];
            allFloors = fRes || [];
            
            updateFilters();
            renderBoard();
        } catch(e) {}
        showLoading(false);
    }

    function updateFilters() {
        const hallFilter = document.getElementById('hallFilter');
        const trainerFilter = document.getElementById('trainerFilter');
        const hallSelect = document.getElementById('hallId');
        const trainerSelect = document.getElementById('trainerId');
        const groupSelect = document.getElementById('groupId');
        
        hallFilter.innerHTML = '<option value="all">كل القاعات</option>';
        trainerFilter.innerHTML = '<option value="all">كل المدربين</option>';
        hallSelect.innerHTML = '';
        trainerSelect.innerHTML = '';
        groupSelect.innerHTML = '<option value="">بدون جروب</option>';
        
        allHalls.forEach(h => {
            hallFilter.innerHTML += `<option value="${h.id}">${h.name}</option>`;
            hallSelect.innerHTML += `<option value="${h.id}">${h.name}</option>`;
        });
        
        allTrainers.forEach(t => {
            trainerFilter.innerHTML += `<option value="${t.id}">${t.name}</option>`;
            trainerSelect.innerHTML += `<option value="${t.id}">${t.name}</option>`;
        });
        
        allGroups.forEach(g => {
            groupSelect.innerHTML += `<option value="${g.id}">${g.name}</option>`;
        });
    }

    function getVisibleFloors() {
        let allowed = currentUser.allowedFloors || '*';
        if (allowed === '*') return allFloors;
        let allowedIds = allowed.toString().split(',').map(id => parseInt(id));
        return allFloors.filter(f => allowedIds.includes(f.id));
    }

    function renderBoard() {
        const hallFilter = document.getElementById('hallFilter').value;
        const trainerFilter = document.getElementById('trainerFilter').value;
        const visibleFloors = getVisibleFloors();
        
        let filteredBookings = [...allBookings];
        // Filter out bookings for floors user doesn't have access to
        filteredBookings = filteredBookings.filter(b => {
            const hall = allHalls.find(h => h.id == b.hallId);
            return hall && visibleFloors.some(f => f.id == hall.floorNumber);
        });
        
        if (hallFilter !== 'all') filteredBookings = filteredBookings.filter(b => b.hallId == hallFilter);
        if (trainerFilter !== 'all') filteredBookings = filteredBookings.filter(b => b.trainerId == trainerFilter);
        
        const header = document.getElementById('boardHeader');
        const body = document.getElementById('boardBody');
        
        // Render Header (Days)
        let headerHtml = `<tr>
            <th style="padding: 15px; background: var(--dark-blue); color: white; border: 1px solid #dee2e6; width: 120px; position: sticky; right: 0; z-index: 10;">الدور / القاعات</th>
        `;
        for (let day of daysOfWeek) {
            headerHtml += `<th style="padding: 15px; background: var(--dark-blue); color: white; border: 1px solid #dee2e6; text-align: center; min-width: 250px;">${daysNames[day]}</th>`;
        }
        headerHtml += `</tr>`;
        header.innerHTML = headerHtml;
        
        // Render Body (Floors)
        let bodyHtml = '';
        if (visibleFloors.length === 0) {
            bodyHtml = `<tr><td colspan="8" style="text-align: center; padding: 50px; color: var(--gray);">ليس لديك صلاحية لرؤية أي قاعات أو أدوار.</td></tr>`;
        } else {
            for (let floor of visibleFloors) {
                let rowHtml = `<tr>
                    <td style="padding: 15px; background: #f8f9fa; border: 1px solid #dee2e6; font-weight: bold; text-align: center; position: sticky; right: 0; z-index: 9; box-shadow: -2px 0 5px rgba(0,0,0,0.02);">
                        <div style="font-size: 16px; color: var(--primary-blue);">${floor.name}</div>
                    </td>
                `;
                
                for (let day of daysOfWeek) {
                    // Get all bookings for this floor and this day
                    let dayBookings = filteredBookings.filter(b => {
                        const hall = allHalls.find(h => h.id == b.hallId);
                        return b.day === day && hall && hall.floorNumber == floor.id;
                    });
                    
                    // Sort bookings by start time
                    dayBookings.sort((a, b) => a.startTime.localeCompare(b.startTime));
                    
                    let cellContent = '';
                    if (dayBookings.length > 0) {
                        cellContent = `<div style="display: flex; flex-direction: column; gap: 10px;">`;
                        for (let booking of dayBookings) {
                            const trainer = allTrainers.find(t => t.id === booking.trainerId);
                            const hall = allHalls.find(h => h.id === booking.hallId);
                            const group = allGroups.find(g => g.id === booking.groupId);
                            const isConflict = booking.conflict === 'CONFLICT';
                            
                            const cardStyle = isConflict 
                                ? "background: #fff5f5; border-right: 4px solid var(--danger); padding: 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s;"
                                : "background: #f8faff; border-right: 4px solid var(--primary-blue); padding: 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s;";
                            
                            cellContent += `
                                <div style="${cardStyle}" onclick="editBooking(${booking.id})" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                        <span style="font-size: 14px; font-weight: bold; color: ${isConflict ? 'var(--danger)' : 'var(--dark-blue)'};"><i class="far fa-clock"></i> ${booking.startTime} - ${booking.endTime}</span>
                                        <span style="font-size: 12px; background: ${isConflict ? '#fee2e2' : '#e0e7ff'}; color: ${isConflict ? '#991b1b' : '#3730a3'}; padding: 3px 8px; border-radius: 12px; font-weight: bold;">${hall?.name || 'قاعة غير محددة'}</span>
                                    </div>
                                    <div style="font-size: 13px; color: var(--dark); margin-bottom: 4px;"><i class="fas fa-chalkboard-user" style="color: var(--gray); width: 16px;"></i> المدرب: <strong>${trainer?.name || 'غير محدد'}</strong></div>
                                    <div style="font-size: 13px; color: var(--dark);"><i class="fas fa-users" style="color: var(--gray); width: 16px;"></i> الجروب: <strong>${group?.name || 'بدون جروب'}</strong></div>
                                </div>
                            `;
                        }
                        cellContent += `</div>`;
                    }
                    
                    // Add an "Add" button at the bottom of the cell
                    cellContent += `
                        <div style="margin-top: 15px; text-align: center;">
                            <button onclick="openAddModalAtSlot('${day}', '${floor.id}')" style="background: transparent; border: 1px dashed #ccc; color: var(--gray); padding: 8px; width: 100%; border-radius: 8px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#f8f9fa'; this.style.borderColor='var(--primary-blue)'; this.style.color='var(--primary-blue)';" onmouseout="this.style.background='transparent'; this.style.borderColor='#ccc'; this.style.color='var(--gray)';">
                                <i class="fas fa-plus"></i> إضافة حجز
                            </button>
                        </div>
                    `;
                    
                    rowHtml += `<td style="padding: 15px; border: 1px solid #dee2e6; vertical-align: top; background: white;">${cellContent}</td>`;
                }
                rowHtml += `</tr>`;
                bodyHtml += rowHtml;
            }
        }
        body.innerHTML = bodyHtml;
    }

    function openAddModal() {
        document.getElementById('modalTitle').textContent = 'حجز جديد';
        document.getElementById('bookingForm').reset();
        document.getElementById('bookingId').value = '';
        document.getElementById('deleteBookingBtn').style.display = 'none';
        document.getElementById('bookingModal').classList.add('show');
    }

    function openAddModalAtSlot(day, floorId) {
        document.getElementById('modalTitle').textContent = 'حجز جديد';
        document.getElementById('bookingForm').reset();
        document.getElementById('bookingId').value = '';
        document.getElementById('bookingDay').value = day;
        
        // Auto-select first hall in this floor
        const floorHalls = allHalls.filter(h => h.floorNumber == floorId);
        if (floorHalls.length > 0) {
            document.getElementById('hallId').value = floorHalls[0].id;
        }
        
        document.getElementById('deleteBookingBtn').style.display = 'none';
        document.getElementById('bookingModal').classList.add('show');
    }

    function editBooking(id) {
        const booking = allBookings.find(b => b.id == id);
        if (!booking) return;
        
        document.getElementById('modalTitle').textContent = 'تعديل الحجز';
        document.getElementById('bookingId').value = booking.id;
        document.getElementById('bookingDay').value = booking.day;
        document.getElementById('startTime').value = booking.startTime;
        document.getElementById('endTime').value = booking.endTime;
        document.getElementById('hallId').value = booking.hallId;
        document.getElementById('trainerId').value = booking.trainerId;
        document.getElementById('groupId').value = booking.groupId || '';
        document.getElementById('deleteBookingBtn').style.display = 'block';
        document.getElementById('bookingModal').classList.add('show');
    }

    function closeModal() {
        document.getElementById('bookingModal').classList.remove('show');
    }

    async function saveBooking() {
        const rules = {
            bookingDay: [{ fn: Validators.required, msg: 'اليوم مطلوب' }],
            startTime: [{ fn: Validators.required, msg: 'وقت البدء مطلوب' }],
            endTime: [{ fn: Validators.required, msg: 'وقت الانتهاء مطلوب' }],
            hallId: [{ fn: Validators.required, msg: 'القاعة مطلوبة' }],
            trainerId: [{ fn: Validators.required, msg: 'المدرب مطلوب' }]
        };
        
        if (!validateForm(rules)) return;
        
        const bookingData = {
            id: document.getElementById('bookingId').value || null,
            day: document.getElementById('bookingDay').value,
            startTime: document.getElementById('startTime').value,
            endTime: document.getElementById('endTime').value,
            hallId: parseInt(document.getElementById('hallId').value, 10) || 0,
            trainerId: parseInt(document.getElementById('trainerId').value, 10) || 0,
            groupId: document.getElementById('groupId').value ? parseInt(document.getElementById('groupId').value, 10) : null,
            createdBy: currentUser.id
        };
        
        showLoading(true);
        try {
            await apiCall('saveBooking', bookingData);
            showToast('تم حفظ الحجز بنجاح', 'success');
            closeModal();
            loadData();
        } catch(e) {}
        showLoading(false);
    }

    async function deleteBooking() {
        const id = document.getElementById('bookingId').value;
        if (!id) return;
        if (confirm('هل أنت متأكد من حذف هذا الحجز؟')) {
            showLoading(true);
            try {
                await apiCall('deleteBooking', { bookingId: id });
                showToast('تم حذف الحجز بنجاح', 'success');
                closeModal();
                loadData();
            } catch(e) {}
            showLoading(false);
        }
    }

    function showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) overlay.classList.add('show');
        else overlay.classList.remove('show');
    }

    """
    content = content[:js_start] + new_js + content[js_end:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Redesigned schedule.html board view")
