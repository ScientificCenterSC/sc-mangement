import re

with open('code.gs', 'r', encoding='utf-8') as f:
    content = f.read()

new_saveBooking = '''function saveBooking(bookingData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Bookings");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!bookingData || (!bookingData.day && !bookingData.days) || !bookingData.startTime || !bookingData.endTime) {
    return { success: false, message: "بيانات الحجز غير مكتملة" };
  }
  
  var days = bookingData.days || [bookingData.day];
  var allBookings = getAllBookings();
  
  // Check for conflicts first
  var conflicts = [];
  for (var d = 0; d < days.length; d++) {
      var day = days[d];
      var tempBooking = {
          id: bookingData.id,
          hallId: bookingData.hallId,
          trainerId: bookingData.trainerId,
          day: day,
          startTime: bookingData.startTime,
          endTime: bookingData.endTime
      };
      var conflict = checkBookingConflict(tempBooking, allBookings);
      if (conflict) {
          conflicts.push(day);
      }
  }
  
  if (conflicts.length > 0) {
      return { success: false, message: "يوجد تعارض في المواعيد في الأيام التالية: " + conflicts.join("، ") + " - لم يتم حفظ الحجز." };
  }
  
  var createdCount = 0;
  
  if (bookingData.id) {
    var data = sheet.getDataRange().getValues();
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == bookingData.id) {
        sheet.getRange(i+1, 2).setValue(safeInt(bookingData.hallId, ''));
        sheet.getRange(i+1, 3).setValue(safeInt(bookingData.trainerId, ''));
        sheet.getRange(i+1, 4).setValue(safeInt(bookingData.groupId, ''));
        sheet.getRange(i+1, 5).setValue(days[0]);
        sheet.getRange(i+1, 6).setValue(bookingData.startTime);
        sheet.getRange(i+1, 7).setValue(bookingData.endTime);
        sheet.getRange(i+1, 9).setValue("OK");
        return { success: true, message: "تم تحديث الحجز بنجاح" };
      }
    }
  } else {
    var lastRow = sheet.getLastRow();
    for (var d = 0; d < days.length; d++) {
        var day = days[d];
        var newId = lastRow + d;
        sheet.getRange(lastRow + 1 + d, 1).setValue(newId);
        sheet.getRange(lastRow + 1 + d, 2).setValue(safeInt(bookingData.hallId, ''));
        sheet.getRange(lastRow + 1 + d, 3).setValue(safeInt(bookingData.trainerId, ''));
        sheet.getRange(lastRow + 1 + d, 4).setValue(safeInt(bookingData.groupId, ''));
        sheet.getRange(lastRow + 1 + d, 5).setValue(day);
        sheet.getRange(lastRow + 1 + d, 6).setValue(bookingData.startTime);
        sheet.getRange(lastRow + 1 + d, 7).setValue(bookingData.endTime);
        sheet.getRange(lastRow + 1 + d, 8).setValue(safeInt(bookingData.createdBy, 1));
        sheet.getRange(lastRow + 1 + d, 9).setValue("OK");
        createdCount++;
    }
    return { success: true, message: "تم الحجز بنجاح لعدد " + createdCount + " أيام" };
  }
  
  return { success: false, message: "حدث خطأ" };
}

function checkBookingConflict(newBooking, existingBookings) {
  for (var b = 0; b < existingBookings.length; b++) {
    var booking = existingBookings[b];
    if (booking.id == newBooking.id) continue;
    if (booking.day === newBooking.day) {
      if (booking.hallId == newBooking.hallId || booking.trainerId == newBooking.trainerId) {
        if ((newBooking.startTime >= booking.startTime && newBooking.startTime < booking.endTime) ||
            (newBooking.endTime > booking.startTime && newBooking.endTime <= booking.endTime) ||
            (newBooking.startTime <= booking.startTime && newBooking.endTime >= booking.endTime)) {
          return true;
        }
      }
    }
  }
  return false;
}'''

content = re.sub(r'function saveBooking\(bookingData\) \{.*?(?=function deleteBooking)', new_saveBooking + '\n\n', content, flags=re.DOTALL)

with open('code.gs', 'w', encoding='utf-8') as f:
    f.write(content)
