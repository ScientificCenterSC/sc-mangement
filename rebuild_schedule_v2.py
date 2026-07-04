with open('schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.index('<script>')
html_part = content[:idx]

# Fix the modal - replace time inputs with dropdowns
old_time_inputs = '''                <div class="form-row">
                    <div class="form-group">
                        <label>من الساعة</label>
                        <input type="time" id="startTime" required>
                    </div>
                    <div class="form-group">
                        <label>إلى الساعة</label>
                        <input type="time" id="endTime" required>
                    </div>
                </div>'''

new_time_selects = '''                <div class="form-row">
                    <div class="form-group">
                        <label>من الساعة</label>
                        <select id="startTime" required style="width:100%;padding:10px 12px;border:2px solid #e9ecef;border-radius:10px;font-family:inherit;">
                            <option value="">اختر وقت البداية...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>إلى الساعة</label>
                        <select id="endTime" required style="width:100%;padding:10px 12px;border:2px solid #e9ecef;border-radius:10px;font-family:inherit;">
                            <option value="">اختر وقت النهاية...</option>
                        </select>
                    </div>
                </div>'''

html_part = html_part.replace(old_time_inputs, new_time_selects)

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

    // Time slots 9 AM to 10 PM with 30-min intervals
    const timeSlots = [];
    for (let i = 9; i <= 22; i++) {
        for (let m of [0, 30]) {
            if (i === 22 && m === 30) continue;
            const h12 = i > 12 ? i - 12 : i;
            const suffix = i >= 12 ? 'م' : 'ص';
            const minStr = m === 0 ? '00' : '30';
            timeSlots.push({
                time24: `${String(i).padStart(2,'0')}:${minStr}`,
                display: `${h12}:${minStr} ${suffix}`
            });
        }
    }
    // Board only shows full hours
    const boardSlots = timeSlots.filter(s => s.time24.endsWith(':00'));

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

        // Populate time dropdowns
        const startSel = document.getElementById('startTime');
        const endSel = document.getElementById('endTime');
        timeSlots.forEach(s => {
            startSel.innerHTML += `<option value="${s.time24}">${s.display}</option>`;
            endSel.innerHTML += `<option value="${s.time24}">${s.display}</option>`;
        });

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
        allHalls.forEach(h => {
            const floor = allFloors.find(f => f.id == h.floorNumber);
            hallSelect.innerHTML += `<option value="${h.id}">${h.name}${floor ? ' - ' + floor.name : ''}</option>`;
        });

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

        // Header - full hours for display
        let headerHtml = '<tr><th style="padding:15px;background:var(--dark-blue);color:white;border:1px solid #334;width:120px;position:sticky;right:0;z-index:10;">اليوم / الوقت</th>';
        for (const slot of boardSlots) {
            headerHtml += `<th style="padding:10px;background:var(--dark-blue);color:white;border:1px solid #334;text-align:center;min-width:160px;font-size:13px;">${slot.display}</th>`;
        }
        headerHtml += '</tr>';
        header.innerHTML = headerHtml;

        const floorColors = ['#e3f2fd','#fce4ec','#e8f5e9','#fff3e0','#f3e5f5','#e8eaf6'];
        const floorBorderColors = ['#1565c0','#c62828','#2e7d32','#e65100','#6a1b9a','#283593'];

        let bodyHtml = '';
        for (const day of daysOfWeek) {
            let rowHtml = `<tr>
                <td style="padding:12px;background:linear-gradient(135deg,#f8f9fa,#e9ecef);border:1px solid #dee2e6;text-align:center;position:sticky;right:0;z-index:9;min-width:100px;">
                    <div style="color:var(--dark-blue);font-weight:800;font-size:15px;">${daysNames[day]}</div>
                    <button onclick="openAddModalAtDay('${day}')" style="margin-top:6px;background:transparent;border:1px dashed #aaa;color:#777;padding:3px 8px;width:100%;border-radius:6px;cursor:pointer;font-size:11px;transition:all 0.2s;" onmouseover="this.style.borderColor='var(--primary-blue)'" onmouseout="this.style.borderColor='#aaa'">
                        <i class="fas fa-plus"></i> حجز
                    </button>
                </td>`;
            
            for (const slot of boardSlots) {
                const time = slot.time24;
                let cellContent = '';

                // Check bookings that fall in this hour slot
                for (let i = 0; i < allFloors.length; i++) {
                    const floor = allFloors[i];
                    const floorColor = floorColors[i % floorColors.length];
                    const borderColor = floorBorderColors[i % floorBorderColors.length];

                    const floorBookings = filteredBookings.filter(b => {
                        const hall = allHalls.find(h => h.id == b.hallId);
                        // hall.floorNumber is the field from code.gs
                        if (!hall || hall.floorNumber != floor.id) return false;
                        const bookingDays = b.days || (b.day ? [b.day] : []);
                        if (!bookingDays.includes(day)) return false;
                        // Check time overlap: booking covers this hour slot
                        return b.startTime <= time && b.endTime > time;
                    });

                    if (floorBookings.length > 0) {
                        cellContent += `<div style="background:${floorColor};border-right:4px solid ${borderColor};padding:7px 8px;margin-bottom:5px;border-radius:8px;font-size:11px;box-shadow:0 2px 4px rgba(0,0,0,0.08);">
                            <div style="font-weight:800;color:${borderColor};margin-bottom:4px;border-bottom:1px solid rgba(0,0,0,0.08);padding-bottom:3px;">
                                <i class="fas fa-layer-group"></i> ${floor.name}
                            </div>`;
                        for (const b of floorBookings) {
                            const trainer = allTrainers.find(t => t.id == b.trainerId);
                            const hall = allHalls.find(h => h.id == b.hallId);
                            const group = allGroups.find(g => g.id == b.groupId);
                            const dept = trainer ? allDepartments.find(d => d.id == trainer.deptId) : null;
                            cellContent += `<div onclick="editBooking(${b.id})" style="cursor:pointer;background:rgba(255,255,255,0.85);padding:6px 8px;margin-top:4px;border-radius:6px;transition:all 0.15s;border:1px solid rgba(0,0,0,0.06);" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                                <div style="font-weight:700;color:#1a2a6c;margin-bottom:3px;">
                                    <i class="fas fa-clock" style="color:${borderColor}"></i> ${b.startTime} - ${b.endTime}
                                </div>
                                <div style="color:#444;margin-bottom:2px;"><i class="fas fa-door-open" style="color:${borderColor};width:14px;"></i> <strong>${hall?.name || '-'}</strong>${hall ? ' (سعة: '+hall.capacity+')' : ''}</div>
                                <div style="color:#444;margin-bottom:2px;"><i class="fas fa-user-tie" style="color:${borderColor};width:14px;"></i> ${trainer?.name || '-'}</div>
                                ${dept ? `<div style="color:#666;font-size:10px;"><i class="fas fa-building" style="width:14px;"></i> ${dept.name}</div>` : ''}
                                ${group ? `<div style="color:#666;font-size:10px;"><i class="fas fa-users" style="width:14px;"></i> ${group.name}</div>` : ''}
                            </div>`;
                        }
                        cellContent += '</div>';
                    }
                }

                const isEmpty = !cellContent;
                rowHtml += `<td style="padding:8px;border:1px solid #e8eaf0;vertical-align:top;background:${isEmpty ? 'white' : '#fafbff'};min-height:80px;transition:background 0.2s;" onmouseover="if(!this.querySelector('div')) this.style.background='#f0f4ff'" onmouseout="this.style.background=''">
                    ${cellContent || '<div style="height:40px;"></div>'}
                </td>`;
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
        if (!startTime) { showToast('يرجى اختيار وقت البداية', 'warning'); return; }
        if (!endTime) { showToast('يرجى اختيار وقت النهاية', 'warning'); return; }
        if (!hallId) { showToast('يرجى اختيار القاعة', 'warning'); return; }
        if (!trainerId) { showToast('يرجى اختيار المدرب', 'warning'); return; }
        if (startTime >= endTime) { showToast('وقت النهاية يجب أن يكون بعد وقت البداية', 'warning'); return; }

        const bookingData = { id: id || undefined, days, startTime, endTime, hallId, trainerId, groupId, createdBy: currentUser.id };
        
        showLoading(true);
        try {
            const res = await apiCall('saveBooking', { bookingData });
            const isSuccess = res && res.success !== false;
            showToast(res.message || (isSuccess ? 'تم الحفظ بنجاح' : 'حدث خطأ'), isSuccess ? 'success' : 'error');
            if (isSuccess) { closeModal(); loadData(); }
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

print("Done - schedule.html rebuilt with fixed board and time dropdowns")
