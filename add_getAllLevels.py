import re

with open('code.gs', 'r', encoding='utf-8') as f:
    content = f.read()

new_fn = '''
function getAllLevels() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Levels");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var levels = [];
  for (var i = 1; i < data.length; i++) {
    levels.push({
      id: data[i][0],
      studentId: data[i][1],
      levelNumber: data[i][2],
      levelFee: data[i][3],
      status: data[i][4],
      studentName: data[i][5]
    });
  }
  return levels;
}
'''

content = content.replace("function handleApiRequestGet(params) {", "function handleApiRequestGet(params) {\n  var action = params.action;\n  if (action === 'getAllLevels') return { success: true, data: getAllLevels() };")
content = content.replace("function handleApiRequestPost(action, params) {", "function handleApiRequestPost(action, params) {\n  if (action === 'getAllLevels') return { success: true, data: getAllLevels() };")

content += new_fn

with open('code.gs', 'w', encoding='utf-8') as f:
    f.write(content)
