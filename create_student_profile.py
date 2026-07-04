import os

filepath = "c:/Users/shahd/Downloads/ss/student_profile.html"
html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الملف الشخصي للطالب | Scientific Center</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
        :root {
            --primary-blue: #3c6ec8;
            --dark-blue: #1e3c72;
            --light-blue: #e0e7ff;
            --success: #2ecc71;
            --danger: #e74c3c;
            --gray: #6c757d;
            --light-gray: #f8f9fa;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Cairo', sans-serif; }
        body { background: #f0f4f8; padding: 20px; }
        
        .header-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: white;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .btn-back {
            padding: 10px 20px;
            background: var(--light-gray);
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--dark-blue);
            text-decoration: none;
        }
        .btn-back:hover { background: #e2e6ea; }
        
        .profile-container {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
        }
        
        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        
        .info-item {
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px dashed #eee;
        }
        .info-item:last-child { border: none; margin-bottom: 0; padding-bottom: 0; }
        .info-label { color: var(--gray); font-size: 14px; margin-bottom: 5px; }
        .info-value { font-size: 16px; font-weight: bold; color: var(--dark-blue); }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background: var(--dark-blue);
            color: white;
            padding: 15px;
            text-align: right;
            font-size: 14px;
        }
        td {
            padding: 15px;
            border-bottom: 1px solid #eee;
            font-size: 14px;
        }
        tr:hover { background: var(--light-gray); }
        
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        
        @media (max-width: 900px) {
            .profile-container { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

<div class="header-bar">
    <div>
        <h2 style="color: var(--dark-blue);">الملف الشخصي للطالب</h2>
        <p style="color: var(--gray); font-size: 14px;">بيانات تفصيلية وسجل مالي كامل</p>
    </div>
    <a href="students.html" class="btn-back"><i class="fas fa-arrow-right"></i> عودة لقائمة الطلاب</a>
</div>

<div class="profile-container">
    <!-- Basic Info -->
    <div class="card">
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="width: 100px; height: 100px; background: linear-gradient(135deg, var(--primary-blue), var(--dark-blue)); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 40px; margin: 0 auto 15px;">
                <i class="fas fa-user-graduate"></i>
            </div>
            <h2 id="stName" style="color: var(--dark-blue);">-</h2>
            <div id="stCode" style="color: var(--gray); margin-top: 5px;">-</div>
        </div>
        
        <div class="info-item">
            <div class="info-label"><i class="fas fa-phone"></i> رقم الهاتف</div>
            <div class="info-value" id="stPhone">-</div>
        </div>
        <div class="info-item">
            <div class="info-label"><i class="fas fa-school"></i> المدرسة / الجامعة</div>
            <div class="info-value" id="stSchool">-</div>
        </div>
        <div class="info-item">
            <div class="info-label"><i class="fas fa-birthday-cake"></i> العمر</div>
            <div class="info-value" id="stAge">-</div>
        </div>
        <div class="info-item">
            <div class="info-label"><i class="fas fa-building"></i> القسم</div>
            <div class="info-value" id="stDept">-</div>
        </div>
        <div class="info-item">
            <div class="info-label"><i class="fas fa-users"></i> الجروب الحالي</div>
            <div class="info-value" id="stGroup">-</div>
        </div>
        <div class="info-item">
            <div class="info-label"><i class="fas fa-book"></i> الكورس الأكاديمي</div>
            <div class="info-value" id="stCourse">-</div>
        </div>
    </div>
    
    <!-- Financial & AddOns -->
    <div>
        <!-- AddOns Card -->
        <div class="card" style="margin-bottom: 20px;">
            <h3 style="color: var(--dark-blue); margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px;"><i class="fas fa-plus-circle"></i> الإضافات المدفوعة (AddOns)</h3>
            <ul id="stAddonsList" style="list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 15px;">
                <li style="color: var(--gray);">جاري التحميل...</li>
            </ul>
        </div>
        
        <!-- Payments Card -->
        <div class="card">
            <h3 style="color: var(--dark-blue); margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px;"><i class="fas fa-history"></i> السجل المالي والدفعات</h3>
            <div style="overflow-x: auto;">
                <table id="paymentsTable">
                    <thead>
                        <tr>
                            <th>المستوى</th>
                            <th>إجمالي المستحق</th>
                            <th>المبلغ المدفوع</th>
                            <th>المتبقي</th>
                            <th>التاريخ</th>
                        </tr>
                    </thead>
                    <tbody id="stPaymentsBody">
                        <tr><td colspan="5" style="text-align: center;">جاري التحميل...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<script>
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';
    
    async function apiCall(action, data = {}) {
        const response = await fetch(SCRIPT_URL, {
            method: 'POST',
            body: JSON.stringify({ action, ...data })
        });
        const result = await response.json();
        return result.data !== undefined ? result.data : result;
    }

    document.addEventListener('DOMContentLoaded', async function() {
        const urlParams = new URLSearchParams(window.location.search);
        const stId = urlParams.get('id');
        if(!stId) { alert("طالب غير موجود"); window.location.href = "students.html"; return; }
        
        try {
            const [sRes, gRes, pRes, cRes, aRes] = await Promise.all([
                apiCall('getAllStudents'),
                apiCall('getAllGroups'),
                apiCall('getAllPayments'),
                apiCall('getAllCourses'),
                apiCall('getAllAddOns')
            ]);
            
            const student = (sRes || []).find(s => s.id == stId);
            if(!student) { alert("طالب غير موجود"); window.location.href = "students.html"; return; }
            
            // Populate Basic Info
            document.getElementById('stName').textContent = student.name || '-';
            document.getElementById('stCode').textContent = student.code || '-';
            document.getElementById('stPhone').textContent = student.phone || '-';
            document.getElementById('stSchool').textContent = student.school || '-';
            document.getElementById('stAge').textContent = student.age || '-';
            
            const deptNames = {1: 'تقنية المعلومات (IT)', 2: 'اللغات (LANG)', 3: 'إدارة الأعمال (BUS)', 4: 'التصميم (GD)'};
            document.getElementById('stDept').textContent = deptNames[student.deptId] || '-';
            
            const groups = gRes || [];
            const group = groups.find(g => g.id == student.groupId);
            document.getElementById('stGroup').textContent = group ? group.name : 'بدون جروب';
            
            let courseName = '-';
            if (group && group.courseId) {
                const course = (cRes || []).find(c => c.id == group.courseId);
                if (course) courseName = course.name;
            }
            document.getElementById('stCourse').textContent = courseName;
            
            // Payments
            const payments = (pRes || []).filter(p => p.studentId == stId);
            payments.sort((a, b) => new Date(b.paymentDate) - new Date(a.paymentDate));
            
            const payBody = document.getElementById('stPaymentsBody');
            if (payments.length > 0) {
                payBody.innerHTML = payments.map(p => {
                    const isPaid = p.remainingBalance <= 0;
                    return `
                    <tr>
                        <td><strong>مستوى ${p.levelNumber || 1}</strong></td>
                        <td>${p.totalFee || 0} ج.م</td>
                        <td><span class="badge badge-success">${p.amountPaid || 0} ج.م</span></td>
                        <td><span class="badge ${isPaid ? 'badge-success' : 'badge-danger'}">${p.remainingBalance || 0} ج.م</span></td>
                        <td>${p.paymentDate ? new Date(p.paymentDate).toLocaleDateString('ar-EG') : '-'}</td>
                    </tr>
                `}).join('');
            } else {
                payBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #6c757d;">لا يوجد سجل مالي</td></tr>`;
            }
            
            // AddOns
            let paidAddonIds = new Set();
            payments.forEach(p => {
                if (p.addonsPaid) {
                    let ids = p.addonsPaid.split(',').map(aid => parseInt(aid.trim()));
                    ids.forEach(aid => { if(!isNaN(aid)) paidAddonIds.add(aid); });
                }
            });
            
            const addList = document.getElementById('stAddonsList');
            if (paidAddonIds.size > 0) {
                addList.innerHTML = Array.from(paidAddonIds).map(aid => {
                    const addon = (aRes || []).find(a => a.id == aid);
                    if (addon) {
                        return `<li style="background: #eef2ff; padding: 10px 20px; border-radius: 12px; border: 1px solid #c7d2fe; color: #3730a3; font-weight: bold;"><i class="fas fa-check-circle" style="color: var(--success); margin-left: 5px;"></i> ${addon.name} <span style="background: white; padding: 2px 8px; border-radius: 10px; margin-right: 10px; font-size: 12px;">${addon.price} ج.م</span></li>`;
                    }
                    return '';
                }).join('');
            } else {
                addList.innerHTML = `<li style="color: var(--gray); width: 100%; text-align: center;">لم يتم دفع أية إضافات</li>`;
            }
            
        } catch(e) {
            console.error(e);
            alert("حدث خطأ أثناء تحميل البيانات");
        }
    });
</script>
</body>
</html>
"""
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html_content)

# Update students.html to link to this new page instead of modal
students_filepath = "c:/Users/shahd/Downloads/ss/students.html"
with open(students_filepath, 'r', encoding='utf-8') as f:
    st_content = f.read()

# Replace viewProfile function logic to redirect
js_start = st_content.find('function viewProfile(id) {')
js_end = st_content.find('window.viewProfile = viewProfile;', js_start)

new_js = """function viewProfile(id) {
        window.location.href = 'student_profile.html?id=' + id;
    }
    
    """
st_content = st_content[:js_start] + new_js + st_content[js_end:]

with open(students_filepath, 'w', encoding='utf-8') as f:
    f.write(st_content)

print("Created student_profile.html and updated students.html linking")
