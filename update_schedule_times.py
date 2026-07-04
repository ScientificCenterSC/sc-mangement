import os

filepath = "c:/Users/shahd/Downloads/ss/schedule.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the renderBoard function and its related HTML
js_start = content.find('function renderBoard() {')
js_end = content.find('function openAddModal() {', js_start)

new_js = """
    const timeSlots = [];
    for (let i = 9; i <= 22; i++) {
        timeSlots.push(`${i.toString().padStart(2, '0')}:00`);
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
        
        // Render Header (Time Slots)
        let headerHtml = `<tr>
            <th style="padding: 15px; background: var(--dark-blue); color: white; border: 1px solid #dee2e6; width: 120px; position: sticky; right: 0; z-index: 10;">اليوم / المواعيد</th>
        `;
        for (let time of timeSlots) {
            headerHtml += `<th style="padding: 10px; background: var(--dark-blue); color: white; border: 1px solid #dee2e6; text-align: center; min-width: 150px;">${time}</th>`;
        }
        headerHtml += `</tr>`;
        header.innerHTML = headerHtml;
        
        // Define floor colors
        const floorColors = ['#e3f2fd', '#fce4ec', '#e8f5e9', '#fff3e0', '#f3e5f5'];
        const floorBorderColors = ['#2196f3', '#e91e63', '#4caf50', '#ff9800', '#9c27b0'];
        
        // Render Body (Days)
        let bodyHtml = '';
        for (let day of daysOfWeek) {
            let rowHtml = `<tr>
                <td style="padding: 15px; background: #f8f9fa; border: 1px solid #dee2e6; font-weight: bold; text-align: center; position: sticky; right: 0; z-index: 9; box-shadow: -2px 0 5px rgba(0,0,0,0.02);">
                    <div style="font-size: 16px; color: var(--primary-blue);">${daysNames[day]}</div>
                    <button onclick="openAddModalAtDay('${day}')" style="margin-top: 10px; background: transparent; border: 1px dashed #ccc; color: var(--gray); padding: 5px; width: 100%; border-radius: 8px; cursor: pointer; transition: all 0.2s; font-size: 11px;">
                        <i class="fas fa-plus"></i> إضافة
                    </button>
                </td>
            `;
            
            for (let time of timeSlots) {
                let cellContent = '';
                
                // For this [Day, Time], group by Floor
                for (let i = 0; i < visibleFloors.length; i++) {
                    let floor = visibleFloors[i];
                    let floorColor = floorColors[i % floorColors.length];
                    let borderColor = floorBorderColors[i % floorBorderColors.length];
                    
                    let floorBookings = filteredBookings.filter(b => {
                        const hall = allHalls.find(h => h.id == b.hallId);
                        // Simple time overlap check
                        return b.day === day && hall && hall.floorNumber == floor.id && (b.startTime <= time && b.endTime > time);
                    });
                    
                    if (floorBookings.length > 0) {
                        cellContent += `<div style="background: ${floorColor}; border-right: 4px solid ${borderColor}; padding: 6px; margin-bottom: 6px; border-radius: 6px; font-size: 11px; color: var(--dark);">`;
                        cellContent += `<div style="font-weight: bold; margin-bottom: 4px; border-bottom: 1px solid rgba(0,0,0,0.05); padding-bottom: 2px;">${floor.name}</div>`;
                        
                        for (let booking of floorBookings) {
                            const trainer = allTrainers.find(t => t.id === booking.trainerId);
                            const hall = allHalls.find(h => h.id === booking.hallId);
                            const isConflict = booking.conflict === 'CONFLICT';
                            const conflictAlert = isConflict ? `<i class="fas fa-exclamation-triangle" style="color: var(--danger);" title="تعارض"></i> ` : '';
                            
                            cellContent += `
                                <div onclick="editBooking(${booking.id})" style="cursor: pointer; background: rgba(255,255,255,0.7); padding: 4px; margin-top: 4px; border-radius: 4px; transition: transform 0.1s;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                                    <div style="font-weight: bold;">${conflictAlert}${booking.startTime} - ${booking.endTime}</div>
                                    <div><i class="fas fa-door-open"></i> ${hall?.name || '-'}</div>
                                    <div><i class="fas fa-user-tie"></i> ${trainer?.name || '-'}</div>
                                </div>
                            `;
                        }
                        cellContent += `</div>`;
                    }
                }
                
                rowHtml += `<td style="padding: 10px; border: 1px solid #dee2e6; vertical-align: top; background: white; min-height: 100px;">${cellContent}</td>`;
            }
            rowHtml += `</tr>`;
            bodyHtml += rowHtml;
        }
        body.innerHTML = bodyHtml;
    }
    
    function openAddModalAtDay(day) {
        openAddModal();
        document.getElementById('bookingDay').value = day;
    }
"""
content = content[:js_start] + new_js + content[js_end:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated schedule times table")
