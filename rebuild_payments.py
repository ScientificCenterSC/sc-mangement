with open('payments.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.index('<script>')
html_part = content[:idx]

new_script = """<script>
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';
    
    let currentUser = null;
    let allPayments = [];
    let allStudents = [];
    let allCourses = [];
    let allGroups = [];
    let allAddOns = [];
    let paymentChart, revenueChart;

    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    function showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) overlay.classList.add('show');
        else overlay.classList.remove('show');
    }

    async function apiCall(action, data = {}) {
        try {
            const response = await fetch(SCRIPT_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                body: JSON.stringify({ action, ...data })
            });
            const result = await response.json();
            if (result.success === false) throw new Error(result.message || 'خطأ');
            return result.data !== undefined ? result.data : result;
        } catch (error) {
            showToast(error.message || 'خطأ في الاتصال', 'error');
            throw error;
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        const userStr = sessionStorage.getItem('loggedInUser');
        if (!userStr) { window.location.href = 'index.html'; return; }
        try { currentUser = JSON.parse(userStr); } catch(e) { window.location.href = 'index.html'; return; }
        
        document.getElementById('userName').textContent = currentUser.fullName || currentUser.username;
        const roleNames = {1:'مدير النظام',2:'محاسب',3:'مدير دور',4:'مسؤول حجوزات',5:'مشاهد'};
        document.getElementById('userRole').textContent = roleNames[currentUser.roleId] || 'مستخدم';

        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.toggle('open'));
        document.getElementById('logoutBtn').addEventListener('click', () => { sessionStorage.removeItem('loggedInUser'); window.location.href = 'index.html'; });
        document.getElementById('searchBtn').addEventListener('click', () => filterAndRender());
        document.getElementById('searchInput').addEventListener('keypress', e => { if(e.key==='Enter') filterAndRender(); });
        document.getElementById('statusFilter').addEventListener('change', () => filterAndRender());
        document.getElementById('addPaymentBtn').addEventListener('click', () => openAddPaymentModal());
        document.getElementById('closeModal').addEventListener('click', () => closeModal());
        document.getElementById('cancelModal').addEventListener('click', () => closeModal());
        document.getElementById('savePayment').addEventListener('click', () => completePayment());
        document.getElementById('studentSearchInput').addEventListener('input', e => searchStudents(e.target.value));
        
        window.addEventListener('click', e => { if(e.target === document.getElementById('paymentModal')) closeModal(); });

        loadData();
    });

    async function loadData() {
        showLoading(true);
        try {
            const [pRes, sRes, cRes, gRes, aRes, dRes, fRes] = await Promise.all([
                apiCall('getAllPayments'),
                apiCall('getAllStudents'),
                apiCall('getAllCourses'),
                apiCall('getAllGroups'),
                apiCall('getAllAddOns'),
                apiCall('getAllDepartments'),
                apiCall('getAllFloors')
            ]);
            allPayments = pRes || [];
            allStudents = sRes || [];
            allCourses = cRes || [];
            allGroups = gRes || [];
            allAddOns = aRes || [];
            
            const deptFilter = document.getElementById('deptFilter');
            const floorFilter = document.getElementById('floorFilter');
            if (deptFilter) {
                deptFilter.innerHTML = '<option value="all">الكل</option>';
                if(dRes) dRes.forEach(d => deptFilter.innerHTML += `<option value="${d.id}">${d.name}</option>`);
            }
            if (floorFilter) {
                floorFilter.innerHTML = '<option value="all">الكل</option>';
                if(fRes) fRes.forEach(f => floorFilter.innerHTML += `<option value="${f.id}">${f.name}</option>`);
            }

            updateStats();
            updateCharts();
            filterAndRender();
        } catch (error) {
            console.error('Error:', error);
        }
        showLoading(false);
    }

    function updateStats() {
        let totalPaid = 0, totalRemaining = 0, overdueCount = 0;
        allPayments.forEach(p => {
            totalPaid += parseFloat(p.amountPaid) || 0;
            totalRemaining += parseFloat(p.remainingBalance) || 0;
            if ((parseFloat(p.remainingBalance) || 0) > 0) overdueCount++;
        });
        document.getElementById('totalPaid').textContent = totalPaid.toLocaleString() + ' ج.م';
        document.getElementById('totalRemaining').textContent = totalRemaining.toLocaleString() + ' ج.م';
        document.getElementById('totalStudents').textContent = allStudents.length;
        document.getElementById('overdueCount').textContent = overdueCount;
    }

    function updateCharts() {
        let paid = 0, remaining = 0;
        allPayments.forEach(p => { paid += parseFloat(p.amountPaid)||0; remaining += parseFloat(p.remainingBalance)||0; });
        
        const ctx1 = document.getElementById('paymentChart').getContext('2d');
        if (paymentChart) paymentChart.destroy();
        paymentChart = new Chart(ctx1, {
            type: 'doughnut',
            data: { labels: ['مدفوع', 'متبقي'], datasets: [{ data: [paid, remaining], backgroundColor: ['#2ecc71', '#e74c3c'], borderWidth: 0 }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', rtl: true } } }
        });

        const ctx2 = document.getElementById('revenueChart').getContext('2d');
        if (revenueChart) revenueChart.destroy();
        revenueChart = new Chart(ctx2, {
            type: 'line',
            data: { labels: ['يناير','فبراير','مارس','أبريل','مايو','يونيو'], datasets: [{ label: 'الإيرادات', data: [8500,9200,7800,10500,12400,14500], borderColor: '#3c6ec8', tension: 0.3, fill: true }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } } }
        });
    }

    function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;
        
        let filtered = [...allPayments];
        if (searchTerm) {
            filtered = filtered.filter(p => {
                const studentName = (p.studentName || '').toLowerCase();
                const student = allStudents.find(s => s.id == p.studentId);
                const code = (student?.code || '').toLowerCase();
                return studentName.includes(searchTerm) || code.includes(searchTerm);
            });
        }
        if (statusFilter === 'paid') filtered = filtered.filter(p => parseFloat(p.remainingBalance) === 0);
        else if (statusFilter === 'partial') filtered = filtered.filter(p => parseFloat(p.remainingBalance) > 0 && parseFloat(p.amountPaid) > 0);
        else if (statusFilter === 'unpaid') filtered = filtered.filter(p => !parseFloat(p.amountPaid));
        
        renderTable(filtered);
    }

    function renderTable(payments) {
        const tbody = document.getElementById('paymentsTableBody');
        if (!payments || payments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="11" style="text-align:center;padding:30px;color:var(--gray)">لا توجد مدفوعات</td></tr>';
            return;
        }
        
        tbody.innerHTML = payments.map(p => {
            const student = allStudents.find(s => s.id == p.studentId);
            const remaining = parseFloat(p.remainingBalance) || 0;
            const paid = parseFloat(p.amountPaid) || 0;
            const status = remaining === 0 ? 'مدفوع' : (paid > 0 ? 'جزئي' : 'غير مدفوع');
            const statusClass = remaining === 0 ? 'status-paid' : (paid > 0 ? 'status-partial' : 'status-unpaid');
            const date = p.paymentDate ? new Date(p.paymentDate).toLocaleDateString('ar-EG') : '-';
            const payType = p.paymentType === 'Course Payment' ? 'كورس' : p.paymentType === 'AddOn Payment' ? 'إضافة' : p.paymentType || '-';
            return `
                <tr>
                    <td><strong>${p.studentName || '-'}</strong></td>
                    <td>${student?.code || '-'}</td>
                    <td>المستوى ${p.levelNumber || 1}</td>
                    <td>${payType}</td>
                    <td style="color:var(--success);font-weight:600">${paid.toLocaleString()} ج.م</td>
                    <td>${(parseFloat(p.discountAmount)||0).toLocaleString()} ج.م</td>
                    <td>${(parseFloat(p.totalLevelFee)||0).toLocaleString()} ج.م</td>
                    <td style="color:${remaining>0?'var(--danger)':'var(--success)'};font-weight:600">${remaining.toLocaleString()} ج.م</td>
                    <td>${p.notes || '-'}</td>
                    <td>${date}</td>
                    <td class="action-buttons">
                        <button class="btn-icon btn-delete" onclick="deletePayment(${p.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function openAddPaymentModal() {
        document.getElementById('modalTitle').textContent = 'تسجيل دفعة جديدة';
        document.getElementById('studentSearchSection').style.display = 'block';
        document.getElementById('paymentFormSection').style.display = 'none';
        document.getElementById('savePayment').style.display = 'none';
        document.getElementById('studentSearchInput').value = '';
        document.getElementById('studentResults').innerHTML = '<div style="padding:15px;text-align:center;color:gray">ابحث باسم الطالب أو الكود...</div>';
        document.getElementById('paymentModal').classList.add('show');
    }

    function closeModal() {
        document.getElementById('paymentModal').classList.remove('show');
    }

    function searchStudents(query) {
        const results = document.getElementById('studentResults');
        if (!query.trim()) { results.innerHTML = '<div style="padding:15px;text-align:center;color:gray">ابحث باسم الطالب أو الكود...</div>'; return; }
        const filtered = allStudents.filter(s => (s.name||'').toLowerCase().includes(query.toLowerCase()) || (s.code||'').toLowerCase().includes(query.toLowerCase()));
        if (!filtered.length) { results.innerHTML = '<div style="padding:15px;text-align:center;color:gray">لا توجد نتائج</div>'; return; }
        results.innerHTML = filtered.map(s => `
            <div class="student-selector" onclick="selectStudent(${s.id}, '${s.name}', '${s.code||''}')">
                <div class="student-name">${s.name}</div>
                <div class="student-code">${s.code||''}</div>
            </div>
        `).join('');
    }

    window.selectStudent = function(id, name, code) {
        document.getElementById('selectedStudentId').value = id;
        document.getElementById('selectedStudentName').value = `${name} (${code})`;
        document.getElementById('studentSearchSection').style.display = 'none';
        document.getElementById('paymentFormSection').style.display = 'block';
        document.getElementById('savePayment').style.display = 'block';
        document.getElementById('paymentDate').valueAsDate = new Date();
        document.getElementById('discountAmount').value = '0';
        
        // Auto-fill course fee
        const student = allStudents.find(s => s.id == id);
        let courseFee = 0;
        if (student && student.groupId) {
            const group = allGroups.find(g => g.id == student.groupId);
            if (group && group.courseId) {
                const course = allCourses.find(c => c.id == group.courseId);
                if (course) courseFee = course.pricePerLevel || 0;
            }
        }
        document.getElementById('totalLevelFee').value = courseFee;
    };

    async function completePayment() {
        const studentId = document.getElementById('selectedStudentId').value;
        const amountPaid = parseFloat(document.getElementById('amountPaid').value);
        if (!studentId) { showToast('يرجى اختيار طالب أولاً', 'warning'); return; }
        if (!amountPaid || amountPaid <= 0) { showToast('المبلغ المدفوع مطلوب ويجب أن يكون أكبر من صفر', 'warning'); return; }
        
        const totalFee = parseFloat(document.getElementById('totalLevelFee').value) || 0;
        const discount = parseFloat(document.getElementById('discountAmount').value) || 0;
        const remaining = Math.max(0, totalFee - amountPaid - discount);
        
        const paymentData = {
            studentId,
            levelNumber: parseInt(document.getElementById('levelNumber').value) || 1,
            paymentType: document.getElementById('paymentType').value,
            totalLevelFee: totalFee,
            amountPaid,
            discountAmount: discount,
            remainingBalance: remaining,
            notes: document.getElementById('notes').value,
            paymentDate: document.getElementById('paymentDate').value,
            createdBy: currentUser.id
        };
        
        showLoading(true);
        try {
            await apiCall('savePayment', { paymentData });
            showToast('تم تسجيل الدفعة بنجاح', 'success');
            closeModal();
            loadData();
        } catch(e) {}
        showLoading(false);
    }

    window.deletePayment = async function(id) {
        if (!confirm('هل أنت متأكد من حذف هذه الدفعة؟')) return;
        showLoading(true);
        try {
            await apiCall('deletePayment', { paymentId: id });
            showToast('تم الحذف بنجاح', 'success');
            loadData();
        } catch(e) {}
        showLoading(false);
    };
</script>

<script src="sidebar.js"></script>
</body>
</html>
"""

new_content = html_part + new_script

with open('payments.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done - payments.html rebuilt")
