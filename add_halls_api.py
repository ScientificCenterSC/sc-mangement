import re

with open('code.gs', 'r', encoding='utf-8') as f:
    content = f.read()

new_fns = '''
function saveHall(hallData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Halls");
  if (!sheet) return { success: false, message: "Sheet not found" };
  if (!hallData || !hallData.name) return { success: false, message: "اسم القاعة مطلوب" };
  
  var data = sheet.getDataRange().getValues();
  if (hallData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == hallData.id) {
        sheet.getRange(i+1, 2).setValue(hallData.name);
        sheet.getRange(i+1, 3).setValue(safeInt(hallData.floorId, 1));
        sheet.getRange(i+1, 4).setValue(hallData.type || 'theory');
        sheet.getRange(i+1, 5).setValue(safeInt(hallData.capacity, 20));
        sheet.getRange(i+1, 6).setValue(hallData.status || 'Active');
        return { success: true, message: "تم التحديث بنجاح" };
      }
    }
  } else {
    var newId = sheet.getLastRow();
    sheet.getRange(newId + 1, 1).setValue(newId);
    sheet.getRange(newId + 1, 2).setValue(hallData.name);
    sheet.getRange(newId + 1, 3).setValue(safeInt(hallData.floorId, 1));
    sheet.getRange(newId + 1, 4).setValue(hallData.type || 'theory');
    sheet.getRange(newId + 1, 5).setValue(safeInt(hallData.capacity, 20));
    sheet.getRange(newId + 1, 6).setValue(hallData.status || 'Active');
    return { success: true, message: "تمت الإضافة بنجاح" };
  }
  return { success: false, message: "القاعة غير موجودة" };
}

function deleteHall(hallId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Halls");
  if (!sheet) return { success: false, message: "Sheet not found" };
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == hallId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم الحذف بنجاح" };
    }
  }
  return { success: false, message: "القاعة غير موجودة" };
}
'''

content = content.replace("function handleApiRequestPost(action, params) {", "function handleApiRequestPost(action, params) {\n  if (action === 'saveHall') return saveHall(params.hallData);\n  if (action === 'deleteHall') return deleteHall(params.id);")

content += new_fns

with open('code.gs', 'w', encoding='utf-8') as f:
    f.write(content)
