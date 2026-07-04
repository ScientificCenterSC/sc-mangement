import re

with open('student_profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add apiCall('getAllDepartments') to Promise.all
content = content.replace(
    "apiCall('getAllAddOns')",
    "apiCall('getAllAddOns'),\n                apiCall('getAllDepartments')"
).replace(
    "const [sRes, gRes, pRes, cRes, aRes]",
    "const [sRes, gRes, pRes, cRes, aRes, dRes]"
)

# Update department rendering
content = re.sub(
    r"const deptNames = \{.*?\};\s*document\.getElementById\('stDept'\)\.textContent = deptNames\[student\.deptId\] \|\| '\-';",
    "const allDepartments = dRes || [];\n            const dept = allDepartments.find(d => d.id == student.deptId);\n            document.getElementById('stDept').textContent = dept ? dept.name : '-';",
    content
)

# Replace table headers
new_headers = '''
                        <tr>
                            <th>نوع الدفع</th>
                            <th>المستوى</th>
                            <th>إجمالي المستحق</th>
                            <th>الخصم</th>
                            <th>المدفوع</th>
                            <th>المتبقي</th>
                            <th>ملاحظات</th>
                            <th>التاريخ</th>
                        </tr>
'''
content = re.sub(
    r'<tr>\s*<th>المستوى</th>\s*<th>إجمالي المستحق</th>\s*<th>المبلغ المدفوع</th>\s*<th>المتبقي</th>\s*<th>التاريخ</th>\s*</tr>',
    new_headers,
    content
)

# Replace table row rendering
new_row = '''
                    <tr>
                        <td>${p.paymentType || 'دفع كورس'}</td>
                        <td><strong>مستوى ${p.levelNumber || 1}</strong></td>
                        <td>${p.totalFee || 0} ج.م</td>
                        <td><span style="color:var(--danger)">${p.discountAmount || 0} ج.م</span></td>
                        <td><span class="badge badge-success">${p.amountPaid || 0} ج.م</span></td>
                        <td><span class="badge ${isPaid ? 'badge-success' : 'badge-danger'}">${p.remainingBalance || 0} ج.م</span></td>
                        <td>${p.notes || '-'}</td>
                        <td>${p.paymentDate ? new Date(p.paymentDate).toLocaleDateString('ar-EG') : '-'}</td>
                    </tr>
'''
content = re.sub(
    r'<tr>\s*<td><strong>مستوى \$\{p\.levelNumber \|\| 1\}<\/strong><\/td>.*?<\/tr>',
    new_row,
    content, flags=re.DOTALL
)

# Course history section: just below Payments
course_history_html = '''
        <!-- Course History Card -->
        <div class="card" style="margin-top: 20px;">
            <h3 style="color: var(--dark-blue); margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px;"><i class="fas fa-book"></i> سجل الكورسات والمستويات</h3>
            <div style="overflow-x: auto;">
                <table id="courseHistoryTable">
                    <thead>
                        <tr>
                            <th>الكورس</th>
                            <th>المستوى</th>
                            <th>المصاريف</th>
                            <th>حالة الدفع</th>
                        </tr>
                    </thead>
                    <tbody id="stCoursesBody">
                        <tr><td colspan="4" style="text-align: center;">جاري التحميل...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
'''

content = content.replace('</div>\n</div>\n\n<script>', course_history_html + '\n    </div>\n</div>\n\n<script>')

# Course history logic
# We need to add 'getAllLevels'
content = content.replace(
    "apiCall('getAllDepartments')",
    "apiCall('getAllDepartments'),\n                apiCall('getAllLevels')"
).replace(
    "const [sRes, gRes, pRes, cRes, aRes, dRes]",
    "const [sRes, gRes, pRes, cRes, aRes, dRes, lRes]"
)

course_logic = '''
            // Course History
            const levels = (lRes || []).filter(l => l.studentId == stId);
            const coursesBody = document.getElementById('stCoursesBody');
            if (levels.length > 0) {
                coursesBody.innerHTML = levels.map(l => {
                    const statusBadge = l.status === 'paid' ? '<span class="badge badge-success">مدفوع بالكامل</span>' :
                                       l.status === 'partial' ? '<span class="badge badge-warning" style="background:#fff3cd; color:#856404;">مدفوع جزئياً</span>' :
                                       '<span class="badge badge-danger">غير مدفوع</span>';
                    
                    return `
                    <tr>
                        <td><strong>${courseName}</strong></td>
                        <td>مستوى ${l.levelNumber}</td>
                        <td>${l.levelFee || 0} ج.م</td>
                        <td>${statusBadge}</td>
                    </tr>
                    `;
                }).join('');
            } else {
                coursesBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: #6c757d;">لا توجد مستويات مسجلة</td></tr>`;
            }
'''

content = content.replace("// AddOns", course_logic + "\n            // AddOns")

with open('student_profile.html', 'w', encoding='utf-8') as f:
    f.write(content)
