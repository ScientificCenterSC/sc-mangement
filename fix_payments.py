import re

with open('payments.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update Table Headers
new_headers = '''
                        <tr>
                            <th>الطالب</th>
                            <th>الكود</th>
                            <th>المستوى</th>
                            <th>نوع الدفع</th>
                            <th>المدفوع</th>
                            <th>الخصم</th>
                            <th>إجمالي المستوى</th>
                            <th>المتبقي</th>
                            <th>ملاحظات</th>
                            <th>التاريخ</th>
                            <th>الإجراءات</th>
                        </tr>
'''
content = re.sub(
    r'<tr>\s*<th>الطالب</th>\s*<th>الكود</th>\s*<th>المستوى</th>\s*<th>المبلغ المدفوع</th>\s*<th>إجمالي المستوى</th>\s*<th>المتبقي</th>\s*<th>التاريخ</th>\s*<th>الحالة</th>\s*<th>الإجراءات</th>\s*</tr>',
    new_headers,
    content
)

# Replace Modal content
new_modal = '''
            <div id="paymentFormSection" style="display: none;">
                <div class="form-group">
                    <label>الطالب</label>
                    <input type="text" id="selectedStudentName" readonly style="background: #f5f5f5;">
                    <input type="hidden" id="selectedStudentId">
                </div>
                <div class="form-group">
                    <label>رقم المستوى / رقم الإضافة</label>
                    <input type="number" id="levelNumber" value="1" min="1">
                </div>
                <div class="form-group">
                    <label>نوع الدفع</label>
                    <select id="paymentType">
                        <option value="Course Payment">دفع كورس</option>
                        <option value="AddOn Payment">دفع إضافة</option>
                        <option value="Manual Adjustment">تعديل يدوي</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>إجمالي الرسوم (ج.م)</label>
                    <input type="number" id="totalLevelFee" placeholder="مثلاً: 500">
                </div>
                <div class="form-group">
                    <label>المبلغ المدفوع (ج.م)</label>
                    <input type="number" id="amountPaid" placeholder="أدخل المبلغ">
                </div>
                <div class="form-group">
                    <label>الخصم (ج.م)</label>
                    <input type="number" id="discountAmount" placeholder="قيمة الخصم إن وجد" value="0">
                </div>
                <div class="form-group">
                    <label>ملاحظات</label>
                    <input type="text" id="notes" placeholder="ملاحظات إضافية">
                </div>
                <div class="form-group">
                    <label>تاريخ الدفع</label>
                    <input type="date" id="paymentDate">
                </div>
            </div>
'''
content = re.sub(r'<div id="paymentFormSection" style="display: none;">.*?</div>\s*</div>\s*<div class="modal-footer">', new_modal + '\n        </div>\n        <div class="modal-footer">', content, flags=re.DOTALL)

# In JS: update rendering
new_render_row = '''
        const student = allStudents.find(s => s.id == p.studentId) || {};
        const isPaid = p.remainingBalance <= 0;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${student.name || p.studentName || 'غير معروف'}</strong></td>
            <td>${student.code || '-'}</td>
            <td>مستوى ${p.levelNumber || 1}</td>
            <td>${p.paymentType || 'دفع كورس'}</td>
            <td><span class="badge badge-success">${p.amountPaid || 0} ج.م</span></td>
            <td><span style="color:var(--danger)">${p.discountAmount || 0} ج.م</span></td>
            <td>${p.totalFee || 0} ج.م</td>
            <td><span class="badge ${isPaid ? 'badge-success' : 'badge-danger'}">${p.remainingBalance || 0} ج.م</span></td>
            <td>${p.notes || '-'}</td>
            <td>${p.paymentDate ? new Date(p.paymentDate).toLocaleDateString('ar-EG') : '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-icon btn-delete" onclick="deletePayment(${p.id})" title="حذف الدفعة"><i class="fas fa-trash"></i></button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
'''
content = re.sub(r'const student = allStudents\.find\(s => s\.id == p\.studentId\) \|\| \{\};.*?tbody\.appendChild\(tr\);', new_render_row, content, flags=re.DOTALL)

# Update savePayment logic in JS
# Find function completePayment
new_save = '''
        const data = {
            studentId: document.getElementById('selectedStudentId').value,
            levelNumber: document.getElementById('levelNumber').value,
            paymentType: document.getElementById('paymentType').value,
            totalLevelFee: document.getElementById('totalLevelFee').value,
            amountPaid: document.getElementById('amountPaid').value,
            discountAmount: document.getElementById('discountAmount').value,
            notes: document.getElementById('notes').value,
            paymentDate: document.getElementById('paymentDate').value || new Date().toISOString().split('T')[0],
            createdBy: currentUser.id
        };
        
        if (!data.studentId || (parseFloat(data.amountPaid) <= 0 && parseFloat(data.discountAmount) <= 0)) {
            showToast('الرجاء إدخال مبلغ صحيح أو خصم', 'warning');
            return;
        }
        
        showLoading(true);
        try {
            const res = await apiCall('savePayment', { paymentData: data });
            if (res.success) {
                showToast(res.message, 'success');
                closeModal();
                loadData();
            } else {
                showToast(res.message, 'error');
            }
        } catch (e) {
            console.error(e);
        }
        showLoading(false);
'''
content = re.sub(r'async function completePayment\(\) \{.*?showLoading\(false\);\s*\}', 'async function completePayment() {\n' + new_save + '\n}', content, flags=re.DOTALL)

# To ensure the event listener points to completePayment properly, wait, the button is "savePayment".
# Let's check what it currently does. It had a function bound to it probably. I'll just find what is inside document.getElementById('savePayment').addEventListener('click', ...)
content = re.sub(r"document\.getElementById\('savePayment'\)\.addEventListener\('click', .*?\);", "document.getElementById('savePayment').addEventListener('click', completePayment);", content)

with open('payments.html', 'w', encoding='utf-8') as f:
    f.write(content)
