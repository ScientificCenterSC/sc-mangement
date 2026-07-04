import re

with open('code.gs', 'r', encoding='utf-8') as f:
    content = f.read()

new_insert = '''function insertSeedData(sheets) {
  // --- Roles (5 columns) ---
  sheets.Roles.getRange(2,1,2,5).setValues([
    [1, "Super Admin", "Full system access with all permissions", "Active", "1,2,3,4"],
    [2, "Admin", "Administrative access", "Active", "1,2,3,4"]
  ]);
  
  // --- Floors (4 columns) ---
  sheets.Floors.getRange(2,1,2,4).setValues([
    [1, "Floor 1", "#4a8fe0", "Active"],
    [2, "Floor 2", "#2ecc71", "Active"]
  ]);
  
  // --- Users (9 columns) ---
  sheets.Users.getRange(2,1,2,9).setValues([
    [1, "admin", "admin123", "Ahmed Mansour", "0100112233", 1, true, new Date(), "admin@sc.com"],
    [2, "accountant", "acc123", "Mona El Sayed", "0100445566", 2, true, new Date(), "mona@sc.com"]
  ]);
  
  // --- Permissions (4 columns) - keep all 23 so system works ---
  var permissions = [
    [1, "users", "view", "View Users"], [2, "users", "edit", "Manage Users"],
    [3, "courses", "view", "View Courses"], [4, "courses", "edit", "Manage Courses"],
    [5, "students", "view", "View Students"], [6, "students", "edit", "Manage Students"],
    [7, "payments", "view", "View Payments"], [8, "payments", "edit", "Manage Payments"],
    [9, "reports", "view", "View Reports"], [10, "reports", "edit", "Export/Manage Reports"],
    [11, "settings", "view", "View Settings"], [12, "settings", "edit", "Manage Settings"],
    [13, "trainers", "view", "View Trainers"], [14, "trainers", "edit", "Manage Trainers"],
    [15, "schedule", "view", "View Schedule"], [16, "schedule", "edit", "Manage Schedule"],
    [17, "roles", "view", "View Roles"], [18, "roles", "edit", "Manage Roles"],
    [19, "departments", "view", "View Departments"], [20, "departments", "edit", "Manage Departments"],
    [21, "floors", "view", "View Floors"], [22, "floors", "edit", "Manage Floors"],
    [23, "dashboard", "view", "View Dashboard"]
  ];
  sheets.Permissions.getRange(2,1,permissions.length,4).setValues(permissions);
  
  // --- RolePermissions: Super Admin gets ALL permissions ---
  var rolePerms = [];
  for (var i = 1; i <= permissions.length; i++) {
    rolePerms.push([i, 1, i]); 
  }
  sheets.RolePermissions.getRange(2,1,rolePerms.length,3).setValues(rolePerms);
  
  // --- Settings (3 columns) ---
  sheets.Settings.getRange(2,1,6,3).setValues([
    ["center_name", "Scientific Center - المركز العلمي", new Date()],
    ["center_phone", "0100112233", new Date()],
    ["center_email", "info@scientificcenter.com", new Date()],
    ["center_address", "Cairo, Egypt", new Date()],
    ["working_hours", "09:00 - 21:00", new Date()],
    ["currency", "ج.م", new Date()]
  ]);
  
  // --- Departments (4 columns) ---
  sheets.Departments.getRange(2,1,2,4).setValues([
    [1, "Information Technology", "IT", 1],
    [2, "Languages", "LANG", 1]
  ]);
  
  // --- Trainers (7 columns) ---
  sheets.Trainers.getRange(2,1,2,7).setValues([
    [1, "Dr. Mohamed Fathy", "0123456789", 1, "Web Development", "Active", ""],
    [2, "Ms. Hend Sabry", "0123456791", 2, "English", "Active", ""]
  ]);
  
  // --- Halls (6 columns) ---
  sheets.Halls.getRange(2,1,2,6).setValues([
    [1, "Hall A (Theory)", 1, "theory", 30, "Active"],
    [2, "Lab 1", 2, "practical", 15, "Active"]
  ]);
  
  // --- Courses (6 columns) ---
  sheets.Courses.getRange(2,1,2,6).setValues([
    [1, "Full Stack Web", 1, 500, 6, ""],
    [2, "English Conversation", 2, 300, 4, ""]
  ]);
  
  // --- Groups (6 columns) ---
  sheets.Groups.getRange(2,1,2,6).setValues([
    [1, 1, "FSW-01", 6, new Date(2025,0,15), ""],
    [2, 2, "ENG-01", 4, new Date(2025,0,20), ""]
  ]);
  
  // --- Students (10 columns) ---
  sheets.Students.getRange(2,1,2,10).setValues([
    [1, "IT-1001", "Youssef Ahmed", "0101112223", "Cairo University", 22, 1, 1, new Date(), ""],
    [2, "LANG-2001", "Omar Khaled", "0101112225", "American University", 23, 2, 2, new Date(), ""]
  ]);
  
  // --- Bookings (9 columns) ---
  sheets.Bookings.getRange(2,1,2,9).setValues([
    [1, 1, 1, 1, "Sunday", "10:00", "12:00", 1, "OK"],
    [2, 2, 2, 2, "Monday", "11:00", "13:00", 1, "OK"]
  ]);
  
  // --- Payments (11 columns) ---
  sheets.Payments.getRange(2,1,2,11).setValues([
    [1, 1, 1, "Course Payment", 300, 0, 500, 200, "First installment", new Date(2025,0,10), 1],
    [2, 2, 1, "Course Payment", 300, 0, 300, 0, "Full payment", new Date(2025,0,15), 1]
  ]);
  
  // --- Levels (6 columns) ---
  sheets.Levels.getRange(2,1,2,6).setValues([
    [1, 1, 1, 500, "partial", ""],
    [2, 2, 1, 300, "paid", ""]
  ]);
  
  // --- AddOns (6 columns) ---
  sheets.AddOns.getRange(2,1,2,6).setValues([
    [1, "Course Book", 150, 1, 1, "Active"],
    [2, "Placement Test", 50, 2, 2, "Active"]
  ]);
}'''

content = re.sub(r'function insertSeedData\(sheets\) \{.*?(?=\n// \-{44}\n// 4\. SETUP RELATIONSHIPS)', new_insert, content, flags=re.DOTALL)

with open('code.gs', 'w', encoding='utf-8') as f:
    f.write(content)
