import re

with open('code.gs', 'r', encoding='utf-8') as f:
    content = f.read()

# Append updateSystemSafely to code.gs
if "function updateSystemSafely()" not in content:
    update_func = """

function updateSystemSafely() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const requiredSheets = [
    "Roles", "Permissions", "RolePermissions", "Users",
    "Settings", "Departments", "Floors", "Halls",
    "Courses", "AddOns", "Trainers", "Groups",
    "Students", "Bookings", "Payments", "Levels"
  ];
  
  var sheetsObj = {};
  requiredSheets.forEach(name => {
    let sheet = ss.getSheetByName(name);
    if (!sheet) {
      sheet = ss.insertSheet(name);
    }
    sheetsObj[name] = sheet;
  });
  
  createTableSchemas(sheetsObj);
  
  // Also insert seed data ONLY for missing things (optional, but let's just do it manually if needed)
  // Actually, let's just update headers. Data shouldn't be touched automatically here to avoid wiping.
}
"""
    content += update_func

    with open('code.gs', 'w', encoding='utf-8') as f:
        f.write(content)
