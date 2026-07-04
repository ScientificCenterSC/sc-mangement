// ====================================================
// SCIENTIFIC CENTER - Course Management System
// ERP Lite Full Database Schema
// Google Apps Script Backend with doPost/doGet Support
// ====================================================

// ============================================
// SAFE CONVERSION UTILITIES (Prevent NaN)
// ============================================
function safeInt(value, defaultValue) {
  if (defaultValue === undefined) defaultValue = '';
  if (value === null || value === undefined || value === '') return defaultValue;
  var parsed = parseInt(value, 10);
  return isNaN(parsed) ? defaultValue : parsed;
}

function safeFloat(value, defaultValue) {
  if (defaultValue === undefined) defaultValue = 0;
  if (value === null || value === undefined || value === '') return defaultValue;
  var parsed = parseFloat(value);
  return isNaN(parsed) ? defaultValue : parsed;
}

// --------------------------------------------
// 1. MAIN FUNCTION TO SETUP THE ENTIRE SYSTEM
// --------------------------------------------
function setupEntireSystem() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Keep only one sheet, delete others
  const sheets = ss.getSheets();
  sheets.forEach(sheet => {
    if (sheet.getSheetName() !== "Instructions" && sheet.getSheetName() !== "README" && sheet.getSheetName() !== "Sheet1") {
      try {
        ss.deleteSheet(sheet);
      } catch(e) { /* ignore */ }
    }
  });
  
  // 2. Create all sheets
  const sheetNames = [
    "Users", "Roles", "Permissions", "RolePermissions", "Floors",
    "Departments", "Trainers", "Halls", "Courses", 
    "Groups", "Students", "Bookings", 
    "Payments", "Levels", "AddOns", "Settings"
  ];
  
  const sheetsCreated = {};
  sheetNames.forEach(name => {
    let sheet = ss.getSheetByName(name);
    if (sheet) {
      ss.deleteSheet(sheet);
    }
    sheet = ss.insertSheet(name);
    sheetsCreated[name] = sheet;
  });
  
  // 3. Create schemas
  createTableSchemas(sheetsCreated);
  
  // 4. Insert seed data
  insertSeedData(sheetsCreated);
  
  // 5. Setup relationships
  setupRelationships(sheetsCreated);
  
  // 6. Create custom menu
  createCustomMenu();
  
  SpreadsheetApp.getUi().alert('✅ System Ready!\n\nAll tables created with sample data.\nUse the custom menu: "🏫 Course System"');
}

// --------------------------------------------
// 2. DEFINE ALL TABLE SCHEMAS
// --------------------------------------------
function createTableSchemas(sheets) {
  // Roles
  sheets.Roles.getRange(1,1,1,5).setValues([["role_id", "role_name", "description", "status", "allowed_floors"]]);
  
  // Floors
  sheets.Floors.getRange(1,1,1,4).setValues([["floor_id", "floor_name", "color", "status"]]);
  
  // Users (added email as column 9)
  sheets.Users.getRange(1,1,1,9).setValues([["user_id", "username", "password", "full_name", "phone", "role_id", "is_active", "created_at", "email"]]);
  
  // Permissions
  sheets.Permissions.getRange(1,1,1,4).setValues([["permission_id", "module", "action", "description"]]);
  
  // RolePermissions
  sheets.RolePermissions.getRange(1,1,1,3).setValues([["rp_id", "role_id", "permission_id"]]);
  
  // Settings
  sheets.Settings.getRange(1,1,1,3).setValues([["setting_key", "setting_value", "updated_at"]]);
  
  // Departments
  sheets.Departments.getRange(1,1,1,4).setValues([["dept_id", "dept_name", "dept_code", "created_by"]]);
  
  // Trainers
  sheets.Trainers.getRange(1,1,1,7).setValues([["trainer_id", "name", "phone", "dept_id", "specialization", "status", "dept_name_auto"]]);
  
  // Halls
  sheets.Halls.getRange(1,1,1,6).setValues([["hall_id", "hall_name", "floor_id", "hall_type", "capacity", "status"]]);
  
  // Courses
  sheets.Courses.getRange(1,1,1,6).setValues([["course_id", "course_name", "dept_id", "price_per_level", "duration_levels", "dept_name_auto"]]);
  
  // Groups
  sheets.Groups.getRange(1,1,1,6).setValues([["group_id", "course_id", "group_name", "level_count", "start_date", "course_name_auto"]]);
  
  // Students
  sheets.Students.getRange(1,1,1,10).setValues([["student_id", "student_code", "name", "phone", "school", "age", "dept_id", "group_id", "created_at", "group_name_auto"]]);
  
  // Bookings
  sheets.Bookings.getRange(1,1,1,9).setValues([["booking_id", "hall_id", "trainer_id", "group_id", "day", "start_time", "end_time", "created_by", "conflict_check"]]);
  
  // Payments
  sheets.Payments.getRange(1,1,1,11).setValues([["payment_id", "student_id", "level_number", "payment_type", "amount_paid", "discount_amount", "total_level_fee", "remaining_balance", "notes", "payment_date", "created_by"]]);
  
  // Levels
  sheets.Levels.getRange(1,1,1,6).setValues([["level_id", "student_id", "level_number", "level_fee", "status", "student_name_auto"]]);
  
  // AddOns
  sheets.AddOns.getRange(1,1,1,6).setValues([["addon_id", "name", "price", "dept_id", "course_id", "status"]]);
  
  // Format headers
  Object.values(sheets).forEach(sheet => {
    sheet.setFrozenRows(1);
    sheet.getRange(1,1,1,sheet.getLastColumn()).setFontWeight("bold").setBackground("#1a2a6c").setFontColor("#ffffff");
  });
}

// --------------------------------------------
// 3. SEED DATA
// --------------------------------------------
function insertSeedData(sheets) {
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
}
// --------------------------------------------
// 4. SETUP RELATIONSHIPS (VLOOKUP Formulas)
// --------------------------------------------
function setupRelationships(sheets) {
  // Trainers - auto department name
  sheets.Trainers.getRange("G2").setFormula("=ARRAYFORMULA(IF(D2:D=\"\",, VLOOKUP(D2:D, Departments!A:D, 2, FALSE)))");
  
  // Courses - auto department name
  sheets.Courses.getRange("F2").setFormula("=ARRAYFORMULA(IF(C2:C=\"\",, VLOOKUP(C2:C, Departments!A:D, 2, FALSE)))");
  
  // Groups - auto course name
  sheets.Groups.getRange("F2").setFormula("=ARRAYFORMULA(IF(B2:B=\"\",, VLOOKUP(B2:B, Courses!A:F, 2, FALSE)))");
  
  // Students - auto group name
  sheets.Students.getRange("J2").setFormula("=ARRAYFORMULA(IF(H2:H=\"\",, VLOOKUP(H2:H, Groups!A:F, 3, FALSE)))");
  
  // Levels - auto student name
  sheets.Levels.getRange("F2").setFormula("=ARRAYFORMULA(IF(B2:B=\"\",, VLOOKUP(B2:B, Students!A:J, 3, FALSE)))");
  
  // Add dropdown validation
  addDropdownValidation(sheets);
  
  // Auto-resize columns
  Object.values(sheets).forEach(sheet => {
    try {
      sheet.autoResizeColumns(1, sheet.getLastColumn());
    } catch(e) {}
  });
}

// --------------------------------------------
// 5. DROPDOWN VALIDATION
// --------------------------------------------
function addDropdownValidation(sheets) {
  try {
    const rolesRange = sheets.Roles.getRange("B2:B" + sheets.Roles.getLastRow());
    const roleRule = SpreadsheetApp.newDataValidation()
      .requireValueInRange(rolesRange, true)
      .build();
    sheets.Users.getRange("F2:F").setDataValidation(roleRule);
  } catch(e) {}
  
  try {
    const statusRule = SpreadsheetApp.newDataValidation()
      .requireValueInList(["Active", "Inactive"], true)
      .build();
    sheets.Trainers.getRange("F2:F").setDataValidation(statusRule);
    sheets.Halls.getRange("F2:F").setDataValidation(statusRule);
  } catch(e) {}
  
  try {
    const levelStatusRule = SpreadsheetApp.newDataValidation()
      .requireValueInList(["paid", "partial", "unpaid"], true)
      .build();
    sheets.Levels.getRange("E2:E").setDataValidation(levelStatusRule);
  } catch(e) {}
  
  try {
    const typeRule = SpreadsheetApp.newDataValidation()
      .requireValueInList(["theory", "practical"], true)
      .build();
    sheets.Halls.getRange("D2:D").setDataValidation(typeRule);
  } catch(e) {}
}

// --------------------------------------------
// 6. CUSTOM MENU
// --------------------------------------------
function createCustomMenu() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🏫 Course System')
    .addItem('🔄 Full System Reset (Wipe & Rebuild)', 'setupEntireSystem')
    .addSeparator()
    .addItem('➕ Add Sample Student', 'addSampleStudent')
    .addItem('💰 Add Sample Payment', 'addSamplePayment')
    .addSeparator()
    .addItem('📊 Show Dashboard Summary', 'showDashboardSummary')
    .addSeparator()
    .addItem('🛠️ Migrate Database Safely (V2)', 'migrateDatabaseSafe')
    .addToUi();
}

// --------------------------------------------
// 7. UTILITY FUNCTIONS
// --------------------------------------------
function addSampleStudent() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const studentsSheet = ss.getSheetByName("Students");
  if (!studentsSheet) return;
  
  const lastRow = studentsSheet.getLastRow();
  const newId = lastRow;
  const deptCode = "IT";
  const randomNum = Math.floor(Math.random() * 9000 + 1000);
  const studentCode = deptCode + "-" + randomNum;
  
  studentsSheet.getRange(lastRow + 1, 1, 1, 10).setValues([[
    newId, studentCode, "New Student", "0100000000", "Test School", 20, 1, 1, new Date(), ""
  ]]);
  SpreadsheetApp.getUi().alert('✅ Student added with Code: ' + studentCode);
}

function addSamplePayment() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const paymentsSheet = ss.getSheetByName("Payments");
  if (!paymentsSheet) return;
  
  const lastRow = paymentsSheet.getLastRow();
  const newId = lastRow;
  
  paymentsSheet.getRange(lastRow + 1, 1, 1, 8).setValues([[
    newId, 1, 1, 100, 500, 400, new Date(), 2
  ]]);
  SpreadsheetApp.getUi().alert('✅ Partial payment of 100 recorded for Student ID 1. Remaining: 400');
}

function showDashboardSummary() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const students = (ss.getSheetByName("Students") ? ss.getSheetByName("Students").getLastRow() - 1 : 0) || 0;
  const trainers = (ss.getSheetByName("Trainers") ? ss.getSheetByName("Trainers").getLastRow() - 1 : 0) || 0;
  const payments = (ss.getSheetByName("Payments") ? ss.getSheetByName("Payments").getLastRow() - 1 : 0) || 0;
  
  SpreadsheetApp.getUi().alert(
    '📊 SYSTEM DASHBOARD\n\n' +
    '👨‍🎓 Students: ' + students + '\n' +
    '👨‍🏫 Trainers: ' + trainers + '\n' +
    '💰 Payments: ' + payments + '\n' +
    '✅ System ready for daily use.'
  );
}

function migrateDatabaseSafe() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Update Groups table schema
  const groupsSheet = ss.getSheetByName("Groups");
  if (groupsSheet) {
    const headers = groupsSheet.getRange(1, 1, 1, groupsSheet.getLastColumn()).getValues()[0];
    const requiredGroupHeaders = ["dept_id", "level", "trainer_id", "capacity", "status"];
    let nextCol = headers.length + 1;
    
    requiredGroupHeaders.forEach(col => {
      if (!headers.includes(col)) {
        groupsSheet.getRange(1, nextCol).setValue(col).setFontWeight("bold").setBackground("#1a2a6c").setFontColor("#ffffff");
        nextCol++;
      }
    });
  }

  // 2. Update Payments table schema
  const paymentsSheet = ss.getSheetByName("Payments");
  if (paymentsSheet) {
    const headers = paymentsSheet.getRange(1, 1, 1, paymentsSheet.getLastColumn()).getValues()[0];
    if (!headers.includes("receipt_number")) {
      const nextCol = headers.length + 1;
      paymentsSheet.getRange(1, nextCol).setValue("receipt_number").setFontWeight("bold").setBackground("#1a2a6c").setFontColor("#ffffff");
    }
  }

  SpreadsheetApp.getUi().alert('✅ Database migration completed successfully! All necessary columns added without data loss.');
}

// --------------------------------------------
// 8. ON OPEN TRIGGER
// --------------------------------------------
function onOpen() {
  createCustomMenu();
}

// ====================================================
// 9. WEB APP ENDPOINTS (doGet & doPost) - WITH CORS
// ====================================================

function doGet(e) {
  try {
    if (e && e.parameter && e.parameter.action) {
      const result = handleApiRequestGet(e.parameter);
      return createJsonResponse(result);
    }
    
    return HtmlService.createHtmlOutputFromFile('index')
      .setTitle('Scientific Center - Course Management')
      .setFaviconUrl('https://cdn-icons-png.flaticon.com/512/3135/3135715.png')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1');
  } catch (error) {
    return createJsonResponse({ success: false, message: "Server error: " + error.toString() });
  }
}

function doPost(e) {
  try {
    var requestData = {};
    if (e && e.postData && e.postData.contents) {
      requestData = JSON.parse(e.postData.contents);
    } else if (e && e.parameter) {
      requestData = e.parameter;
    }
    
    var action = requestData.action;
    
    if (!action) {
      return createJsonResponse({ success: false, message: "Missing 'action' parameter" });
    }
    
    var result = handleApiRequestPost(action, requestData);
    return createJsonResponse(result);
    
  } catch (error) {
    return createJsonResponse({ 
      success: false, 
      message: "Server error: " + error.toString() 
    });
  }
}

function handleApiRequestGet(params) {
  var action = params.action;
  if (action === 'getAllLevels') return { success: true, data: getAllLevels() };
  var action = params.action;
  
  switch (action) {
    case 'login':
      return verifyLogin(params.username, params.password);
    case 'getAllStudents':
      return { success: true, data: getAllStudents() };
    case 'getAllPayments':
      return { success: true, data: getAllPayments() };
    case 'getFinancialSummary':
      return { success: true, data: getFinancialSummary() };
    case 'getAllTrainers':
      return { success: true, data: getAllTrainers() };
    case 'getAllHalls':
      return { success: true, data: getAllHalls() };
    case 'getAllGroups':
      return { success: true, data: getAllGroups() };
    case 'getAllBookings':
      return { success: true, data: getAllBookings() };
    case 'getDashboardStats':
      return { success: true, data: getDashboardStats() };
    case 'getAllRoles':
      return { success: true, data: getAllRoles() };
    case 'getAllPermissions':
      return { success: true, data: getAllPermissions() };
    case 'getAllSettings':
      return { success: true, data: getAllSettings() };
    case 'getAllDepartments':
      return { success: true, data: getAllDepartments() };
    case 'getAllFloors':
      return { success: true, data: getAllFloors() };
    case 'getAllCourses':
      return { success: true, data: getAllCourses() };
    case 'getAllAddOns':
      return { success: true, data: getAllAddOns() };
    default:
      return { success: false, message: "Unknown action: " + action };
  }
}

function handleApiRequestPost(action, params) {
  if (action === 'saveHall') return saveHall(params.hallData);
  if (action === 'deleteHall') return deleteHall(params.id);
  if (action === 'getAllLevels') return { success: true, data: getAllLevels() };
  switch (action) {
    // Auth
    case 'login':
      return verifyLogin(params.username, params.password);
    
    // Users
    case 'getAllUsers':
      return { success: true, data: getAllUsers() };
    case 'saveUser':
      return saveUser(params.data);
    case 'deleteUser':
      return deleteUser(params.id);
    
    // Students
    case 'getAllStudents':
      return { success: true, data: getAllStudents() };
    case 'getStudentById':
      return { success: true, data: getStudentById(params.studentId) };
    case 'saveStudent':
      return saveStudent(params.studentData || params.data || params);
    case 'deleteStudent':
      return deleteStudent(params.studentId || params.id);
    
    // Payments
    case 'getAllPayments':
      return { success: true, data: getAllPayments() };
    case 'savePayment':
      return savePayment(params.paymentData || params.data || params);
    case 'bulkSavePayments':
      return bulkSavePayments(params.payments);
    case 'deletePayment':
      return deletePayment(params.paymentId || params.id);
    case 'getFinancialSummary':
      return { success: true, data: getFinancialSummary() };
    
    // Trainers
    case 'getAllTrainers':
      return { success: true, data: getAllTrainers() };
    case 'saveTrainer':
      return saveTrainer(params.trainerData || params.data || params);
    case 'deleteTrainer':
      return deleteTrainer(params.id || params.trainerId);
    
    // Halls & Groups
    case 'getAllHalls':
      return { success: true, data: getAllHalls() };
    case 'getAllGroups':
      return { success: true, data: getAllGroups() };
    case 'saveGroup':
      return saveGroup(params.groupData || params.data || params);
    case 'deleteGroup':
      return deleteGroup(params.groupId || params.id);
    
    // Bookings
    case 'getAllBookings':
      return { success: true, data: getAllBookings() };
    case 'saveBooking':
      return saveBooking(params.bookingData || params.data || params);
    case 'deleteBooking':
      return deleteBooking(params.bookingId || params.id);
    
    // Dashboard
    case 'getDashboardStats':
      return { success: true, data: getDashboardStats() };
    
    // Roles
    case 'getAllRoles':
      return { success: true, data: getAllRoles() };
    case 'saveRole':
      return saveRole(params.data || params);
    case 'deleteRole':
      return deleteRole(params.id || params.roleId);
    
    // Permissions
    case 'getAllPermissions':
      return { success: true, data: getAllPermissions() };
    case 'savePermission':
      return savePermission(params.data || params);
    case 'deletePermission':
      return deletePermission(params.id || params.permissionId);
    
    // Role Permissions
    case 'getRolePermissions':
      return { success: true, data: getRolePermissions(params.roleId) };
    case 'saveRolePermissions':
      return saveRolePermissions(params.roleId, params.permissionIds);
    case 'checkPermission':
      return { success: true, data: checkPermission(params.roleId, params.module, params.action_name) };
    case 'getUserPermissions':
      return { success: true, data: getUserPermissions(params.roleId) };
    
    // Settings
    case 'getAllSettings':
      return { success: true, data: getAllSettings() };
    case 'saveSettings':
      return saveSettings(params.data || params.settings);
      
    // Departments
    case 'getAllDepartments':
      return { success: true, data: getAllDepartments() };
    case 'saveDepartment':
      return saveDepartment(params.deptData || params.data || params);
    case 'deleteDepartment':
      return deleteDepartment(params.id || params.deptId);
      
    // Floors
    case 'getAllFloors':
      return { success: true, data: getAllFloors() };
    case 'saveFloor':
      return saveFloor(params.floorData || params.data || params);
    case 'deleteFloor':
      return deleteFloor(params.id || params.floorId);
      
    // Courses
    case 'getAllCourses':
      return { success: true, data: getAllCourses() };
    case 'saveCourse':
      return saveCourse(params.courseData || params.data || params);
    case 'deleteCourse':
      return deleteCourse(params.id || params.courseId);
      
    // AddOns
    case 'getAllAddOns':
      return { success: true, data: getAllAddOns() };
    case 'saveAddOn':
      return saveAddOn(params.addonData || params.data || params);
    case 'deleteAddOn':
      return deleteAddOn(params.id || params.addonId);
      
    // Payment Details
    case 'getStudentPaymentDetails':
      return { success: true, data: getStudentPaymentDetails(params.studentId) };
    
    default:
      return { success: false, message: "Unknown action: " + action };
  }
}

function createJsonResponse(data) {
  var output = ContentService.createTextOutput(JSON.stringify(data));
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}

// ====================================================
// 10. API FUNCTIONS (DATABASE OPERATIONS)
// ====================================================

// ---------- AUTH ----------
function verifyLogin(username, password) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Users");
  if (!sheet) return { success: false, message: "System not initialized" };
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][1] === username && data[i][2] === password) {
      if (data[i][6] === false) {
        return { success: false, message: "هذا الحساب غير نشط" };
      }
      var roleId = data[i][5];
      var roleAllowedFloors = "";
      var rolesSheet = ss.getSheetByName("Roles");
      if (rolesSheet) {
        var rData = rolesSheet.getDataRange().getValues();
        for (var r = 1; r < rData.length; r++) {
          if (rData[r][0] == roleId) {
            roleAllowedFloors = rData[r][4] || "";
            break;
          }
        }
      }
      return {
        success: true,
        user: {
          id: data[i][0],
          username: data[i][1],
          fullName: data[i][3],
          phone: data[i][4],
          roleId: roleId,
          isActive: data[i][6],
          email: data[i][8] || '',
          permissions: getUserPermissions(roleId),
          allowedFloors: roleAllowedFloors
        }
      };
    }
  }
  return { success: false, message: "اسم المستخدم أو كلمة المرور غير صحيحة" };
}

// ---------- USERS ----------
function getAllUsers() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Users");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var users = [];
  for (var i = 1; i < data.length; i++) {
    users.push({
      id: data[i][0],
      username: data[i][1],
      fullName: data[i][3],
      phone: data[i][4],
      roleId: data[i][5],
      isActive: data[i][6],
      createdAt: data[i][7],
      email: data[i][8] || ''
    });
  }
  return users;
}

function saveUser(userData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Users");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!userData || !userData.username || !userData.fullName) {
    return { success: false, message: "الاسم واسم المستخدم مطلوبان" };
  }
  
  var data = sheet.getDataRange().getValues();
  
  // Check for unique username
  for (var i = 1; i < data.length; i++) {
    if (data[i][1] === userData.username && data[i][0] != userData.id) {
      return { success: false, message: "اسم المستخدم موجود مسبقاً!" };
    }
  }
  
  if (userData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == userData.id) {
        sheet.getRange(i+1, 2).setValue(userData.username);
        if (userData.password) sheet.getRange(i+1, 3).setValue(userData.password);
        sheet.getRange(i+1, 4).setValue(userData.fullName);
        sheet.getRange(i+1, 5).setValue(userData.phone || '');
        sheet.getRange(i+1, 6).setValue(safeInt(userData.roleId, 1));
        sheet.getRange(i+1, 7).setValue(userData.isActive !== false && userData.isActive !== 'false');
        sheet.getRange(i+1, 9).setValue(userData.email || '');
        return { success: true, message: "تم تحديث المستخدم بنجاح" };
      }
    }
  } else {
    var lastRow = sheet.getLastRow();
    var newId = lastRow;
    
    if (!userData.password) {
      return { success: false, message: "كلمة المرور مطلوبة للمستخدم الجديد" };
    }
    
    sheet.getRange(lastRow + 1, 1).setValue(newId);
    sheet.getRange(lastRow + 1, 2).setValue(userData.username);
    sheet.getRange(lastRow + 1, 3).setValue(userData.password);
    sheet.getRange(lastRow + 1, 4).setValue(userData.fullName);
    sheet.getRange(lastRow + 1, 5).setValue(userData.phone || '');
    sheet.getRange(lastRow + 1, 6).setValue(safeInt(userData.roleId, 1));
    sheet.getRange(lastRow + 1, 7).setValue(userData.isActive !== false && userData.isActive !== 'false');
    sheet.getRange(lastRow + 1, 8).setValue(new Date());
    sheet.getRange(lastRow + 1, 9).setValue(userData.email || '');
    
    return { success: true, message: "تم إضافة المستخدم بنجاح" };
  }
  return { success: false, message: "المستخدم غير موجود" };
}

function deleteUser(userId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Users");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == userId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم حذف المستخدم بنجاح" };
    }
  }
  return { success: false, message: "المستخدم غير موجود" };
}

// ---------- ROLES ----------
function getAllRoles() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Roles");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var roles = [];
  for (var i = 1; i < data.length; i++) {
    roles.push({
      id: data[i][0],
      name: data[i][1],
      description: data[i][2],
      status: data[i][3] || 'Active',
      allowedFloors: data[i][4] || ''
    });
  }
  return roles;
}

function saveRole(roleData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Roles");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!roleData || !roleData.name) {
    return { success: false, message: "اسم الصلاحية مطلوب" };
  }
  
  var data = sheet.getDataRange().getValues();
  
  // Check unique name
  for (var i = 1; i < data.length; i++) {
    if (data[i][1] === roleData.name && data[i][0] != roleData.id) {
      return { success: false, message: "اسم الصلاحية موجود مسبقاً!" };
    }
  }
  
  if (roleData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == roleData.id) {
        sheet.getRange(i+1, 2).setValue(roleData.name);
        sheet.getRange(i+1, 3).setValue(roleData.description || '');
        sheet.getRange(i+1, 4).setValue(roleData.status || 'Active');
        sheet.getRange(i+1, 5).setValue(roleData.allowedFloors || '');
      return { success: true, message: "تم تحديث الصلاحية بنجاح", roleId: roleData.id };
      }
    }
  } else {
    var lastRow = sheet.getLastRow();
    var newId = lastRow;
    
    sheet.getRange(lastRow + 1, 1).setValue(newId);
    sheet.getRange(lastRow + 1, 2).setValue(roleData.name);
    sheet.getRange(lastRow + 1, 3).setValue(roleData.description || '');
    sheet.getRange(lastRow + 1, 4).setValue(roleData.status || 'Active');
    sheet.getRange(lastRow + 1, 5).setValue(roleData.allowedFloors || '');
    
    return { success: true, message: "تم إضافة الصلاحية بنجاح", roleId: newId };
  }
  return { success: false, message: "الصلاحية غير موجودة" };
}

function deleteRole(roleId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Roles");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  // Don't allow deleting Super Admin
  if (roleId == 1) {
    return { success: false, message: "لا يمكن حذف صلاحية Super Admin" };
  }
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == roleId) {
      sheet.deleteRow(i+1);
      // Also remove all RolePermissions for this role
      removeRolePermissionsForRole(roleId);
      return { success: true, message: "تم حذف الصلاحية بنجاح" };
    }
  }
  return { success: false, message: "الصلاحية غير موجودة" };
}

// ---------- PERMISSIONS ----------
function getAllPermissions() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Permissions");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var perms = [];
  for (var i = 1; i < data.length; i++) {
    perms.push({
      id: data[i][0],
      module: data[i][1],
      action: data[i][2],
      description: data[i][3]
    });
  }
  return perms;
}

function savePermission(permData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Permissions");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!permData || !permData.module || !permData.action) {
    return { success: false, message: "الوحدة والإجراء مطلوبان" };
  }
  
  var data = sheet.getDataRange().getValues();
  
  if (permData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == permData.id) {
        sheet.getRange(i+1, 2).setValue(permData.module);
        sheet.getRange(i+1, 3).setValue(permData.action);
        sheet.getRange(i+1, 4).setValue(permData.description || '');
        return { success: true, message: "تم تحديث الصلاحية بنجاح" };
      }
    }
  } else {
    var lastRow = sheet.getLastRow();
    var newId = lastRow;
    
    sheet.getRange(lastRow + 1, 1).setValue(newId);
    sheet.getRange(lastRow + 1, 2).setValue(permData.module);
    sheet.getRange(lastRow + 1, 3).setValue(permData.action);
    sheet.getRange(lastRow + 1, 4).setValue(permData.description || '');
    
    return { success: true, message: "تم إضافة الصلاحية بنجاح" };
  }
  return { success: false, message: "الصلاحية غير موجودة" };
}

function deletePermission(permId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Permissions");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == permId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم حذف الصلاحية بنجاح" };
    }
  }
  return { success: false, message: "الصلاحية غير موجودة" };
}

// ---------- ROLE PERMISSIONS ----------
function getRolePermissions(roleId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("RolePermissions");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var permIds = [];
  for (var i = 1; i < data.length; i++) {
    if (data[i][1] == roleId) {
      permIds.push(data[i][2]);
    }
  }
  return permIds;
}

function saveRolePermissions(roleId, permissionIds) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("RolePermissions");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!roleId) return { success: false, message: "Role ID is required" };
  
  // Remove existing permissions for this role
  removeRolePermissionsForRole(roleId);
  
  // Add new permissions
  if (permissionIds && permissionIds.length > 0) {
    var lastRow = sheet.getLastRow();
    for (var i = 0; i < permissionIds.length; i++) {
      var newId = lastRow + i;
      sheet.getRange(lastRow + 1 + i, 1).setValue(newId);
      sheet.getRange(lastRow + 1 + i, 2).setValue(safeInt(roleId));
      sheet.getRange(lastRow + 1 + i, 3).setValue(safeInt(permissionIds[i]));
    }
  }
  
  return { success: true, message: "تم تحديث صلاحيات الدور بنجاح" };
}

function removeRolePermissionsForRole(roleId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("RolePermissions");
  if (!sheet) return;
  
  var data = sheet.getDataRange().getValues();
  // Delete from bottom to top to avoid row shifting issues
  for (var i = data.length - 1; i >= 1; i--) {
    if (data[i][1] == roleId) {
      sheet.deleteRow(i + 1);
    }
  }
}

function checkPermission(roleId, module, actionName) {
  // Super Admin always has all permissions
  if (roleId == 1) return true;
  
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var rpSheet = ss.getSheetByName("RolePermissions");
  var permSheet = ss.getSheetByName("Permissions");
  if (!rpSheet || !permSheet) return false;
  
  // Find the permission ID for this module+action
  var permData = permSheet.getDataRange().getValues();
  var permId = null;
  for (var i = 1; i < permData.length; i++) {
    if (permData[i][1] === module && permData[i][2] === actionName) {
      permId = permData[i][0];
      break;
    }
  }
  if (!permId) return false;
  
  // Check if role has this permission
  var rpData = rpSheet.getDataRange().getValues();
  for (var i = 1; i < rpData.length; i++) {
    if (rpData[i][1] == roleId && rpData[i][2] == permId) {
      return true;
    }
  }
  return false;
}

function getUserPermissions(roleId) {
  // Super Admin gets all
  if (roleId == 1) {
    var allPerms = getAllPermissions();
    return allPerms.map(function(p) { return { module: p.module, action: p.action }; });
  }
  
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var rpSheet = ss.getSheetByName("RolePermissions");
  var permSheet = ss.getSheetByName("Permissions");
  if (!rpSheet || !permSheet) return [];
  
  var rolePermIds = getRolePermissions(roleId);
  var allPerms = getAllPermissions();
  var result = [];
  
  for (var i = 0; i < allPerms.length; i++) {
    for (var j = 0; j < rolePermIds.length; j++) {
      if (allPerms[i].id == rolePermIds[j]) {
        result.push({ module: allPerms[i].module, action: allPerms[i].action });
        break;
      }
    }
  }
  return result;
}

// ---------- SETTINGS ----------
function getAllSettings() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Settings");
  if (!sheet) return {};
  var data = sheet.getDataRange().getValues();
  var settings = {};
  for (var i = 1; i < data.length; i++) {
    settings[data[i][0]] = data[i][1];
  }
  return settings;
}

function saveSettings(settingsData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Settings");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!settingsData) return { success: false, message: "No settings data provided" };
  
  var data = sheet.getDataRange().getValues();
  var now = new Date();
  
  for (var key in settingsData) {
    if (!settingsData.hasOwnProperty(key)) continue;
    var found = false;
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] === key) {
        sheet.getRange(i+1, 2).setValue(settingsData[key]);
        sheet.getRange(i+1, 3).setValue(now);
        found = true;
        break;
      }
    }
    if (!found) {
      var lastRow = sheet.getLastRow();
      sheet.getRange(lastRow + 1, 1).setValue(key);
      sheet.getRange(lastRow + 1, 2).setValue(settingsData[key]);
      sheet.getRange(lastRow + 1, 3).setValue(now);
      data.push([key, settingsData[key], now]); // Update local cache
    }
  }
  
  return { success: true, message: "تم حفظ الإعدادات بنجاح" };
}

// ---------- STUDENTS ----------
function getAllStudents() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Students");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var students = [];
  for (var i = 1; i < data.length; i++) {
    students.push({
      id: data[i][0],
      code: data[i][1],
      name: data[i][2],
      phone: data[i][3],
      school: data[i][4],
      age: data[i][5],
      deptId: data[i][6],
      groupId: data[i][7],
      createdAt: data[i][8],
      groupName: data[i][9]
    });
  }
  return students;
}

function getStudentById(studentId) {
  var students = getAllStudents();
  for (var i = 0; i < students.length; i++) {
    if (students[i].id == studentId) return students[i];
  }
  return null;
}

function saveStudent(studentData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Students");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!studentData || !studentData.name) {
    return { success: false, message: "الاسم بالكامل مطلوب" };
  }
  
  var data = sheet.getDataRange().getValues();
  
  // Dynamic Department Codes
  var deptSheet = ss.getSheetByName("Departments");
  var deptCodeMap = {};
  if (deptSheet) {
    var deptData = deptSheet.getDataRange().getValues();
    for (var d = 1; d < deptData.length; d++) {
      deptCodeMap[deptData[d][0]] = deptData[d][2] || "STD";
    }
  } else {
    deptCodeMap = {1: "IT", 2: "LANG", 3: "BUS", 4: "GD"};
  }
  
  var currentYear = new Date().getFullYear();
  var deptCode = deptCodeMap[studentData.deptId] || "STD";
  var prefix = deptCode + "-" + currentYear + "-";
  
  function getNextStudentCode() {
    var maxSeq = 0;
    for (var j = 1; j < data.length; j++) {
      var existingCode = data[j][1];
      if (existingCode && existingCode.indexOf(prefix) === 0) {
        var seqStr = existingCode.split("-")[2];
        var seqNum = parseInt(seqStr, 10);
        if (!isNaN(seqNum) && seqNum > maxSeq) {
          maxSeq = seqNum;
        }
      }
    }
    var nextSeq = maxSeq + 1;
    var paddedSeq = ("000" + nextSeq).slice(-4);
    return prefix + paddedSeq;
  }
  
  if (studentData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == studentData.id) {
        var studentCode = data[i][1];
        if (!studentCode) {
          studentCode = getNextStudentCode();
        }
        
        sheet.getRange(i+1, 2).setValue(studentCode);
        sheet.getRange(i+1, 3).setValue(studentData.name);
        sheet.getRange(i+1, 4).setValue(studentData.phone || '');
        sheet.getRange(i+1, 5).setValue(studentData.school || '');
        sheet.getRange(i+1, 6).setValue(safeInt(studentData.age, ''));
        sheet.getRange(i+1, 7).setValue(safeInt(studentData.deptId, ''));
        sheet.getRange(i+1, 8).setValue(studentData.groupId ? safeInt(studentData.groupId) : '');
        
        return { success: true, message: "تم تحديث بيانات الطالب بنجاح" };
      }
    }
  } else {
    var lastRow = sheet.getLastRow();
    var newId = lastRow;
    
    var studentCode = getNextStudentCode();
    
    sheet.getRange(lastRow + 1, 1).setValue(newId);
    sheet.getRange(lastRow + 1, 2).setValue(studentCode);
    sheet.getRange(lastRow + 1, 3).setValue(studentData.name);
    sheet.getRange(lastRow + 1, 4).setValue(studentData.phone || '');
    sheet.getRange(lastRow + 1, 5).setValue(studentData.school || '');
    sheet.getRange(lastRow + 1, 6).setValue(safeInt(studentData.age, ''));
    sheet.getRange(lastRow + 1, 7).setValue(safeInt(studentData.deptId, ''));
    sheet.getRange(lastRow + 1, 8).setValue(studentData.groupId ? safeInt(studentData.groupId) : '');
    sheet.getRange(lastRow + 1, 9).setValue(new Date());
    
    return { success: true, message: "تم إضافة الطالب بنجاح - الكود: " + studentCode };
  }
  
  return { success: false, message: "الطالب غير موجود" };
}

function deleteStudent(studentId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Students");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == studentId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم حذف الطالب بنجاح" };
    }
  }
  
  return { success: false, message: "الطالب غير موجود" };
}

// ---------- PAYMENTS ----------
function getAllPayments() {
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
    if (!data[i][0] && !data[i][1]) continue; // skip empty rows
    payments.push({
      id: data[i][0],
      studentId: data[i][1],
      studentName: studentNames[data[i][1]] || '',
      levelNumber: data[i][2],
      paymentType: data[i][3],
      amountPaid: safeFloat(data[i][4], 0),
      discountAmount: safeFloat(data[i][5], 0),
      totalLevelFee: safeFloat(data[i][6], 0),
      totalFee: safeFloat(data[i][6], 0), // alias for compatibility
      remainingBalance: safeFloat(data[i][7], 0),
      notes: data[i][8] || '',
      paymentDate: data[i][9] ? new Date(data[i][9]).toISOString().split('T')[0] : '',
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
  var receiptNumber = paymentData.receiptNumber || paymentData.receipt_number || '';
  
  if (!studentId || (amountPaid <= 0 && discountAmount <= 0)) {
    return { success: false, message: "بيانات الدفع غير مكتملة" };
  }
  
  if (!receiptNumber) {
    return { success: false, message: "رقم الإيصال مطلوب" };
  }
  
  var data = sheet.getDataRange().getValues();
  var prevTotalPaid = 0;
  var prevTotalDiscount = 0;
  
  if (paymentData.id) {
      for (var i = 1; i < data.length; i++) {
        if (data[i][11] == receiptNumber && data[i][0] != paymentData.id) {
            return { success: false, message: "رقم الإيصال مسجل مسبقاً" };
        }
        if (data[i][1] == studentId && data[i][2] == levelNumber && data[i][3] == paymentType && data[i][0] != paymentData.id) {
          prevTotalPaid += safeFloat(data[i][4], 0);
          prevTotalDiscount += safeFloat(data[i][5], 0);
        }
      }
  } else {
      for (var i = 1; i < data.length; i++) {
        if (data[i][11] == receiptNumber) {
            return { success: false, message: "رقم الإيصال مسجل مسبقاً" };
        }
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
              sheet.getRange(i+1, 12).setValue(receiptNumber);
              
              updateLevelsTable(studentId, levelNumber, totalLevelFee, remainingBalance);
              return { success: true, message: "تم تحديث الدفع بنجاح" };
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
      sheet.getRange(lastRow + 1, 12).setValue(receiptNumber);
  }
  
  updateLevelsTable(studentId, levelNumber, totalLevelFee, remainingBalance);
  
  return { success: true, message: "تم تسجيل الدفعة بنجاح" };
}

function updateLevelsTable(studentId, levelNumber, levelFee, remainingBalance) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var levelsSheet = ss.getSheetByName("Levels");
  if (!levelsSheet) return;
  
  var data = levelsSheet.getDataRange().getValues();
  var found = false;
  
  for (var i = 1; i < data.length; i++) {
    if (data[i][1] == studentId && data[i][2] == levelNumber) {
      var status = remainingBalance === 0 ? "paid" : "partial";
      levelsSheet.getRange(i+1, 4).setValue(levelFee);
      levelsSheet.getRange(i+1, 5).setValue(status);
      found = true;
      break;
    }
  }
  
  if (!found) {
    var lastRow = levelsSheet.getLastRow();
    var status = remainingBalance === 0 ? "paid" : "partial";
    levelsSheet.getRange(lastRow + 1, 1).setValue(lastRow);
    levelsSheet.getRange(lastRow + 1, 2).setValue(studentId);
    levelsSheet.getRange(lastRow + 1, 3).setValue(levelNumber);
    levelsSheet.getRange(lastRow + 1, 4).setValue(levelFee);
    levelsSheet.getRange(lastRow + 1, 5).setValue(status);
  }
}

function deletePayment(paymentId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Payments");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == paymentId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم حذف الدفعة بنجاح" };
    }
  }
  return { success: false, message: "الدفعة غير موجودة" };
}

function getFinancialSummary() {
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
}

// ---------- TRAINERS ----------
function getAllTrainers() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Trainers");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var trainers = [];
  for (var i = 1; i < data.length; i++) {
    trainers.push({
      id: data[i][0],
      name: data[i][1],
      phone: data[i][2],
      deptId: data[i][3],
      specialization: data[i][4],
      status: data[i][5],
      deptName: data[i][6]
    });
  }
  return trainers;
}

function saveTrainer(trainerData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Trainers");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!trainerData || !trainerData.name) {
    return { success: false, message: "اسم المدرب مطلوب" };
  }
  
  var data = sheet.getDataRange().getValues();
  
  if (trainerData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == trainerData.id) {
        sheet.getRange(i+1, 2).setValue(trainerData.name);
        sheet.getRange(i+1, 3).setValue(trainerData.phone || '');
        sheet.getRange(i+1, 4).setValue(safeInt(trainerData.deptId, ''));
        sheet.getRange(i+1, 5).setValue(trainerData.specialization || '');
        sheet.getRange(i+1, 6).setValue(trainerData.status || "Active");
        return { success: true, message: "تم تحديث بيانات المدرب بنجاح" };
      }
    }
  } else {
    var lastRow = sheet.getLastRow();
    var newId = lastRow;
    
    sheet.getRange(lastRow + 1, 1).setValue(newId);
    sheet.getRange(lastRow + 1, 2).setValue(trainerData.name);
    sheet.getRange(lastRow + 1, 3).setValue(trainerData.phone || '');
    sheet.getRange(lastRow + 1, 4).setValue(safeInt(trainerData.deptId, ''));
    sheet.getRange(lastRow + 1, 5).setValue(trainerData.specialization || '');
    sheet.getRange(lastRow + 1, 6).setValue(trainerData.status || "Active");
    
    return { success: true, message: "تم إضافة المدرب بنجاح" };
  }
  
  return { success: false, message: "المدرب غير موجود" };
}

function deleteTrainer(trainerId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Trainers");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == trainerId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم حذف المدرب بنجاح" };
    }
  }
  
  return { success: false, message: "المدرب غير موجود" };
}

// ---------- HALLS ----------
function getAllHalls() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Halls");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var halls = [];
  for (var i = 1; i < data.length; i++) {
    halls.push({
      id: data[i][0],
      name: data[i][1],
      floorNumber: data[i][2],
      type: data[i][3],
      capacity: data[i][4],
      status: data[i][5]
    });
  }
  return halls;
}

// ---------- BULK PAYMENTS ----------

function bulkSavePayments(paymentsArray) {
  try {
    if (!paymentsArray || !Array.isArray(paymentsArray) || paymentsArray.length === 0) {
      return { success: false, message: "لا توجد مدفوعات للحفظ" };
    }
    
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("Payments");
    var levelsSheet = ss.getSheetByName("Levels");
    
    if (!sheet) return { success: false, message: "Sheet 'Payments' not found" };
    if (!levelsSheet) return { success: false, message: "Sheet 'Levels' not found" };
    
    var data = sheet.getDataRange().getValues();
    var lastRow = sheet.getLastRow();
    
    // Prepare array of arrays to append in bulk for performance
    var newRows = [];
    var newId = lastRow > 1 ? parseInt(data[lastRow - 1][0], 10) || 0 : 0;
    
    // Update Levels
    var levelsData = levelsSheet.getDataRange().getValues();
    
    for (var i = 0; i < paymentsArray.length; i++) {
      var pay = paymentsArray[i];
      newId++;
      
      var studentId = pay.studentId;
      var levelNumber = pay.levelNumber;
      var paymentType = pay.paymentType || "Course Payment";
      var totalLevelFee = safeFloat(pay.totalLevelFee, 0);
      var amountPaid = safeFloat(pay.amountPaid, 0);
      var discountAmount = safeFloat(pay.discountAmount, 0);
      
      var currentTotalPaid = amountPaid;
      var currentTotalDiscount = discountAmount;
      
      // Find previous payments in DB
      for (var r = 1; r < data.length; r++) {
        if (data[r][1] == studentId && data[r][2] == levelNumber && data[r][3] == paymentType) {
          currentTotalPaid += safeFloat(data[r][5], 0);
          currentTotalDiscount += safeFloat(data[r][6], 0);
        }
      }
      
      // Account for payments in THIS batch
      for (var j = 0; j < i; j++) {
        if (paymentsArray[j].studentId == studentId && paymentsArray[j].levelNumber == levelNumber && paymentsArray[j].paymentType == paymentType) {
           currentTotalPaid += safeFloat(paymentsArray[j].amountPaid, 0);
           currentTotalDiscount += safeFloat(paymentsArray[j].discountAmount, 0);
        }
      }
      
      var remainingBalance = totalLevelFee - currentTotalPaid - currentTotalDiscount;
      if (remainingBalance < 0) remainingBalance = 0;
      
      var dateStr = pay.paymentDate ? pay.paymentDate : new Date().toISOString().split('T')[0];
      
      newRows.push([
        newId,
        studentId,
        levelNumber,
        paymentType,
        totalLevelFee,
        amountPaid,
        discountAmount,
        remainingBalance,
        pay.notes || '',
        dateStr,
        new Date(),
        pay.receiptNumber || ''
      ]);
      
      updateLevelsTableBulk(levelsSheet, levelsData, studentId, levelNumber, totalLevelFee, remainingBalance);
    }
    
    if (newRows.length > 0) {
      sheet.getRange(lastRow + 1, 1, newRows.length, newRows[0].length).setValues(newRows);
    }
    
    return { success: true, message: "تم حفظ الدفعات המجمعة بنجاح" };
  } catch (e) {
    return { success: false, message: "Error in bulkSavePayments: " + e.message };
  }
}

function updateLevelsTableBulk(levelsSheet, levelsData, studentId, levelNumber, levelFee, remainingBalance) {
  var found = false;
  var status = remainingBalance === 0 ? "paid" : "partial";
  
  for (var i = 1; i < levelsData.length; i++) {
    if (levelsData[i][1] == studentId && levelsData[i][2] == levelNumber) {
      levelsSheet.getRange(i+1, 4).setValue(levelFee);
      levelsSheet.getRange(i+1, 5).setValue(status);
      found = true;
      break;
    }
  }
  
  if (!found) {
    var lastRow = levelsSheet.getLastRow();
    levelsSheet.getRange(lastRow + 1, 1).setValue(lastRow);
    levelsSheet.getRange(lastRow + 1, 2).setValue(studentId);
    levelsSheet.getRange(lastRow + 1, 3).setValue(levelNumber);
    levelsSheet.getRange(lastRow + 1, 4).setValue(levelFee);
    levelsSheet.getRange(lastRow + 1, 5).setValue(status);
    levelsData.push([lastRow, studentId, levelNumber, levelFee, status]);
  }
}

// ---------- GROUPS ----------
function getAllGroups() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Groups");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var groups = [];
  for (var i = 1; i < data.length; i++) {
    groups.push({
      id: data[i][0],
      courseId: data[i][1],
      name: data[i][2],
      levelCount: data[i][3],
      startDate: data[i][4],
      courseName: data[i][5],
      deptId: data[i][6] || null,
      level: data[i][7] || '',
      trainerId: data[i][8] || null,
      capacity: data[i][9] || '',
      status: data[i][10] || 'Active'
    });
  }
  return groups;
}

function saveGroup(groupData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Groups");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!groupData || !groupData.name) {
    return { success: false, message: "اسم الجروب مطلوب" };
  }
  
  var data = sheet.getDataRange().getValues();
  
  // Check unique name
  for (var i = 1; i < data.length; i++) {
    if (data[i][2] === groupData.name && data[i][0] != groupData.id) {
      return { success: false, message: "اسم الجروب موجود مسبقاً!" };
    }
  }
  
  if (groupData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == groupData.id) {
        sheet.getRange(i+1, 2).setValue(groupData.courseId || '');
        sheet.getRange(i+1, 3).setValue(groupData.name);
        sheet.getRange(i+1, 4).setValue(groupData.levelCount || '');
        sheet.getRange(i+1, 5).setValue(groupData.startDate || '');
        sheet.getRange(i+1, 7).setValue(groupData.deptId || '');
        sheet.getRange(i+1, 8).setValue(groupData.level || '');
        sheet.getRange(i+1, 9).setValue(groupData.trainerId || '');
        sheet.getRange(i+1, 10).setValue(groupData.capacity || '');
        sheet.getRange(i+1, 11).setValue(groupData.status || 'Active');
        return { success: true, message: "تم تحديث الجروب بنجاح" };
      }
    }
  } else {
    var lastRow = sheet.getLastRow();
    var newId = lastRow; // Assumes row 1 is header
    
    sheet.getRange(lastRow + 1, 1).setValue(newId);
    sheet.getRange(lastRow + 1, 2).setValue(groupData.courseId || '');
    sheet.getRange(lastRow + 1, 3).setValue(groupData.name);
    sheet.getRange(lastRow + 1, 4).setValue(groupData.levelCount || '');
    sheet.getRange(lastRow + 1, 5).setValue(groupData.startDate || new Date());
    // Auto formula will run for courseName in F
    sheet.getRange(lastRow + 1, 7).setValue(groupData.deptId || '');
    sheet.getRange(lastRow + 1, 8).setValue(groupData.level || '');
    sheet.getRange(lastRow + 1, 9).setValue(groupData.trainerId || '');
    sheet.getRange(lastRow + 1, 10).setValue(groupData.capacity || '');
    sheet.getRange(lastRow + 1, 11).setValue(groupData.status || 'Active');
    
    return { success: true, message: "تم إضافة الجروب بنجاح" };
  }
  return { success: false, message: "الجروب غير موجود" };
}

function deleteGroup(groupId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Groups");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == groupId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم حذف الجروب بنجاح" };
    }
  }
  return { success: false, message: "الجروب غير موجود" };
}

// ---------- BOOKINGS ----------
function getAllBookings() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Bookings");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var bookings = [];
  for (var i = 1; i < data.length; i++) {
    bookings.push({
      id: data[i][0],
      hallId: data[i][1],
      trainerId: data[i][2],
      groupId: data[i][3],
      day: data[i][4],
      startTime: data[i][5],
      endTime: data[i][6],
      createdBy: data[i][7],
      conflict: data[i][8]
    });
  }
  return bookings;
}

function saveBooking(bookingData) {
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
}

function deleteBooking(bookingId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Bookings");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == bookingId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم حذف الحجز بنجاح" };
    }
  }
  return { success: false, message: "الحجز غير موجود" };
}

// ---------- DASHBOARD ----------
function getDashboardStats() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  var studentsSheet = ss.getSheetByName("Students");
  var trainersSheet = ss.getSheetByName("Trainers");
  var bookingsSheet = ss.getSheetByName("Bookings");
  var paymentsSheet = ss.getSheetByName("Payments");
  var hallsSheet = ss.getSheetByName("Halls");
  var groupsSheet = ss.getSheetByName("Groups");
  
  return {
    studentCount: studentsSheet ? Math.max(studentsSheet.getLastRow() - 1, 0) : 0,
    trainerCount: trainersSheet ? Math.max(trainersSheet.getLastRow() - 1, 0) : 0,
    bookingCount: bookingsSheet ? Math.max(bookingsSheet.getLastRow() - 1, 0) : 0,
    paymentCount: paymentsSheet ? Math.max(paymentsSheet.getLastRow() - 1, 0) : 0,
    hallCount: hallsSheet ? Math.max(hallsSheet.getLastRow() - 1, 0) : 0,
    groupCount: groupsSheet ? Math.max(groupsSheet.getLastRow() - 1, 0) : 0
  };
}

// ---------- DEPARTMENTS ----------
function getAllDepartments() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Departments");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var departments = [];
  for (var i = 1; i < data.length; i++) {
    departments.push({
      id: data[i][0],
      name: data[i][1],
      code: data[i][2],
      createdBy: data[i][3]
    });
  }
  return departments;
}

function saveDepartment(deptData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Departments");
  if (!sheet) return { success: false, message: "Sheet not found" };
  if (!deptData || !deptData.name) return { success: false, message: "اسم القسم مطلوب" };
  
  var data = sheet.getDataRange().getValues();
  if (deptData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == deptData.id) {
        sheet.getRange(i+1, 2).setValue(deptData.name);
        sheet.getRange(i+1, 3).setValue(deptData.code || '');
        return { success: true, message: "تم التحديث بنجاح" };
      }
    }
  } else {
    var newId = sheet.getLastRow();
    sheet.getRange(newId + 1, 1).setValue(newId);
    sheet.getRange(newId + 1, 2).setValue(deptData.name);
    sheet.getRange(newId + 1, 3).setValue(deptData.code || '');
    sheet.getRange(newId + 1, 4).setValue(safeInt(deptData.createdBy, 1));
    return { success: true, message: "تمت الإضافة بنجاح" };
  }
  return { success: false, message: "القسم غير موجود" };
}

function deleteDepartment(deptId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Departments");
  if (!sheet) return { success: false, message: "Sheet not found" };
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == deptId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم الحذف بنجاح" };
    }
  }
  return { success: false, message: "القسم غير موجود" };
}

// ---------- FLOORS ----------
function getAllFloors() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Floors");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var floors = [];
  for (var i = 1; i < data.length; i++) {
    floors.push({
      id: data[i][0],
      name: data[i][1],
      color: data[i][2],
      status: data[i][3] || 'Active'
    });
  }
  return floors;
}

function saveFloor(floorData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Floors");
  if (!sheet) return { success: false, message: "Sheet not found" };
  if (!floorData || !floorData.name) return { success: false, message: "اسم الدور مطلوب" };
  
  var data = sheet.getDataRange().getValues();
  if (floorData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == floorData.id) {
        sheet.getRange(i+1, 2).setValue(floorData.name);
        sheet.getRange(i+1, 3).setValue(floorData.color || '#cccccc');
        sheet.getRange(i+1, 4).setValue(floorData.status || 'Active');
        return { success: true, message: "تم التحديث بنجاح" };
      }
    }
  } else {
    var newId = sheet.getLastRow();
    sheet.getRange(newId + 1, 1).setValue(newId);
    sheet.getRange(newId + 1, 2).setValue(floorData.name);
    sheet.getRange(newId + 1, 3).setValue(floorData.color || '#cccccc');
    sheet.getRange(newId + 1, 4).setValue(floorData.status || 'Active');
    return { success: true, message: "تمت الإضافة بنجاح" };
  }
  return { success: false, message: "الدور غير موجود" };
}

function deleteFloor(floorId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Floors");
  if (!sheet) return { success: false, message: "Sheet not found" };
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == floorId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم الحذف بنجاح" };
    }
  }
  return { success: false, message: "الدور غير موجود" };
}

// ---------- COURSES ----------
function getAllCourses() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Courses");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var courses = [];
  for (var i = 1; i < data.length; i++) {
    courses.push({
      id: data[i][0],
      name: data[i][1],
      deptId: data[i][2],
      pricePerLevel: data[i][3],
      durationLevels: data[i][4],
      deptName: data[i][5]
    });
  }
  return courses;
}

function saveCourse(courseData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Courses");
  if (!sheet) return { success: false, message: "Sheet not found" };
  if (!courseData || !courseData.name) return { success: false, message: "اسم الكورس مطلوب" };
  
  var data = sheet.getDataRange().getValues();
  if (courseData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == courseData.id) {
        sheet.getRange(i+1, 2).setValue(courseData.name);
        sheet.getRange(i+1, 3).setValue(safeInt(courseData.deptId, ''));
        sheet.getRange(i+1, 4).setValue(safeFloat(courseData.pricePerLevel, 0));
        sheet.getRange(i+1, 5).setValue(safeInt(courseData.durationLevels, 1));
        return { success: true, message: "تم التحديث بنجاح" };
      }
    }
  } else {
    var newId = sheet.getLastRow();
    sheet.getRange(newId + 1, 1).setValue(newId);
    sheet.getRange(newId + 1, 2).setValue(courseData.name);
    sheet.getRange(newId + 1, 3).setValue(safeInt(courseData.deptId, ''));
    sheet.getRange(newId + 1, 4).setValue(safeFloat(courseData.pricePerLevel, 0));
    sheet.getRange(newId + 1, 5).setValue(safeInt(courseData.durationLevels, 1));
    return { success: true, message: "تمت الإضافة بنجاح" };
  }
  return { success: false, message: "الكورس غير موجود" };
}

function deleteCourse(courseId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Courses");
  if (!sheet) return { success: false, message: "Sheet not found" };
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == courseId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم الحذف بنجاح" };
    }
  }
  return { success: false, message: "الكورس غير موجود" };
}

// ---------- ADDONS ----------
function getAllAddOns() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("AddOns");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var addons = [];
  for (var i = 1; i < data.length; i++) {
    addons.push({
      id: data[i][0],
      name: data[i][1],
      price: data[i][2],
      courseId: data[i][3],
      levelApplicable: data[i][4]
    });
  }
  return addons;
}

function saveAddOn(addonData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("AddOns");
  if (!sheet) return { success: false, message: "Sheet not found" };
  if (!addonData || !addonData.name) return { success: false, message: "الاسم مطلوب" };
  
  var data = sheet.getDataRange().getValues();
  if (addonData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == addonData.id) {
        sheet.getRange(i+1, 2).setValue(addonData.name);
        sheet.getRange(i+1, 3).setValue(safeFloat(addonData.price, 0));
        sheet.getRange(i+1, 4).setValue(addonData.courseId ? safeInt(addonData.courseId) : '');
        sheet.getRange(i+1, 5).setValue(addonData.levelApplicable ? safeInt(addonData.levelApplicable) : '');
        return { success: true, message: "تم التحديث بنجاح" };
      }
    }
  } else {
    var newId = sheet.getLastRow();
    sheet.getRange(newId + 1, 1).setValue(newId);
    sheet.getRange(newId + 1, 2).setValue(addonData.name);
    sheet.getRange(newId + 1, 3).setValue(safeFloat(addonData.price, 0));
    sheet.getRange(newId + 1, 4).setValue(addonData.courseId ? safeInt(addonData.courseId) : '');
    sheet.getRange(newId + 1, 5).setValue(addonData.levelApplicable ? safeInt(addonData.levelApplicable) : '');
    return { success: true, message: "تمت الإضافة بنجاح" };
  }
  return { success: false, message: "الإضافة غير موجودة" };
}

function deleteAddOn(addonId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("AddOns");
  if (!sheet) return { success: false, message: "Sheet not found" };
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == addonId) {
      sheet.deleteRow(i+1);
      return { success: true, message: "تم الحذف بنجاح" };
    }
  }
  return { success: false, message: "الإضافة غير موجودة" };
}

// ---------- PAYMENT DETAILS ----------
function getStudentPaymentDetails(studentId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Get Student Group
  var studentsSheet = ss.getSheetByName("Students");
  var groupId = null;
  if (studentsSheet) {
    var sData = studentsSheet.getDataRange().getValues();
    for (var i = 1; i < sData.length; i++) {
      if (sData[i][0] == studentId) {
        groupId = sData[i][7];
        break;
      }
    }
  }
  
  if (!groupId) return { coursePrice: 0, addons: [] };
  
  // 2. Get Group's Course
  var groupsSheet = ss.getSheetByName("Groups");
  var courseId = null;
  if (groupsSheet) {
    var gData = groupsSheet.getDataRange().getValues();
    for (var j = 1; j < gData.length; j++) {
      if (gData[j][0] == groupId) {
        courseId = gData[j][1];
        break;
      }
    }
  }
  
  if (!courseId) return { coursePrice: 0, addons: [] };
  
  // 3. Get Course Price
  var coursesSheet = ss.getSheetByName("Courses");
  var coursePrice = 0;
  if (coursesSheet) {
    var cData = coursesSheet.getDataRange().getValues();
    for (var k = 1; k < cData.length; k++) {
      if (cData[k][0] == courseId) {
        coursePrice = safeFloat(cData[k][3], 0);
        break;
      }
    }
  }
  
  // 4. Get Applicable AddOns
  var addonsSheet = ss.getSheetByName("AddOns");
  var addons = [];
  if (addonsSheet) {
    var aData = addonsSheet.getDataRange().getValues();
    for (var a = 1; a < aData.length; a++) {
      if (!aData[a][3] || aData[a][3] == courseId) {
        addons.push({
          id: aData[a][0],
          name: aData[a][1],
          price: safeFloat(aData[a][2], 0)
        });
      }
    }
  }
  
  return {
    coursePrice: coursePrice,
    addons: addons
  };
}
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
