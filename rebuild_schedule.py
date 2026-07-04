with open('schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.index('<script>')
html_part = content[:idx]

new_script = """<script>
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';
    
    let currentUser = null;
    let allBookings = [];
    let allHalls = [];
    let allTrainers = [];
    let allGroups = [];
    let allFloors = [];
    let allDepartments = [];

    const daysOfWeek = ['Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday'];
    const daysNames = { Saturday:'السبت', Sunday:'الأحد', Monday:'الاثنين', Tuesday:'الثلاثاء', Wednesday:'الأربعاء', Thursday:'الخميس' };

    // Time slots 9 AM to 10 PM
    const timeSlots = [];
    for (let i = 9; i <= 22; i++) {
        const suffix = i >= 12 ? 'م' : 'ص';
        const h12 = i > 12 ? i - 12 : i;
        timeSlots.push({ time24: `${String(i).padStart(2,'0')}:00`, display: `${h12}:00 ${suffix}` });
    }

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
        document.getElementById('applyFilterBtn').addEventListener('click', () => renderBoard());
        document.getElementById('addBookingBtn').addEventListener('click', () => openAddModal());
        document.getElementById('closeModal').addEventListener('click', () => closeModal());
        document.getElementById('cancelModal').addEventListener('click', () => closeModal());
        document.getElementById('saveBooking').addEventListener('click', () => saveBooking());
        document.getElementById('deleteBookingBtn').addEventListener('click', () => deleteBooking());
        window.addEventListener('click', e => { if(e.target === document.getElementById('bookingModal')) closeModal(); });

        loadData();
    });

    async function loadData() {
        showLoading(true);
        try {
            const [bRes, hRes, tRes, gRes, fRes, dRes] = await Promise.all([
                apiCall('getAllBookings'),
                apiCall('getAllHalls'),
                apiCall('getAllTrainers'),
                apiCall('getAllGroups'),
                apiCall('getAllFloors'),
                apiCall('getAllDepartments')
            ]);
            allBookings = bRes || [];
            allHalls = hRes || [];
            allTrainers = tRes || [];
            allGroups = gRes || [];
            allFloors = fRes || [];
            allDepartments = dRes || [];
            
            populateFilters();
            renderBoard();
        } catch(e) { console.error(e); }
        showLoading(false);
    }

    function populateFilters() {
        const hallFilter = document.getElementById('hallFilter');
        const trainerFilter = document.getElementById('trainerFilter');
        const floorFilter = document.getElementById('floorFilter');
        const deptFilter = document.getElementById('deptFilter');
        const hallSelect = document.getElementById('hallId');
        const trainerSelect = document.getElementById('trainerId');
        const groupSelect = document.getElementById('groupId');

        hallFilter.innerHTML = '<option value="all">كل القاعات</option>';
        allHalls.forEach(h => hallFilter.innerHTML += `<option value="${h.id}">${h.name}</option>`);

        trainerFilter.innerHTML = '<option value="all">كل المدربين</option>';
        allTrainers.forEach(t => trainerFilter.innerHTML += `<option value="${t.id}">${t.name}</option>`);

        if (floorFilter) {
            floorFilter.innerHTML = '<option value="all">كل الأدوار</option>';
            allFloors.forEach(f => floorFilter.innerHTML += `<option value="${f.id}">${f.name}</option>`);
        }
        if (deptFilter) {
            deptFilter.innerHTML = '<option value="all">كل الأقسام</option>';
            allDepartments.forEach(d => deptFilter.innerHTML += `<option value="${d.id}">${d.name}</option>`);
        }

        hallSelect.innerHTML = '<option value="">اختر القاعة...</option>';
        allHalls.forEach(h => hallSelect.innerHTML += `<option value="${h.id}">${h.name}</option>`);

        trainerSelect.innerHTML = '<option value="">اختر المدرب...</option>';
        allTrainers.forEach(t => trainerSelect.innerHTML += `<option value="${t.id}">${t.name}</option>`);

        groupSelect.innerHTML = '<option value="">بدون جروب</option>';
        allGroups.forEach(g => groupSelect.innerHTML += `<option value="${g.id}">${g.name}</option>`);
    }

    function renderBoard() {
        const hallFilter = document.getElementById('hallFilter').value;
        const trainerFilter = document.getElementById('trainerFilter').value;

        let filteredBookings = [...allBookings];
        if (hallFilter !== 'all') filteredBookings = filteredBookings.filter(b => b.hallId == hallFilter);
        if (trainerFilter !== 'all') filteredBookings = filteredBookings.filter(b => b.trainerId == trainerFilter);

        const header = document.getElementById('boardHeader');
        const body = document.getElementById('boardBody');

        let headerHtml = '<tr><th style="padding:15px;background:var(--dark-blue);color:white;border:1px solid #dee2e6;width:120px;position:sticky;right:0;z-index:10;">اليوم / الوقت</th>';
        for (const slot of timeSlots) {
            headerHtml += `<th style="padding:10px;background:var(--dark-blue);color:white;border:1px solid #dee2e6;text-align:center;min-width:150px;">${slot.display}</th>`;
        }
        headerHtml += '</tr>';
        header.innerHTML = headerHtml;

        const floorColors = ['#e3f2fd','#fce4ec','#e8f5e9','#fff3e0','#f3e5f5'];
        const floorBorderColors = ['#2196f3','#e91e63','#4caf50','#ff9800','#9c27b0'];

        let bodyHtml = '';
        for (const day of daysOfWeek) {
            let rowHtml = `<tr>
                <td style="padding:15px;background:#f8f9fa;border:1px solid #dee2e6;font-weight:bold;text-align:center;position:sticky;right:0;z-index:9;">
                    <div style="color:var(--primary-blue);font-size:15px;">${daysNames[day]}</div>
                    <button onclick="openAddModalAtDay('${day}')" style="margin-top:8px;background:transparent;border:1px dashed #ccc;color:var(--gray);padding:4px;width:100%;border-radius:6px;cursor:pointer;font-size:11px;">
                        <i class="fas fa-plus"></i> إضافة
                    </button>
                </td>`;
            
            for (const slot of timeSlots) {
                const time = slot.time24;
                let cellContent = '';

                for (let i = 0; i < allFloors.length; i++) {
                    const floor = allFloors[i];
                    const floorColor = floorColors[i % floorColors.length];
                    const borderColor = floorBorderColors[i % floorBorderColors.length];

                    const floorBookings = filteredBookings.filter(b => {
                        const hall = allHalls.find(h => h.id == b.hallId);
                        const bookingDays = b.days || (b.day ? [b.day] : []);
                        return bookingDays.includes(day) && hall && hall.floorId == floor.id && b.startTime <= time && b.endTime > time;
                    });

                    if (floorBookings.length > 0) {
                        cellContent += `<div style="background:${floorColor};border-right:4px solid ${borderColor};padding:6px;margin-bottom:4px;border-radius:6px;font-size:11px;">
                            <div style="font-weight:bold;margin-bottom:3px;">${floor.name}</div>`;
                        for (const b of floorBookings) {
                            const trainer = allTrainers.find(t => t.id == b.trainerId);
                            const hall = allHalls.find(h => h.id == b.hallId);
                            cellContent += `<div onclick="editBooking(${b.id})" style="cursor:pointer;background:rgba(255,255,255,0.7);padding:4px;margin-top:3px;border-radius:4px;">
                                <div style="font-weight:bold;">${b.startTime} - ${b.endTime}</div>
                                <div><i class="fas fa-door-open"></i> ${hall?.name||'-'}</div>
                                <div><i class="fas fa-user-tie"></i> ${trainer?.name||'-'}</div>
                            </div>`;
                        }
                        cellContent += '</div>';
                    }
                }

                rowHtml += `<td style="padding:8px;border:1px solid #dee2e6;vertical-align:top;background:white;min-height:80px;">${cellContent}</td>`;
            }
            rowHtml += '</tr>';
            bodyHtml += rowHtml;
        }
        body.innerHTML = bodyHtml;
    }

    function openAddModal() {
        document.getElementById('modalTitle').textContent = 'حجز جديد';
        document.getElementById('bookingId').value = '';
        document.querySelectorAll('input[name="bookingDays"]').forEach(cb => cb.checked = false);
        document.getElementById('startTime').value = '';
        document.getElementById('endTime').value = '';
        document.getElementById('hallId').value = '';
        document.getElementById('trainerId').value = '';
        document.getElementById('groupId').value = '';
        document.getElementById('deleteBookingBtn').style.display = 'none';
        document.getElementById('bookingModal').classList.add('show');
    }

    window.openAddModalAtDay = function(day) {
        openAddModal();
        const cb = document.querySelector(`input[name="bookingDays"][value="${day}"]`);
        if (cb) cb.checked = true;
    };

    function closeModal() {
        document.getElementById('bookingModal').classList.remove('show');
    }

    window.editBooking = function(id) {
        const b = allBookings.find(x => x.id == id);
        if (!b) return;
        document.getElementById('modalTitle').textContent = 'تعديل الحجز';
        document.getElementById('bookingId').value = b.id;
        document.querySelectorAll('input[name="bookingDays"]').forEach(cb => cb.checked = false);
        const bookingDays = b.days || (b.day ? [b.day] : []);
        bookingDays.forEach(d => {
            const cb = document.querySelector(`input[name="bookingDays"][value="${d}"]`);
            if (cb) cb.checked = true;
        });
        document.getElementById('startTime').value = b.startTime;
        document.getElementById('endTime').value = b.endTime;
        document.getElementById('hallId').value = b.hallId;
        document.getElementById('trainerId').value = b.trainerId;
        document.getElementById('groupId').value = b.groupId || '';
        document.getElementById('deleteBookingBtn').style.display = 'block';
        document.getElementById('bookingModal').classList.add('show');
    };

    async function saveBooking() {
        const days = Array.from(document.querySelectorAll('input[name="bookingDays"]:checked')).map(cb => cb.value);
        const startTime = document.getElementById('startTime').value;
        const endTime = document.getElementById('endTime').value;
        const hallId = document.getElementById('hallId').value;
        const trainerId = document.getElementById('trainerId').value;
        const groupId = document.getElementById('groupId').value;
        const id = document.getElementById('bookingId').value;

        if (!days.length) { showToast('يرجى اختيار يوم واحد على الأقل', 'warning'); return; }
        if (!startTime || !endTime) { showToast('يرجى تحديد وقت البداية والنهاية', 'warning'); return; }
        if (!hallId) { showToast('يرجى اختيار القاعة', 'warning'); return; }
        if (!trainerId) { showToast('يرجى اختيار المدرب', 'warning'); return; }
        if (startTime >= endTime) { showToast('وقت النهاية يجب أن يكون بعد وقت البداية', 'warning'); return; }

        // Validate half-hour intervals
        const [sm, em] = [startTime.split(':')[1], endTime.split(':')[1]];
        if (sm !== '00' && sm !== '30') { showToast('يرجى اختيار الوقت بأنصاف الساعات فقط (مثال 10:00 أو 10:30)', 'warning'); return; }
        if (em !== '00' && em !== '30') { showToast('يرجى اختيار الوقت بأنصاف الساعات فقط (مثال 10:00 أو 10:30)', 'warning'); return; }

        const bookingData = { id: id || undefined, days, startTime, endTime, hallId, trainerId, groupId, createdBy: currentUser.id };
        
        showLoading(true);
        try {
            const res = await apiCall('saveBooking', { bookingData });
            if (res.success !== false) {
                showToast(typeof res.message === 'string' ? res.message : 'تم الحفظ بنجاح', 'success');
                closeModal();
                loadData();
            } else {
                showToast(res.message || 'حدث خطأ', 'error');
            }
        } catch(e) {}
        showLoading(false);
    }

    async function deleteBooking() {
        const id = document.getElementById('bookingId').value;
        if (!id || !confirm('هل أنت متأكد من حذف هذا الحجز؟')) return;
        showLoading(true);
        try {
            await apiCall('deleteBooking', { bookingId: id });
            showToast('تم الحذف بنجاح', 'success');
            closeModal();
            loadData();
        } catch(e) {}
        showLoading(false);
    }
</script>

<script src="sidebar.js"></script>
</body>
</html>
"""

new_content = html_part + new_script

with open('schedule.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done - schedule.html rebuilt")
