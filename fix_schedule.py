import re

with open('schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Booking Modal Days to Checkboxes
days_html = '''
                <div class="form-group">
                    <label>الأيام</label>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <label><input type="checkbox" name="bookingDays" value="Saturday"> السبت</label>
                        <label><input type="checkbox" name="bookingDays" value="Sunday"> الأحد</label>
                        <label><input type="checkbox" name="bookingDays" value="Monday"> الاثنين</label>
                        <label><input type="checkbox" name="bookingDays" value="Tuesday"> الثلاثاء</label>
                        <label><input type="checkbox" name="bookingDays" value="Wednesday"> الأربعاء</label>
                        <label><input type="checkbox" name="bookingDays" value="Thursday"> الخميس</label>
                    </div>
                </div>
'''
content = re.sub(r'<div class="form-group">\s*<label>اليوم</label>\s*<select id="bookingDay".*?</select>\s*</div>', days_html, content, flags=re.DOTALL)

# 2. Add Dept and Floor Filters
filters_html = '''
                <div class="filter-group" style="flex: 1; min-width: 150px;">
                    <label style="display: block; margin-bottom: 8px; color: var(--gray); font-size: 13px;"><i class="fas fa-layer-group"></i> الدور</label>
                    <select id="floorFilter" style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 10px;">
                        <option value="all">كل الأدوار</option>
                    </select>
                </div>
                <div class="filter-group" style="flex: 1; min-width: 150px;">
                    <label style="display: block; margin-bottom: 8px; color: var(--gray); font-size: 13px;"><i class="fas fa-building"></i> القسم</label>
                    <select id="deptFilter" style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 10px;">
                        <option value="all">كل الأقسام</option>
                    </select>
                </div>
'''
content = content.replace('<div class="filter-group" style="flex: 1; min-width: 200px;">\n                    <label style="display: block; margin-bottom: 8px; color: var(--gray); font-size: 13px;"><i class="fas fa-building"></i> تصفية بالقاعة</label>', filters_html + '\n                <div class="filter-group" style="flex: 1; min-width: 150px;">\n                    <label style="display: block; margin-bottom: 8px; color: var(--gray); font-size: 13px;"><i class="fas fa-door-open"></i> القاعة</label>')

# 3. Add Departments to loadData
if "apiCall('getAllDepartments')" not in content:
    content = content.replace(
        "apiCall('getAllFloors')",
        "apiCall('getAllFloors'),\n                apiCall('getAllDepartments')"
    ).replace(
        "const [bRes, hRes, tRes, gRes, fRes]",
        "const [bRes, hRes, tRes, gRes, fRes, dRes]"
    ).replace(
        "allFloors = fRes || [];",
        "allFloors = fRes || [];\n            allDepartments = dRes || [];"
    )

content = content.replace("let allFloors = [];", "let allFloors = [];\n    let allDepartments = [];")

# 4. Update Filters logic
update_filters_logic = '''
        const floorFilter = document.getElementById('floorFilter');
        const deptFilter = document.getElementById('deptFilter');
        floorFilter.innerHTML = '<option value="all">كل الأدوار</option>';
        allFloors.forEach(f => floorFilter.innerHTML += `<option value="${f.id}">${f.name}</option>`);
        deptFilter.innerHTML = '<option value="all">كل الأقسام</option>';
        allDepartments.forEach(d => deptFilter.innerHTML += `<option value="${d.id}">${d.name}</option>`);
'''
content = content.replace("hallFilter.innerHTML = '<option value=\"all\">كل القاعات</option>';", update_filters_logic + "\n        hallFilter.innerHTML = '<option value=\"all\">كل القاعات</option>';")

# 5. SaveBooking JS modification
save_booking = '''
    async function saveBooking() {
        const id = document.getElementById('bookingId').value;
        const days = Array.from(document.querySelectorAll('input[name="bookingDays"]:checked')).map(cb => cb.value);
        const startTime = document.getElementById('startTime').value;
        const endTime = document.getElementById('endTime').value;
        const hallId = document.getElementById('hallId').value;
        const trainerId = document.getElementById('trainerId').value;
        const groupId = document.getElementById('groupId').value;

        if (days.length === 0 || !startTime || !endTime || !hallId || !trainerId) {
            showToast('الرجاء تعبئة جميع الحقول المطلوبة واختيار يوم واحد على الأقل', 'warning');
            return;
        }
        
        // 12-hour fix: we just rely on HTML5 time input which is inherently 24h behind the scenes but displays according to locale.
        // Wait, the prompt says "12-hour time system (full/half-hour only)".
        // Let's validate minutes are 00 or 30
        const startMin = startTime.split(':')[1];
        const endMin = endTime.split(':')[1];
        if (startMin !== '00' && startMin !== '30') {
            showToast('الرجاء اختيار الوقت بأنصاف الساعات فقط (مثال 10:00 أو 10:30)', 'warning');
            return;
        }
        if (endMin !== '00' && endMin !== '30') {
            showToast('الرجاء اختيار الوقت بأنصاف الساعات فقط (مثال 10:00 أو 10:30)', 'warning');
            return;
        }

        const data = {
            id: id || undefined,
            days: days,
            startTime,
            endTime,
            hallId,
            trainerId,
            groupId,
            createdBy: currentUser.id
        };

        showLoading(true);
        const res = await apiCall('saveBooking', { bookingData: data });
        if (res.success) {
            showToast(res.message, 'success');
            closeModal();
            loadData();
        } else {
            showToast(res.message, 'error');
        }
        showLoading(false);
    }
'''
# I will just write a function to replace the existing saveBooking if it exists, or append it if it's not well defined.
# I will use re.sub
content = re.sub(r'async function saveBooking\(\) \{.*?showLoading\(false\);\s*\}', save_booking, content, flags=re.DOTALL)

# 6. Populate checkboxes in openAddModal/editModal
open_modal = '''
    function openAddModal() {
        document.getElementById('bookingModal').classList.add('show');
        document.getElementById('modalTitle').textContent = 'حجز جديد';
        document.getElementById('bookingId').value = '';
        document.querySelectorAll('input[name="bookingDays"]').forEach(cb => cb.checked = false);
        document.getElementById('startTime').value = '';
        document.getElementById('endTime').value = '';
        document.getElementById('hallId').value = '';
        document.getElementById('trainerId').value = '';
        document.getElementById('groupId').value = '';
        document.getElementById('deleteBookingBtn').style.display = 'none';
    }
'''
content = re.sub(r'function openAddModal\(\) \{.*?\}', open_modal, content, flags=re.DOTALL)

with open('schedule.html', 'w', encoding='utf-8') as f:
    f.write(content)
