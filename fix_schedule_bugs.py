import re

with open('schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update time slots to 12-hour format with AM/PM (9:00 AM to 10:00 PM)
time_slots_logic = '''
    const timeSlots = [];
    for (let i = 9; i <= 22; i++) {
        let suffix = i >= 12 ? 'PM' : 'AM';
        let displayHour = i > 12 ? i - 12 : i;
        let time24 = `${i.toString().padStart(2, '0')}:00`;
        let displayTime = `${displayHour}:00 ${suffix}`;
        timeSlots.push({ time24, displayTime });
    }
'''
content = re.sub(r'const timeSlots = \[\];\s*for \(let i = 9; i <= 22; i\+\+\) \{\s*timeSlots\.push\([^)]+\);\s*\}', time_slots_logic, content)

# Update header rendering
content = content.replace('for (let time of timeSlots) {', 'for (let slot of timeSlots) {\n            let time = slot.time24; // Use 24h for logic, display 12h\n            let displayTime = slot.displayTime;')
content = content.replace('>${time}</th>', '>${displayTime}</th>')

# 2. Add deptFilter logic to renderBoard
render_board_filter = '''
        const hallFilter = document.getElementById('hallFilter').value;
        const trainerFilter = document.getElementById('trainerFilter').value;
        const deptFilter = document.getElementById('deptFilter').value;
        const visibleFloors = getVisibleFloors();
        
        let filteredBookings = [...allBookings];
        // Filter out bookings for floors user doesn't have access to
        filteredBookings = filteredBookings.filter(b => {
            const hall = allHalls.find(h => h.id == b.hallId);
            return hall && visibleFloors.some(f => f.id == hall.floorNumber);
        });
        
        if (hallFilter !== 'all') filteredBookings = filteredBookings.filter(b => b.hallId == hallFilter);
        if (trainerFilter !== 'all') filteredBookings = filteredBookings.filter(b => b.trainerId == trainerFilter);
        if (deptFilter !== 'all') {
            filteredBookings = filteredBookings.filter(b => {
                const trainer = allTrainers.find(t => t.id == b.trainerId);
                return trainer && trainer.department == deptFilter;
            });
        }
'''
content = re.sub(r'const hallFilter.*?;.*?if \(trainerFilter !== \'all\'\).*?;', render_board_filter, content, flags=re.DOTALL)

# 3. Update openAddModalAtDay and openAddModalAtSlot and editBooking
js_modals = '''
    function openAddModalAtDay(day) {
        openAddModal();
        let cb = document.querySelector(`input[name="bookingDays"][value="${day}"]`);
        if (cb) cb.checked = true;
    }

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


    function openAddModalAtSlot(day, floorId) {
        document.getElementById('modalTitle').textContent = 'حجز جديد';
        document.getElementById('bookingForm').reset();
        document.getElementById('bookingId').value = '';
        document.querySelectorAll('input[name="bookingDays"]').forEach(cb => cb.checked = false);
        let cb = document.querySelector(`input[name="bookingDays"][value="${day}"]`);
        if (cb) cb.checked = true;
        
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
        document.querySelectorAll('input[name="bookingDays"]').forEach(cb => cb.checked = false);
        // If the booking has days array (new schema)
        if (booking.days && Array.isArray(booking.days)) {
            booking.days.forEach(d => {
                let cb = document.querySelector(`input[name="bookingDays"][value="${d}"]`);
                if (cb) cb.checked = true;
            });
        } else if (booking.day) {
            // Old schema compatibility
            let cb = document.querySelector(`input[name="bookingDays"][value="${booking.day}"]`);
            if (cb) cb.checked = true;
        }
        document.getElementById('startTime').value = booking.startTime;
        document.getElementById('endTime').value = booking.endTime;
        document.getElementById('hallId').value = booking.hallId;
        document.getElementById('trainerId').value = booking.trainerId;
        document.getElementById('groupId').value = booking.groupId || '';
        document.getElementById('deleteBookingBtn').style.display = 'block';
        document.getElementById('bookingModal').classList.add('show');
    }
'''
content = re.sub(r'function openAddModalAtDay\(day\) \{.*?function closeModal\(\) \{', js_modals + '\n    function closeModal() {', content, flags=re.DOTALL)

with open('schedule.html', 'w', encoding='utf-8') as f:
    f.write(content)
