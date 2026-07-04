import re

with open('code.gs', 'r', encoding='utf-8') as f:
    content = f.read()

new_getAllPayments = '''function getAllPayments() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Payments");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  
  // Build student name lookup map to avoid N+1 queries
  var studentNames = {};
  var studentsSheet = ss.getSheetByName("Students");
  if (studentsSheet) {
    var sData = studentsSheet.getDataRange().getValues();
    for (var j = 1; j < sData.length; j++) {
      studentNames[sData[j][0]] = sData[j][2];
    }
  }
  
  var payments = [];
  for (var i = 1; i < data.length; i++) {
    payments.push({
      id: data[i][0],
      studentId: data[i][1],
      studentName: studentNames[data[i][1]] || '',
      levelNumber: data[i][2],
      paymentType: data[i][3],
      amountPaid: data[i][4],
      discountAmount: data[i][5],
      totalFee: data[i][6],
      remainingBalance: data[i][7],
      notes: data[i][8],
      paymentDate: data[i][9],
      createdBy: data[i][10]
    });
  }
  return payments;
}

function savePayment(paymentData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Payments");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var studentId = safeInt(paymentData.studentId, 0);
  var levelNumber = safeInt(paymentData.levelNumber, 1);
  var paymentType = paymentData.paymentType || 'Course Payment';
  var amountPaid = safeFloat(paymentData.amountPaid, 0);
  var discountAmount = safeFloat(paymentData.discountAmount, 0);
  var totalLevelFee = safeFloat(paymentData.totalLevelFee || paymentData.totalFee, 0);
  var notes = paymentData.notes || '';
  
  if (!studentId || (amountPaid <= 0 && discountAmount <= 0)) {
    return { success: false, message: "بيانات الدفع غير صالحة" };
  }
  
  var data = sheet.getDataRange().getValues();
  var prevTotalPaid = 0;
  var prevTotalDiscount = 0;
  
  if (paymentData.id) {
      for (var i = 1; i < data.length; i++) {
        if (data[i][1] == studentId && data[i][2] == levelNumber && data[i][3] == paymentType && data[i][0] != paymentData.id) {
          prevTotalPaid += safeFloat(data[i][4], 0);
          prevTotalDiscount += safeFloat(data[i][5], 0);
        }
      }
  } else {
      for (var i = 1; i < data.length; i++) {
        if (data[i][1] == studentId && data[i][2] == levelNumber && data[i][3] == paymentType) {
          prevTotalPaid += safeFloat(data[i][4], 0);
          prevTotalDiscount += safeFloat(data[i][5], 0);
        }
      }
  }
  
  var currentTotalPaid = prevTotalPaid + amountPaid;
  var currentTotalDiscount = prevTotalDiscount + discountAmount;
  var remainingBalance = totalLevelFee - currentTotalPaid - currentTotalDiscount;
  if (remainingBalance < 0) remainingBalance = 0;
  
  if (paymentData.id) {
      for (var i = 1; i < data.length; i++) {
          if (data[i][0] == paymentData.id) {
              sheet.getRange(i+1, 2).setValue(studentId);
              sheet.getRange(i+1, 3).setValue(levelNumber);
              sheet.getRange(i+1, 4).setValue(paymentType);
              sheet.getRange(i+1, 5).setValue(amountPaid);
              sheet.getRange(i+1, 6).setValue(discountAmount);
              sheet.getRange(i+1, 7).setValue(totalLevelFee);
              sheet.getRange(i+1, 8).setValue(remainingBalance);
              sheet.getRange(i+1, 9).setValue(notes);
              
              updateLevelsTable(studentId, levelNumber, totalLevelFee, remainingBalance);
              return { success: true, message: "تم تحديث الدفعة بنجاح" };
          }
      }
  } else {
      var lastRow = sheet.getLastRow();
      var newId = lastRow;
      
      sheet.getRange(lastRow + 1, 1).setValue(newId);
      sheet.getRange(lastRow + 1, 2).setValue(studentId);
      sheet.getRange(lastRow + 1, 3).setValue(levelNumber);
      sheet.getRange(lastRow + 1, 4).setValue(paymentType);
      sheet.getRange(lastRow + 1, 5).setValue(amountPaid);
      sheet.getRange(lastRow + 1, 6).setValue(discountAmount);
      sheet.getRange(lastRow + 1, 7).setValue(totalLevelFee);
      sheet.getRange(lastRow + 1, 8).setValue(remainingBalance);
      sheet.getRange(lastRow + 1, 9).setValue(notes);
      sheet.getRange(lastRow + 1, 10).setValue(paymentData.paymentDate || new Date());
      sheet.getRange(lastRow + 1, 11).setValue(safeInt(paymentData.createdBy, 1));
  }
  
  updateLevelsTable(studentId, levelNumber, totalLevelFee, remainingBalance);
  
  return { success: true, message: "تم تسجيل الدفعة بنجاح" };
}'''

content = re.sub(r'function getAllPayments\(\) \{.*?(?=function updateLevelsTable)', new_getAllPayments + '\n\n', content, flags=re.DOTALL)

new_getFinancialSummary = '''function getFinancialSummary() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var paymentsSheet = ss.getSheetByName("Payments");
  var totalPaid = 0;
  
  if (paymentsSheet) {
      var payments = paymentsSheet.getDataRange().getValues();
      for (var i = 1; i < payments.length; i++) {
        totalPaid += safeFloat(payments[i][4], 0);
      }
  }
  
  var studentsSheet = ss.getSheetByName("Students");
  var studentCount = studentsSheet ? Math.max(studentsSheet.getLastRow() - 1, 0) : 0;
  var trainersSheet = ss.getSheetByName("Trainers");
  var bookingsSheet = ss.getSheetByName("Bookings");
  
  return {
    totalPaid: totalPaid,
    totalRemaining: 0, // Simplified for now since we have multiple payment types
    studentCount: studentCount,
    trainerCount: trainersSheet ? Math.max(trainersSheet.getLastRow() - 1, 0) : 0,
    bookingCount: bookingsSheet ? Math.max(bookingsSheet.getLastRow() - 1, 0) : 0
  };
}'''

content = re.sub(r'function getFinancialSummary\(\) \{.*?(?=// \-{10} TRAINERS \-{10})', new_getFinancialSummary + '\n\n', content, flags=re.DOTALL)

with open('code.gs', 'w', encoding='utf-8') as f:
    f.write(content)
