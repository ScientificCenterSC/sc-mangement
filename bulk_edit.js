    // =================== BULK PAYMENT & EDIT ===================

    // Bulk Payment Elements
    const bulkPaymentBtn = document.getElementById('bulkPaymentBtn');
    const bulkPaymentModal = document.getElementById('bulkPaymentModal');
    const closeBulkModalBtn = document.getElementById('closeBulkModal');
    const cancelBulkModalBtn = document.getElementById('cancelBulkModal');
    const bulkDeptFilter = document.getElementById('bulkDeptFilter');
    const bulkCourseFilter = document.getElementById('bulkCourseFilter');
    const bulkGroupFilter = document.getElementById('bulkGroupFilter');
    const bulkStudentsTableBody = document.getElementById('bulkStudentsTableBody');
    const selectAllBulk = document.getElementById('selectAllBulk');
    const saveBulkPaymentsBtn = document.getElementById('saveBulkPaymentsBtn');

    if (bulkPaymentBtn) {
        bulkPaymentBtn.addEventListener('click', () => {
            bulkDeptFilter.innerHTML = '<option value="">اختر القسم</option>';
            allDepts.forEach(d => bulkDeptFilter.innerHTML += <option value="+d.id+">+d.name+</option>);
            bulkCourseFilter.innerHTML = '<option value="">اختر الكورس</option>';
            bulkGroupFilter.innerHTML = '<option value="">اختر الجروب</option>';
            bulkStudentsTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">اختر الجروب لظهور الطلاب</td></tr>';
            bulkPaymentModal.style.display = 'flex';
        });
    }
    
    if (closeBulkModalBtn) closeBulkModalBtn.addEventListener('click', () => bulkPaymentModal.style.display = 'none');
    if (cancelBulkModalBtn) cancelBulkModalBtn.addEventListener('click', () => bulkPaymentModal.style.display = 'none');

    if (bulkDeptFilter) {
        bulkDeptFilter.addEventListener('change', () => {
            const deptId = bulkDeptFilter.value;
            bulkCourseFilter.innerHTML = '<option value="">اختر الكورس</option>';
            bulkGroupFilter.innerHTML = '<option value="">اختر الجروب</option>';
            if (deptId) {
                const courses = allCourses.filter(c => c.deptId == deptId);
                courses.forEach(c => bulkCourseFilter.innerHTML += <option value="+c.id+">+(c.courseName||c.name)+</option>);
            }
            renderBulkStudents();
        });
    }

    if (bulkCourseFilter) {
        bulkCourseFilter.addEventListener('change', () => {
            const deptId = bulkDeptFilter.value;
            const courseId = bulkCourseFilter.value;
            bulkGroupFilter.innerHTML = '<option value="">اختر الجروب</option>';
            if (courseId) {
                let groups = allGroups.filter(g => g.courseId == courseId);
                if (deptId) groups = groups.filter(g => g.deptId == deptId);
                groups.forEach(g => bulkGroupFilter.innerHTML += <option value="+g.id+">+g.name+</option>);
            }
            renderBulkStudents();
        });
    }

    if (bulkGroupFilter) {
        bulkGroupFilter.addEventListener('change', renderBulkStudents);
    }

    function renderBulkStudents() {
        const groupId = bulkGroupFilter.value;
        if (!groupId) {
            bulkStudentsTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">اختر الجروب لظهور الطلاب</td></tr>';
            return;
        }

        const students = allStudents.filter(s => String(s.groupId) === String(groupId));
        if (students.length === 0) {
            bulkStudentsTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">لا يوجد طلاب في هذا الجروب</td></tr>';
            return;
        }

        bulkStudentsTableBody.innerHTML = students.map(s => {
            return <tr>
                <td><input type="checkbox" class="bulk-student-check" value="+s.id+" checked></td>
                <td>+s.name+</td>
                <td>+(s.code || '-')+</td>
                <td><input type="number" class="bulk-amount" data-id="+s.id+" placeholder="المبلغ" style="width: 100px; padding: 5px;" min="0"></td>
                <td><input type="number" class="bulk-discount" data-id="+s.id+" placeholder="الخصم" style="width: 80px; padding: 5px;" min="0" value="0"></td>
                <td><input type="text" class="bulk-receipt" data-id="+s.id+" placeholder="رقم الإيصال" style="width: 120px; padding: 5px;"></td>
            </tr>;
        }).join('');
    }

    if (selectAllBulk) {
        selectAllBulk.addEventListener('change', (e) => {
            const checks = document.querySelectorAll('.bulk-student-check');
            checks.forEach(c => c.checked = e.target.checked);
        });
    }

    if (saveBulkPaymentsBtn) {
        saveBulkPaymentsBtn.addEventListener('click', async () => {
            const groupId = bulkGroupFilter.value;
            if (!groupId) return showToast('الرجاء تحديد الجروب', 'warning');
            
            const group = allGroups.find(g => String(g.id) === String(groupId));
            if (!group) return;
            const course = allCourses.find(c => String(c.id) === String(group.courseId));
            const totalFee = course ? (parseFloat(course.pricePerLevel) || 0) : 0;
            const levelNumber = group.level || '1'; // or just 1 if no level
            
            const payments = [];
            const checks = document.querySelectorAll('.bulk-student-check:checked');
            checks.forEach(c => {
                const sid = c.value;
                const amountInput = document.querySelector(.bulk-amount[data-id="+sid+"]).value;
                const discountInput = document.querySelector(.bulk-discount[data-id="+sid+"]).value;
                const receiptInput = document.querySelector(.bulk-receipt[data-id="+sid+"]).value;
                
                const amt = parseFloat(amountInput) || 0;
                const disc = parseFloat(discountInput) || 0;
                
                if (amt > 0 || disc > 0) {
                    payments.push({
                        studentId: parseInt(sid),
                        levelNumber: levelNumber,
                        paymentType: 'Course Payment',
                        totalLevelFee: totalFee,
                        amountPaid: amt,
                        discountAmount: disc,
                        receiptNumber: receiptInput,
                        notes: 'Bulk Payment',
                        paymentDate: new Date().toISOString()
                    });
                }
            });

            if (payments.length === 0) {
                return showToast('الرجاء إدخال مبالغ مدفوعة للطلاب المحددين', 'warning');
            }

            bulkPaymentModal.style.display = 'none';
            showLoading(true, 'جاري حفظ الدفعات المجمعة...');
            const result = await safeApiCall('bulkSavePayments', { payments: payments }, null);
            if (result && result.success) {
                showToast('تم حفظ الدفعات بنجاح', 'success');
                loadData();
            } else {
                showToast(result?.message || 'حدث خطأ أثناء الحفظ', 'error');
            }
            showLoading(false);
        });
    }

    window.editPayment = function(id) {
        const p = allPayments.find(pay => String(pay.id) === String(id));
        if (!p) return;
        
        document.getElementById('editPaymentId').value = p.id;
        document.getElementById('modalTitle').textContent = 'تعديل الدفعة';
        
        // Cannot easily switch student or level after saving, so just show current
        openAddPaymentModal(); // opens UI
        
        // Hide step 1 and step 2, show step 3 directly
        hide('step1'); hide('step2'); show('step3');
        
        document.getElementById('amountPaid').value = p.amountPaid || 0;
        document.getElementById('discountAmount').value = p.discountAmount || 0;
        document.getElementById('receiptNumber').value = p.receipt_number || p.receiptNumber || '';
        document.getElementById('notes').value = p.notes || '';
        document.getElementById('paymentDate').value = p.paymentDate ? new Date(p.paymentDate).toISOString().substring(0, 10) : new Date().toISOString().substring(0, 10);
        
        // Set fixed variables so save works
        selectedStudent = allStudents.find(s => String(s.id) === String(p.studentId));
        paymentCategory = (p.paymentType === 'Course Payment') ? 'course' : 'addon';
        if (paymentCategory === 'course') {
            selectedLevelNumber = p.levelNumber;
            document.getElementById('totalLevelFee').value = p.totalLevelFee || p.totalFee || 0;
            // update remaining balance
            const remaining = parseFloat(p.totalLevelFee || p.totalFee || 0) - parseFloat(p.amountPaid || 0) - parseFloat(p.discountAmount || 0);
            document.getElementById('remainingBalance').value = remaining > 0 ? remaining : 0;
        } else {
            selectedAddonId = p.levelNumber; // For addon, levelNumber stores addonId
        }
    };
