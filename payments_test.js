
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';

    let currentUser = null;
    let allPayments = [];
    let allStudents = [];
    let allCourses = [];
    let allGroups = [];
    let allAddOns = [];
    let allDepts = [];
    let allFloors = [];
    let paymentChart, revenueChart;

    // Modal state
    let selectedStudentId = null;
    let selectedLevelNumber = null;
    let selectedAddonId = null;
    let paymentCategory = null;
    let currentStep = 1;

    // =================== UTILS ===================

    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4500);
    }

    function showLoading(show, text = 'جاري التحميل...') {
        const overlay = document.getElementById('loadingOverlay');
        const textEl = overlay.querySelector('.loading-text');
        if (textEl) textEl.textContent = text;
        overlay.classList.toggle('show', show);
    }

    function setStatus(ok, text) {
        const dot = document.getElementById('statusDot');
        const txt = document.getElementById('statusText');
        if (dot) dot.style.color = ok ? '#2ecc71' : '#e74c3c';
        if (txt) txt.textContent = text;
    }

    // =================== API ===================

    async function apiCall(action, data = {}) {
        const body = JSON.stringify({ action, ...data });
        const response = await fetch(SCRIPT_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'text/plain;charset=utf-8' },
            body
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const result = await response.json();
        if (result.success === false) throw new Error(result.message || 'خطأ من الخادم');
        return result.data !== undefined ? result.data : result;
    }

    async function safeApiCall(action, data = {}, fallback = []) {
        try {
            const result = await apiCall(action, data);
            return result || fallback;
        } catch (e) {
            console.warn(`[${action}] failed:`, e.message);
            return fallback;
        }
    }

    // =================== INIT ===================
    
    // Bulk Payment Elements
    const bulkPaymentBtn = document.getElementById('bulkPaymentBtn');
    const bulkPaymentModal = document.getElementById('bulkPaymentModal');
    const closeBulkModalBtn = document.getElementById('closeBulkModal');
    const cancelBulkModalBtn = document.getElementById('cancelBulkModal');
    const bulkDeptFilter = document.getElementById('bulkDeptFilter');
    const bulkCourseFilter = document.getElementById('bulkCourseFilter');
    const bulkGroupFilter = document.getElementById('bulkGroupFilter');
    const bulkLevelFilter = document.getElementById('bulkLevelFilter');
    const bulkStudentsTableBody = document.getElementById('bulkStudentsTableBody');
    const selectAllBulk = document.getElementById('selectAllBulk');
    const saveBulkPaymentsBtn = document.getElementById('saveBulkPaymentsBtn');

    if (bulkPaymentBtn) {
        bulkPaymentBtn.addEventListener('click', () => {
            bulkDeptFilter.innerHTML = '<option value="">اختر القسم</option>';
            allDepts.forEach(d => bulkDeptFilter.innerHTML += `<option value="${d.id}">${d.name}</option>`);
            bulkCourseFilter.innerHTML = '<option value="">اختر الكورس</option>';
            bulkGroupFilter.innerHTML = '<option value="">اختر الجروب</option>';
            bulkLevelFilter.innerHTML = '<option value="">اختر المستوى</option>';
            bulkStudentsTableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">اختر القسم والكورس والجروب والمستوى لظهور الطلاب</td></tr>';
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
            bulkLevelFilter.innerHTML = '<option value="">اختر المستوى</option>';
            if (deptId) {
                const courses = allCourses.filter(c => c.deptId == deptId);
                courses.forEach(c => bulkCourseFilter.innerHTML += `<option value="${c.id}">${c.courseName||c.name}</option>`);
            }
            renderBulkStudents();
        });
    }

    if (bulkCourseFilter) {
        bulkCourseFilter.addEventListener('change', () => {
            const courseId = bulkCourseFilter.value;
            bulkGroupFilter.innerHTML = '<option value="">اختر الجروب</option>';
            bulkLevelFilter.innerHTML = '<option value="">اختر المستوى</option>';
            if (courseId) {
                const groups = allGroups.filter(g => g.courseId == courseId);
                groups.forEach(g => bulkGroupFilter.innerHTML += `<option value="${g.id}">${g.name}</option>`);
                
                const course = allCourses.find(c => String(c.id) === String(courseId));
                if (course && course.levels) {
                    for(let i=1; i<=parseInt(course.levels); i++) {
                        bulkLevelFilter.innerHTML += `<option value="${i}">مستوى ${i}</option>`;
                    }
                }
            }
            renderBulkStudents();
        });
    }

    if (bulkGroupFilter) bulkGroupFilter.addEventListener('change', renderBulkStudents);
    if (bulkLevelFilter) bulkLevelFilter.addEventListener('change', renderBulkStudents);

    function renderBulkStudents() {
        const groupId = bulkGroupFilter.value;
        const levelNumber = bulkLevelFilter.value;
        
        if (!groupId || !levelNumber) {
            bulkStudentsTableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">اختر الجروب والمستوى لظهور الطلاب</td></tr>';
            return;
        }

        const students = allStudents.filter(s => String(s.groupId) === String(groupId));
        if (students.length === 0) {
            bulkStudentsTableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">لا يوجد طلاب في هذا الجروب</td></tr>';
            return;
        }

        // Calculate previous paid for this level for each student
        const prevPaidMap = {};
        allPayments.forEach(p => {
            if (String(p.levelNumber) === String(levelNumber) && p.paymentType === 'Course Payment') {
                if (!prevPaidMap[p.studentId]) prevPaidMap[p.studentId] = { paid: 0, discount: 0 };
                prevPaidMap[p.studentId].paid += parseFloat(p.amountPaid) || 0;
                prevPaidMap[p.studentId].discount += parseFloat(p.discountAmount) || 0;
            }
        });

        bulkStudentsTableBody.innerHTML = students.map(s => {
            const prev = prevPaidMap[s.id] || { paid: 0, discount: 0 };
            const prevText = prev.paid > 0 ? `دفع: ${prev.paid} | خصم: ${prev.discount}` : 'لم يدفع';
            return `<tr>
                <td><input type="checkbox" class="bulk-student-check" value="${s.id}" checked></td>
                <td>${s.name}</td>
                <td>${s.code || '-'}</td>
                <td style="font-size: 12px; color: var(--gray);">${prevText}</td>
                <td><input type="number" class="bulk-amount" data-id="${s.id}" placeholder="0" style="width: 80px; padding: 5px;"></td>
                <td><input type="number" class="bulk-discount" data-id="${s.id}" placeholder="0" style="width: 80px; padding: 5px;"></td>
                <td><input type="text" class="bulk-receipt" data-id="${s.id}" placeholder="الإيصال" style="width: 100px; padding: 5px;"></td>
            </tr>`;
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
            const levelNumber = bulkLevelFilter.value;
            const courseId = bulkCourseFilter.value;
            
            if (!groupId || !levelNumber) return showToast('الرجاء تحديد الجروب والمستوى', 'warning');
            
            const course = allCourses.find(c => String(c.id) === String(courseId));
            const totalFee = course ? (parseFloat(course.pricePerLevel) || 0) : 0;
            
            const payments = [];
            const checks = document.querySelectorAll('.bulk-student-check:checked');
            checks.forEach(c => {
                const sid = c.value;
                const amountInput = document.querySelector(`.bulk-amount[data-id="${sid}"]`).value;
                const discountInput = document.querySelector(`.bulk-discount[data-id="${sid}"]`).value;
                const receiptInput = document.querySelector(`.bulk-receipt[data-id="${sid}"]`).value;
                
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
                        paymentDate: new Date().toISOString().substring(0, 10)
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
        
        openAddPaymentModal(); 
        hide('step1'); hide('step2'); show('step3');
        
        document.getElementById('amountPaid').value = p.amountPaid || 0;
        document.getElementById('discountAmount').value = p.discountAmount || 0;
        document.getElementById('receiptNumber').value = p.receipt_number || p.receiptNumber || '';
        document.getElementById('notes').value = p.notes || '';
        document.getElementById('paymentDate').value = p.paymentDate ? new Date(p.paymentDate).toISOString().substring(0, 10) : new Date().toISOString().substring(0, 10);
        
        selectedStudent = allStudents.find(s => String(s.id) === String(p.studentId));
        paymentCategory = (p.paymentType === 'Course Payment') ? 'course' : 'addon';
        if (paymentCategory === 'course') {
            selectedLevelNumber = p.levelNumber;
            document.getElementById('totalLevelFee').value = p.totalLevelFee || p.totalFee || 0;
        } else {
            selectedAddonId = p.levelNumber; 
        }
    };

    document.addEventListener('DOMContentLoaded', function() {
        const userStr = sessionStorage.getItem('loggedInUser');
        if (!userStr) { window.location.href = 'index.html'; return; }
        try { currentUser = JSON.parse(userStr); } catch(e) { window.location.href = 'index.html'; return; }

        document.getElementById('userName').textContent = currentUser.fullName || currentUser.username || 'مستخدم';
        const roleNames = {1:'مدير النظام',2:'محاسب',3:'مدير دور',4:'مسؤول حجوزات',5:'مشاهد'};
        document.getElementById('userRole').textContent = roleNames[currentUser.roleId] || 'مستخدم';

        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.toggle('open'));
        document.getElementById('logoutBtn').addEventListener('click', () => { sessionStorage.removeItem('loggedInUser'); window.location.href = 'index.html'; });
        document.getElementById('searchBtn').addEventListener('click', filterAndRender);
        document.getElementById('searchInput').addEventListener('keypress', e => { if(e.key==='Enter') filterAndRender(); });
        document.getElementById('statusFilter').addEventListener('change', filterAndRender);
        document.getElementById('deptFilter').addEventListener('change', () => { updateProgramFilters(); updateGroupFilters(); filterAndRender(); });
        document.getElementById('levelFilter').addEventListener('change', () => { updateProgramFilters(); updateGroupFilters(); filterAndRender(); });
        document.getElementById('programFilter').addEventListener('change', () => { updateGroupFilters(); filterAndRender(); });
        document.getElementById('groupFilter').addEventListener('change', filterAndRender);
        document.getElementById('addPaymentBtn').addEventListener('click', openAddPaymentModal);
        document.getElementById('closeModal').addEventListener('click', closeModal);
        document.getElementById('cancelModal').addEventListener('click', closeModal);
        document.getElementById('studentSearchInput').addEventListener('input', e => searchStudents(e.target.value));
        window.addEventListener('click', e => { if(e.target === document.getElementById('paymentModal')) closeModal(); });

        loadData();
    });

    // =================== LOAD DATA ===================

    async function loadData() {
        showLoading(true, 'جاري تحميل البيانات...');
        setStatus(false, 'جاري الاتصال...');

        try {
            // Load sequentially to avoid race conditions / quota issues
            allStudents = await safeApiCall('getAllStudents', {}, []);
            allPayments = await safeApiCall('getAllPayments', {}, []);
            allCourses  = await safeApiCall('getAllCourses', {}, []);
            allGroups   = await safeApiCall('getAllGroups', {}, []);
            allAddOns   = await safeApiCall('getAllAddOns', {}, []);
            allDepts    = await safeApiCall('getAllDepartments', {}, []);
            allFloors   = await safeApiCall('getAllFloors', {}, []);

            setStatus(true, `متصل ✓ (${allPayments.length} دفعة)`);

            // Populate filter dropdowns
            populateFilters();
            updateStats();
            updateCharts();
            filterAndRender();

        } catch (error) {
            console.error('loadData error:', error);
            setStatus(false, 'خطأ في الاتصال');
            showToast('خطأ في الاتصال بالخادم: ' + error.message, 'error');
            document.getElementById('paymentsTableBody').innerHTML =
                `<tr><td colspan="12" style="text-align:center;padding:40px;color:var(--danger);">
                    <i class="fas fa-exclamation-triangle" style="font-size:30px;display:block;margin-bottom:10px;"></i>
                    <strong>خطأ في تحميل البيانات</strong><br>
                    <small style="color:var(--gray);">${error.message}</small><br><br>
                    <button onclick="loadData()" style="padding:8px 20px;background:var(--primary-blue);color:white;border:none;border-radius:8px;cursor:pointer;font-family:inherit;">
                        <i class="fas fa-redo"></i> إعادة المحاولة
                    </button>
                </td></tr>`;
        }

        showLoading(false);
    }

    // =================== POPULATE FILTERS ===================

    function populateFilters() {
        const deptSel = document.getElementById('deptFilter');

        if(deptSel) {
            deptSel.innerHTML = '<option value="all">الكل</option>';
            allDepts.forEach(d => {
                deptSel.innerHTML += `<option value="${d.id}">${d.name}</option>`;
            });
        }
        
        updateProgramFilters();
        updateGroupFilters();
    }

    function updateProgramFilters() {
        const deptId = document.getElementById('deptFilter')?.value;
        const programFilter = document.getElementById('programFilter');
        
        if (programFilter) {
            let filteredCourses = typeof allCourses !== 'undefined' ? allCourses : [];
            if (deptId !== 'all' && deptId) {
                filteredCourses = filteredCourses.filter(c => c.deptId == deptId);
            }
            let programHtml = '<option value="all">الكل</option>';
            filteredCourses.forEach(c => programHtml += `<option value="${c.id}">${c.courseName || c.name}</option>`);
            programFilter.innerHTML = programHtml;
        }
    }

    function updateGroupFilters() {
        const deptId = document.getElementById('deptFilter')?.value;
        const levelId = document.getElementById('levelFilter')?.value;
        const progId = document.getElementById('programFilter')?.value;
        
        const groupFilter = document.getElementById('groupFilter');
        
        if (groupFilter) {
            let filteredGroups = typeof allGroups !== 'undefined' ? allGroups : [];
            if (deptId !== 'all' && deptId) filteredGroups = filteredGroups.filter(g => g.deptId == deptId);
            if (levelId !== 'all' && levelId) filteredGroups = filteredGroups.filter(g => String(g.level) === String(levelId));
            if (progId !== 'all' && progId) filteredGroups = filteredGroups.filter(g => g.courseId == progId);
            
            let options = '<option value="all">الكل</option>';
            filteredGroups.forEach(g => {
                options += `<option value="${g.id}">${g.name}</option>`;
            });
            groupFilter.innerHTML = options;
        }
    }

    window.clearFilters = function() {
        document.getElementById('searchInput').value = '';
        document.getElementById('deptFilter').value = 'all';
        document.getElementById('levelFilter').value = 'all';
        document.getElementById('programFilter').value = 'all';
        document.getElementById('groupFilter').value = 'all';
        document.getElementById('statusFilter').value = 'all';
        updateProgramFilters();
        updateGroupFilters();
        filterAndRender();
    };

    // =================== STATS ===================

    function updateStats() {
        let totalPaid = 0, totalRemaining = 0, overdueCount = 0;

        // Get latest remaining per student-level combo
        const latestMap = {};
        allPayments.forEach(p => {
            const key = `${p.studentId}_${p.levelNumber}_${p.paymentType}`;
            totalPaid += parseFloat(p.amountPaid) || 0;
            if (!latestMap[key] || (p.id > latestMap[key].id)) {
                latestMap[key] = p;
            }
        });
        Object.values(latestMap).forEach(p => {
            const r = parseFloat(p.remainingBalance) || 0;
            totalRemaining += r;
            if (r > 0) overdueCount++;
        });

        document.getElementById('totalPaid').textContent = totalPaid.toLocaleString('ar-EG') + ' ج.م';
        document.getElementById('totalRemaining').textContent = totalRemaining.toLocaleString('ar-EG') + ' ج.م';
        document.getElementById('totalStudents').textContent = allStudents.length;
        document.getElementById('overdueCount').textContent = overdueCount;
    }

    function updateCharts() {
        let paid = 0, remaining = 0;
        allPayments.forEach(p => { paid += parseFloat(p.amountPaid)||0; remaining += parseFloat(p.remainingBalance)||0; });

        const ctx1 = document.getElementById('paymentChart');
        if (paymentChart) paymentChart.destroy();
        paymentChart = new Chart(ctx1.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['مدفوع', 'متبقي'],
                datasets: [{ data: [paid, remaining], backgroundColor: ['#2ecc71', '#e74c3c'], borderWidth: 0 }]
            },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', rtl: true } } }
        });

        const ctx2 = document.getElementById('revenueChart');
        if (revenueChart) revenueChart.destroy();
        const months = allPayments.reduce((acc, p) => {
            if (!p.paymentDate) return acc;
            const d = new Date(p.paymentDate);
            if (isNaN(d)) return acc;
            const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;
            acc[key] = (acc[key] || 0) + (parseFloat(p.amountPaid) || 0);
            return acc;
        }, {});
        const sortedKeys = Object.keys(months).sort();
        const labels = sortedKeys.length > 0 ? sortedKeys : ['لا توجد بيانات'];
        const values = sortedKeys.length > 0 ? sortedKeys.map(k => months[k]) : [0];

        revenueChart = new Chart(ctx2.getContext('2d'), {
            type: 'line',
            data: {
                labels,
                datasets: [{ label: 'الإيرادات', data: values, borderColor: '#3c6ec8', tension: 0.3, fill: true, backgroundColor: 'rgba(60,110,200,0.08)', pointBackgroundColor: '#3c6ec8' }]
            },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } } }
        });
    }

    // =================== FILTER & RENDER ===================

    function filterAndRender() {
        const searchTerm = (document.getElementById('searchInput').value || '').toLowerCase().trim();
        const statusFilter = document.getElementById('statusFilter')?.value || 'all';
        const deptFilterVal = document.getElementById('deptFilter')?.value || 'all';
        const levelFilterVal = document.getElementById('levelFilter')?.value || 'all';
        const programFilterVal = document.getElementById('programFilter')?.value || 'all';
        const groupFilterVal = document.getElementById('groupFilter')?.value || 'all';

        // Group by student + level + type
        const grouped = {};
        allPayments.forEach(p => {
            const key = `${p.studentId}__${p.levelNumber}__${p.paymentType}`;
            if (!grouped[key]) {
                grouped[key] = { ...p, allAmounts: [], totalPaid: 0, totalDiscount: 0 };
            }
            grouped[key].allAmounts.push({
                amount: parseFloat(p.amountPaid) || 0,
                date: p.paymentDate,
                id: p.id,
                receipt: p.receipt_number || p.receiptNumber || '-'
            });
            grouped[key].totalPaid += parseFloat(p.amountPaid) || 0;
            grouped[key].totalDiscount += parseFloat(p.discountAmount) || 0;
            // Always use latest remaining balance
            if (!grouped[key]._lastId || p.id >= grouped[key]._lastId) {
                grouped[key]._lastId = p.id;
                grouped[key].remainingBalance = parseFloat(p.remainingBalance) || 0;
                grouped[key].totalLevelFee = parseFloat(p.totalLevelFee) || parseFloat(p.totalFee) || 0;
            }
        });

        // Add students who haven't paid anything yet for the target level
        if (typeof allStudents !== 'undefined' && typeof allGroups !== 'undefined' && typeof allCourses !== 'undefined') {
            const targetLevel = levelFilterVal === 'all' ? '1' : levelFilterVal;
            allStudents.forEach(s => {
                if (s.groupId) {
                    const group = allGroups.find(g => String(g.id) === String(s.groupId));
                    if (group) {
                        const course = allCourses.find(c => String(c.id) === String(group.courseId));
                        if (course) {
                            const durationLevels = parseInt(course.durationLevels) || 1;
                            // Only add debt if the target level is within the course's duration
                            if (parseInt(targetLevel) <= durationLevels) {
                                // Check if student has ANY payment for this specific target level
                                const hasPayment = Object.values(grouped).some(p => String(p.studentId) === String(s.id) && String(p.levelNumber) === String(targetLevel));
                                
                                if (!hasPayment) {
                                    const coursePrice = parseFloat(course.pricePerLevel) || 0;
                                    
                                    const key = `${s.id}__${targetLevel}__Unpaid`;
                                    grouped[key] = {
                                        studentId: s.id,
                                        studentName: s.name,
                                        levelNumber: targetLevel,
                                        paymentType: '-',
                                        paymentDate: s.createdAt || new Date().toISOString(),
                                        amountPaid: 0,
                                        remainingBalance: coursePrice,
                                        totalLevelFee: coursePrice,
                                        totalDiscount: 0,
                                        allAmounts: []
                                    };
                                }
                            }
                        }
                    }
                }
            });
        }

        let rows = Object.values(grouped);

        // Search
        if (searchTerm) {
            rows = rows.filter(p => {
                const s = allStudents.find(st => String(st.id) === String(p.studentId));
                const name = (p.studentName || s?.name || '').toLowerCase();
                const code = (s?.code || '').toLowerCase();
                return name.includes(searchTerm) || code.includes(searchTerm);
            });
        }

        // Dept filter
        if (deptFilterVal !== 'all') {
            rows = rows.filter(p => {
                const s = allStudents.find(st => String(st.id) === String(p.studentId));
                return s && String(s.deptId) === String(deptFilterVal);
            });
        }

        // Level filter
        if (levelFilterVal !== 'all') {
            rows = rows.filter(p => String(p.levelNumber) === String(levelFilterVal));
        }

        // Program filter
        if (programFilterVal !== 'all') {
            rows = rows.filter(p => {
                const s = allStudents.find(st => String(st.id) === String(p.studentId));
                if (!s || !s.groupId) return false;
                const g = allGroups.find(gr => String(gr.id) === String(s.groupId));
                return g && String(g.courseId) === String(programFilterVal);
            });
        }

        // Group filter
        if (groupFilterVal !== 'all') {
            rows = rows.filter(p => {
                const s = allStudents.find(st => String(st.id) === String(p.studentId));
                return s && String(s.groupId) === String(groupFilterVal);
            });
        }

        // Status filter
        if (statusFilter === 'paid') {
            rows = rows.filter(p => p.totalPaid > 0 && parseFloat(p.remainingBalance) === 0);
        } else if (statusFilter === 'partial') {
            rows = rows.filter(p => p.totalPaid > 0 && parseFloat(p.remainingBalance) > 0);
        } else if (statusFilter === 'unpaid') {
            rows = rows.filter(p => p.totalPaid <= 0);
        }

        renderTable(rows);
    }

    function renderTable(rows) {
        const tbody = document.getElementById('paymentsTableBody');
        if (!rows || rows.length === 0) {
            tbody.innerHTML = `<tr><td colspan="12" style="text-align:center;padding:50px;color:var(--gray);">
                <i class="fas fa-inbox" style="font-size:40px;opacity:0.25;display:block;margin-bottom:10px;"></i>
                لا توجد مدفوعات
            </td></tr>`;
            return;
        }

        tbody.innerHTML = rows.map(p => {
            const student = allStudents.find(s => String(s.id) === String(p.studentId));
            const group = student?.groupId ? allGroups.find(g => String(g.id) === String(student.groupId)) : null;
            const courseName = group?.courseName || group?.name || '-';

            const remaining = parseFloat(p.remainingBalance) || 0;
            const paid = p.totalPaid || 0;
            const totalFee = parseFloat(p.totalLevelFee) || parseFloat(p.totalFee) || 0;
            const discountTotal = p.totalDiscount || 0;

            let statusLabel, statusClass;
            if (paid > 0 && remaining === 0) {
                statusLabel = 'مدفوع بالكامل'; statusClass = 'status-paid';
            } else if (paid > 0 && remaining > 0) {
                statusLabel = 'جزئي'; statusClass = 'status-partial';
            } else {
                statusLabel = 'غير مدفوع'; statusClass = 'status-unpaid';
            }

            let lastReceipt = '-';
            let dateStr = '-';
            if (p.allAmounts && p.allAmounts.length > 0) {
                const lastPayment = p.allAmounts[p.allAmounts.length - 1];
                lastReceipt = lastPayment.receipt;
                const lastDate = lastPayment.date;
                if (lastDate) {
                    try { dateStr = new Date(lastDate).toLocaleDateString('ar-EG'); } catch(e) { dateStr = lastDate; }
                }
            }

            const levelOrAddon = p.paymentType === 'Course Payment' 
                ? `Level ${p.levelNumber || 1}` 
                : `<span style="color:var(--gold);"><i class="fas fa-plus-circle"></i> إضافة</span>`;

            let paidDisplay = `<strong>${paid.toLocaleString('ar-EG')}</strong> ج.م`;
            if (p.allAmounts && p.allAmounts.length > 1) {
                const breakdown = p.allAmounts.map(a => `${a.amount.toLocaleString('ar-EG')} ج.م (${a.receipt})`).join(' + ');
                paidDisplay = `<span title="${breakdown}" style="cursor:help;border-bottom:1px dashed var(--primary-blue);">
                    <strong>${paid.toLocaleString('ar-EG')}</strong> ج.م
                    <small style="color:var(--primary-blue);font-weight:700;">(${p.allAmounts.length} دفعات)</small>
                </span>`;
            }

            return `<tr>
                <td style="font-size:12px;color:var(--gray);">${dateStr}</td>
                <td>
                    <strong style="color:var(--dark-blue);">${p.studentName || student?.name || '-'}</strong>
                    <br><code style="background:#f0f4ff;padding:2px 7px;border-radius:5px;font-size:10px;">${student?.code || '-'}</code>
                </td>
                <td><span style="background:#e8f0fe;color:var(--dark-blue);padding:3px 10px;border-radius:10px;font-weight:800;font-size:13px;">${levelOrAddon}</span></td>
                <td><strong style="color:var(--dark-blue);">${lastReceipt}</strong></td>
                <td style="color:var(--success);font-weight:600;">${paidDisplay}</td>
                <td style="color:var(--danger);">${discountTotal > 0 ? '-' + discountTotal.toLocaleString('ar-EG') + ' ج.م' : '-'}</td>
                <td style="color:var(--gray);">${totalFee > 0 ? totalFee.toLocaleString('ar-EG') + ' ج.م' : '-'}</td>
                <td style="font-weight:700;color:${remaining > 0 ? 'var(--danger)' : 'var(--success)'};">
                    ${remaining > 0 ? remaining.toLocaleString('ar-EG') + ' ج.م' : '<i class="fas fa-check-circle"></i> مسدد'}
                </td>
                <td><span class="status-badge ${statusClass}">${statusLabel}</span></td>
                <td style="font-size:12px;color:var(--gray);">${dateStr}</td>
                    <td class="action-buttons">
                        <!-- Add edit button for individual history payments if needed -->
                        <button class="btn-icon btn-edit" onclick="editPayment(${p.id})" title="تعديل"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon btn-delete" onclick="deletePaymentById(${p.id})" title="حذف"><i class="fas fa-trash"></i></button>
                    </td>
            </tr>`;
        }).join('');
    }

    // =================== MODAL FLOW ===================

    function openAddPaymentModal() {
        if (allStudents.length === 0) {
            showToast('لا يوجد طلاب في النظام', 'warning');
            return;
        }
        resetModal();
        document.getElementById('paymentModal').classList.add('show');
    }

    function resetModal() {
        selectedStudentId = null;
        selectedLevelNumber = null;
        selectedAddonId = null;
        paymentCategory = null;
        currentStep = 1;

        show('step1'); hide('step2'); hide('step3Level'); hide('step3Addon');
        document.getElementById('backBtn').style.display = 'none';
        document.getElementById('savePayment').style.display = 'none';
        document.getElementById('studentSearchInput').value = '';
        document.getElementById('studentResults').innerHTML =
            `<div style="padding:20px;text-align:center;color:var(--gray);">
                <i class="fas fa-search" style="font-size:30px;opacity:0.3;display:block;margin-bottom:8px;"></i>
                ابحث باسم الطالب أو الكود
            </div>`;
        updateStepIndicator(1);
    }

    function closeModal() {
        document.getElementById('paymentModal').classList.remove('show');
    }

    function show(id) { const el = document.getElementById(id); if(el) el.style.display = 'block'; }
    function hide(id) { const el = document.getElementById(id); if(el) el.style.display = 'none'; }

    function updateStepIndicator(step) {
        for (let i = 1; i <= 3; i++) {
            const dot = document.getElementById(`step-dot-${i}`);
            if (!dot) continue;
            dot.className = 'step-dot ' + (i < step ? 'done' : i === step ? 'active' : 'inactive');
        }
        const line1 = document.getElementById('step-line-1');
        const line2 = document.getElementById('step-line-2');
        if (line1) line1.className = 'step-line' + (step > 1 ? ' done' : '');
        if (line2) line2.className = 'step-line' + (step > 2 ? ' done' : '');
    }

    window.goBack = function() {
        if (paymentCategory !== null) {
            paymentCategory = null;
            selectedLevelNumber = null;
            selectedAddonId = null;
            hide('step3Level'); hide('step3Addon');
            document.getElementById('editPaymentId').value = '';
            document.getElementById('modalTitle').textContent = 'تسجيل دفعة جديدة';
            show('step2');
            document.getElementById('savePayment').style.display = 'none';
            updateStepIndicator(2);
        } else {
            hide('step2');
            show('step1');
            document.getElementById('backBtn').style.display = 'none';
            selectedStudentId = null;
            updateStepIndicator(1);
        }
    };

    function searchStudents(query) {
        const results = document.getElementById('studentResults');
        query = (query || '').trim();
        if (!query) {
            results.innerHTML = `<div style="padding:20px;text-align:center;color:var(--gray);">
                <i class="fas fa-search" style="font-size:30px;opacity:0.3;display:block;margin-bottom:8px;"></i>
                ابحث باسم الطالب أو الكود
            </div>`;
            return;
        }
        const q = query.toLowerCase();
        const filtered = allStudents.filter(s =>
            (s.name||'').toLowerCase().includes(q) ||
            (s.code||'').toLowerCase().includes(q)
        );
        if (!filtered.length) {
            results.innerHTML = `<div style="padding:20px;text-align:center;color:var(--gray);">لا توجد نتائج لـ "${query}"</div>`;
            return;
        }
        results.innerHTML = filtered.map(s => {
            const group = s.groupId ? allGroups.find(g => String(g.id) === String(s.groupId)) : null;
            const groupName = group?.name || group?.courseName || '';
            return `<div class="student-result-item" onclick="selectStudent(${s.id})">
                <div class="student-result-name">${s.name}</div>
                <div class="student-result-meta">
                    <span style="color:var(--primary-blue);">${s.code || ''}</span>
                    ${groupName ? `<span style="margin-right:8px;color:var(--gray);">• ${groupName}</span>` : ''}
                </div>
            </div>`;
        }).join('');
    }

    window.selectStudent = function(id) {
        const student = allStudents.find(s => String(s.id) === String(id));
        if (!student) return;
        selectedStudentId = id;

        hide('step1');
        show('step2');
        document.getElementById('backBtn').style.display = 'inline-flex';
        updateStepIndicator(2);

        let courseName = 'غير محدد';
        if (student.groupId) {
            const group = allGroups.find(g => String(g.id) === String(student.groupId));
            if (group) courseName = group.courseName || group.name || courseName;
        }
        document.getElementById('selectedStudentDisplay').textContent = `${student.name}  ${student.code ? '(' + student.code + ')' : ''}`;
        document.getElementById('selectedStudentCourse').innerHTML = `<i class="fas fa-book-open"></i> الكورس: ${courseName}`;
    };

    window.choosePaymentCategory = function(cat) {
        paymentCategory = cat;
        hide('step2');
        updateStepIndicator(3);

        if (cat === 'level') {
            show('step3Level');
            const student = allStudents.find(s => String(s.id) === String(selectedStudentId));
            if (student) {
                document.getElementById('studentInfoBar2').textContent = `${student.name}  ${student.code ? '(' + student.code + ')' : ''}`;
            }
            buildLevelButtons();
        } else {
            show('step3Addon');
            const student = allStudents.find(s => String(s.id) === String(selectedStudentId));
            if (student) {
                document.getElementById('studentInfoBar3').textContent = `${student.name}  ${student.code ? '(' + student.code + ')' : ''}`;
            }
            buildAddonList();
        }
    };

    // =================== LEVEL BUTTONS ===================

    function buildLevelButtons() {
        const student = allStudents.find(s => String(s.id) === String(selectedStudentId));
        if (!student) return;

        let totalLevels = 1;
        let pricePerLevel = 0;

        if (student.groupId) {
            const group = allGroups.find(g => String(g.id) === String(student.groupId));
            if (group) {
                const course = allCourses.find(c => String(c.id) === String(group.courseId));
                if (course) {
                    totalLevels = parseInt(course.durationLevels) || parseInt(group.levelCount) || 1;
                    pricePerLevel = parseFloat(course.pricePerLevel) || 0;
                }
            }
        }

        const container = document.getElementById('levelButtons');
        hide('levelPaymentDetails');
        hide('levelPayForm');

        if (totalLevels === 0 || totalLevels > 20) {
            container.innerHTML = `<div style="color:var(--gray);padding:10px;text-align:center;">
                لا توجد مستويات محددة لهذا الطالب
            </div>`;
            return;
        }

        container.innerHTML = '';

        for (let i = 1; i <= totalLevels; i++) {
            const levelPayments = allPayments.filter(p =>
                String(p.studentId) === String(selectedStudentId) &&
                String(p.levelNumber) === String(i) &&
                p.paymentType === 'Course Payment'
            );
            const totalPaid = levelPayments.reduce((sum, p) => sum + (parseFloat(p.amountPaid)||0), 0);
            const totalDiscount = levelPayments.reduce((sum, p) => sum + (parseFloat(p.discountAmount)||0), 0);
            const storedFee = levelPayments.length > 0
                ? (parseFloat(levelPayments[0].totalLevelFee) || parseFloat(levelPayments[0].totalFee) || pricePerLevel)
                : pricePerLevel;
            const remaining = Math.max(0, storedFee - totalPaid - totalDiscount);
            const isPaid = totalPaid > 0 && remaining === 0;
            const isPartial = totalPaid > 0 && remaining > 0;

            let bg, border, badge;
            if (isPaid) {
                bg = '#e8f5e9'; border = '#4caf50';
                badge = `<div style="color:#2e7d32;font-size:11px;margin-top:5px;"><i class="fas fa-check-circle"></i> مدفوع</div>`;
            } else if (isPartial) {
                bg = '#fff3e0'; border = '#ff9800';
                badge = `<div style="color:#e65100;font-size:11px;margin-top:5px;"><i class="fas fa-exclamation-circle"></i> متبقي ${remaining.toLocaleString()}</div>`;
            } else {
                bg = 'white'; border = '#dee2e6';
                badge = `<div style="color:#c62828;font-size:11px;margin-top:5px;"><i class="fas fa-times-circle"></i> لم يُدفع</div>`;
            }

            const btn = document.createElement('div');
            btn.className = 'level-btn';
            btn.style.cssText = `border-color:${border};background:${bg};`;
            btn.innerHTML = `
                <div style="font-weight:800;font-size:18px;color:var(--dark-blue);">L${i}</div>
                <div style="font-size:12px;color:var(--gray);margin:3px 0;">${storedFee > 0 ? storedFee.toLocaleString() + ' ج.م' : 'غير محدد'}</div>
                ${totalPaid > 0 ? `<div style="font-size:11px;color:var(--success);font-weight:700;">✓ ${totalPaid.toLocaleString()} ج.م</div>` : ''}
                ${badge}
            `;
            btn.onclick = () => selectLevel(i, storedFee || pricePerLevel);
            container.appendChild(btn);
        }
    }

    window.selectLevel = function(levelNum, pricePerLevel) {
        selectedLevelNumber = levelNum;

        // Highlight selected
        document.querySelectorAll('.level-btn').forEach(b => b.style.boxShadow = '');
        event && event.currentTarget && (event.currentTarget.style.boxShadow = '0 0 0 3px var(--primary-blue)');

        const levelPayments = allPayments.filter(p =>
            String(p.studentId) === String(selectedStudentId) &&
            String(p.levelNumber) === String(levelNum) &&
            p.paymentType === 'Course Payment'
        );
        const totalPaid = levelPayments.reduce((sum, p) => sum + (parseFloat(p.amountPaid)||0), 0);
        const totalDiscount = levelPayments.reduce((sum, p) => sum + (parseFloat(p.discountAmount)||0), 0);
        const storedFee = levelPayments.length > 0
            ? (parseFloat(levelPayments[0].totalLevelFee) || parseFloat(levelPayments[0].totalFee) || pricePerLevel)
            : pricePerLevel;
        const remaining = Math.max(0, storedFee - totalPaid - totalDiscount);
        const isPaid = totalPaid > 0 && remaining === 0;

        const details = document.getElementById('levelPaymentDetails');
        const banner  = document.getElementById('levelStatusBanner');
        const history = document.getElementById('levelPayHistory');
        const form    = document.getElementById('levelPayForm');

        details.style.display = 'block';

        if (isPaid) {
            banner.style.cssText = 'padding:12px;border-radius:8px;background:#e8f5e9;color:#2e7d32;text-align:center;font-weight:700;margin-bottom:12px;';
            banner.innerHTML = `<i class="fas fa-check-circle" style="font-size:20px;"></i><br>هذا المستوى مدفوع بالكامل ✅<br><small>إجمالي المدفوع: ${totalPaid.toLocaleString()} ج.م</small>`;
            form.style.display = 'none';
            document.getElementById('savePayment').style.display = 'none';
        } else {
            if (totalPaid === 0 && totalDiscount === 0) {
                banner.style.cssText = 'padding:12px;border-radius:8px;background:#fdecea;color:#c62828;text-align:center;font-weight:700;margin-bottom:12px;';
                banner.innerHTML = `<i class="fas fa-times-circle"></i> لم يتم الدفع بعد<br><small>المطلوب: <strong>${storedFee.toLocaleString()} ج.م</strong></small>`;
            } else {
                banner.style.cssText = 'padding:12px;border-radius:8px;background:#fff3e0;color:#e65100;text-align:center;font-weight:700;margin-bottom:12px;';
                banner.innerHTML = `<i class="fas fa-exclamation-circle"></i> دفع جزئي<br>
                    <small>تم دفع <strong>${totalPaid.toLocaleString()} ج.م</strong> • المتبقي: <strong style="color:#c62828;">${remaining.toLocaleString()} ج.م</strong></small>`;
            }
            form.style.display = 'block';
            document.getElementById('totalLevelFee').value = storedFee || pricePerLevel || '';
            document.getElementById('amountPaid').value = '';
            document.getElementById('discountAmount').value = '0';
            document.getElementById('notes').value = '';
            document.querySelectorAll('input[name="payMode"]').forEach(r => r.checked = false);
            document.getElementById('paymentDate').valueAsDate = new Date();
            document.getElementById('savePayment').style.display = 'inline-flex';
            document.getElementById('remainingPreview').style.display = 'none';
        }

        // History table
        if (levelPayments.length > 0) {
            history.innerHTML = `
                <div style="font-weight:700;margin-bottom:8px;color:var(--dark-blue);font-size:13px;">
                    <i class="fas fa-history"></i> سجل الدفعات للمستوى ${levelNum}:
                </div>
                <table style="width:100%;border-collapse:collapse;font-size:12px;">
                    <tr style="background:var(--dark-blue);color:white;">
                        <th style="padding:7px;border:1px solid #dee2e6;">#</th>
                        <th style="padding:7px;border:1px solid #dee2e6;">التاريخ</th>
                        <th style="padding:7px;border:1px solid #dee2e6;">المبلغ</th>
                        <th style="padding:7px;border:1px solid #dee2e6;">خصم</th>
                        <th style="padding:7px;border:1px solid #dee2e6;">المتبقي</th>
                    </tr>
                    ${levelPayments.map((p, idx) => `
                        <tr style="background:${idx%2===0?'white':'#f8f9fa'}">
                            <td style="padding:6px;border:1px solid #e9ecef;text-align:center;font-weight:700;">${idx+1}</td>
                            <td style="padding:6px;border:1px solid #e9ecef;">${p.paymentDate || '-'}</td>
                            <td style="padding:6px;border:1px solid #e9ecef;color:var(--success);font-weight:700;">${(parseFloat(p.amountPaid)||0).toLocaleString()} ج.م</td>
                            <td style="padding:6px;border:1px solid #e9ecef;color:var(--danger);">${parseFloat(p.discountAmount)>0 ? '-'+(parseFloat(p.discountAmount)).toLocaleString()+' ج.م' : '-'}</td>
                            <td style="padding:6px;border:1px solid #e9ecef;font-weight:700;color:${parseFloat(p.remainingBalance)>0?'var(--danger)':'var(--success)'};">${(parseFloat(p.remainingBalance)||0).toLocaleString()} ج.م</td>
                        </tr>
                    `).join('')}
                    <tr style="background:#e8f5e9;font-weight:800;">
                        <td colspan="2" style="padding:8px;border:1px solid #dee2e6;">الإجمالي</td>
                        <td style="padding:8px;border:1px solid #dee2e6;color:var(--success);">${totalPaid.toLocaleString()} ج.م</td>
                        <td style="padding:8px;border:1px solid #dee2e6;color:var(--danger);">${totalDiscount>0?'-'+totalDiscount.toLocaleString()+' ج.م':'-'}</td>
                        <td style="padding:8px;border:1px solid #dee2e6;color:${remaining>0?'var(--danger)':'var(--success)'};">${remaining.toLocaleString()} ج.م</td>
                    </tr>
                </table>`;
        } else {
            history.innerHTML = `<div style="padding:10px;text-align:center;color:var(--gray);font-size:13px;">لا توجد دفعات سابقة لهذا المستوى</div>`;
        }
    };

    window.onPayModeChange = function() {
        const mode = document.querySelector('input[name="payMode"]:checked')?.value;
        const totalFeeEl = document.getElementById('totalLevelFee');
        const amountEl = document.getElementById('amountPaid');

        if (!mode) return;

        if (mode === 'full') {
            // Calculate what's remaining and set that as amount
            const storedFee = parseFloat(totalFeeEl.value) || 0;
            const prevPayments = allPayments.filter(p =>
                String(p.studentId) === String(selectedStudentId) &&
                String(p.levelNumber) === String(selectedLevelNumber) &&
                p.paymentType === 'Course Payment'
            );
            const prevPaid = prevPayments.reduce((sum, p) => sum + (parseFloat(p.amountPaid)||0), 0);
            const prevDiscount = prevPayments.reduce((sum, p) => sum + (parseFloat(p.discountAmount)||0), 0);
            const leftover = Math.max(0, storedFee - prevPaid - prevDiscount);
            amountEl.value = leftover;
            amountEl.readOnly = true;
            amountEl.style.background = '#f0f0f0';
        } else {
            amountEl.readOnly = false;
            amountEl.style.background = '';
            amountEl.value = '';
        }
        updateRemainingPreview();
    };

    window.updateRemainingPreview = function() {
        const total = parseFloat(document.getElementById('totalLevelFee').value) || 0;
        const paid  = parseFloat(document.getElementById('amountPaid').value) || 0;
        const disc  = parseFloat(document.getElementById('discountAmount').value) || 0;

        const prevPayments = allPayments.filter(p =>
            String(p.studentId) === String(selectedStudentId) &&
            String(p.levelNumber) === String(selectedLevelNumber) &&
            p.paymentType === 'Course Payment'
        );
        const prevPaid = prevPayments.reduce((sum, p) => sum + (parseFloat(p.amountPaid)||0), 0);
        const prevDisc = prevPayments.reduce((sum, p) => sum + (parseFloat(p.discountAmount)||0), 0);

        const newRemaining = Math.max(0, total - prevPaid - prevDisc - paid - disc);
        const preview = document.getElementById('remainingPreview');

        if (paid > 0 || disc > 0) {
            preview.style.display = 'block';
            if (newRemaining === 0) {
                preview.style.cssText = 'display:block;padding:12px;border-radius:10px;text-align:center;font-weight:700;border:2px solid #4caf50;background:#e8f5e9;color:#2e7d32;margin-bottom:12px;';
                preview.innerHTML = `<i class="fas fa-check-circle"></i> سيتم سداد المبلغ بالكامل ✅`;
            } else {
                preview.style.cssText = 'display:block;padding:12px;border-radius:10px;text-align:center;font-weight:700;border:2px solid #ff9800;background:#fff3e0;color:#e65100;margin-bottom:12px;';
                preview.innerHTML = `<i class="fas fa-info-circle"></i> المتبقي بعد هذه الدفعة: <strong>${newRemaining.toLocaleString('ar-EG')} ج.م</strong>`;
            }
        } else {
            preview.style.display = 'none';
        }
    };

    // =================== ADDON ===================

    function buildAddonList() {
        const student = allStudents.find(s => String(s.id) === String(selectedStudentId));
        let courseId = null;
        if (student?.groupId) {
            const group = allGroups.find(g => String(g.id) === String(student.groupId));
            if (group) courseId = group.courseId;
        }

        const relevantAddons = allAddOns.filter(a => !a.courseId || !courseId || String(a.courseId) === String(courseId));
        const container = document.getElementById('addonList');

        if (!relevantAddons.length) {
            container.innerHTML = `<div style="padding:20px;text-align:center;color:var(--gray);">لا توجد إضافات متاحة</div>`;
            return;
        }

        container.innerHTML = relevantAddons.map(a => {
            const alreadyPaid = allPayments.some(p =>
                String(p.studentId) === String(selectedStudentId) &&
                String(p.levelNumber) === String(a.id) &&
                p.paymentType === 'AddOn Payment'
            );
            return `<div onclick="${alreadyPaid ? '' : `selectAddon(${a.id}, '${(a.name||'').replace(/'/g,"\\'")}', ${a.price||0})`}"
                style="flex:1;min-width:140px;padding:15px;border:2px solid ${alreadyPaid?'#4caf50':'#e9ecef'};border-radius:12px;
                       cursor:${alreadyPaid?'not-allowed':'pointer'};text-align:center;background:${alreadyPaid?'#f5f5f5':'white'};
                       opacity:${alreadyPaid?'0.7':'1'};transition:all 0.2s;"
                ${!alreadyPaid ? 'onmouseover="this.style.borderColor=\'#3c6ec8\';this.style.transform=\'scale(1.03)\'" onmouseout="this.style.borderColor=\'#e9ecef\';this.style.transform=\'scale(1)\'"' : ''}>
                <i class="fas fa-puzzle-piece" style="font-size:22px;color:var(--gold);display:block;margin-bottom:8px;"></i>
                <div style="font-weight:700;font-size:14px;">${a.name}</div>
                <div style="color:var(--primary-blue);font-weight:700;margin-top:4px;">${(a.price||0).toLocaleString()} ج.م</div>
                ${alreadyPaid ? '<div style="color:#2e7d32;font-size:11px;margin-top:5px;"><i class="fas fa-check-circle"></i> مدفوع بالفعل</div>' : ''}
            </div>`;
        }).join('');
    }

    window.selectAddon = function(addonId, addonName, addonPrice) {
        selectedAddonId = addonId;
        document.getElementById('addonPayForm').style.display = 'block';
        document.getElementById('addonSelectedInfo').innerHTML =
            `<i class="fas fa-puzzle-piece" style="color:var(--gold);font-size:16px;"></i>
             الإضافة: <strong>${addonName}</strong>
             <span style="margin-right:10px;color:var(--primary-blue);">السعر: <strong>${addonPrice.toLocaleString()} ج.م</strong></span>`;
        document.getElementById('addonPaymentDate').valueAsDate = new Date();
        document.getElementById('savePayment').style.display = 'inline-flex';
    };

    // =================== SAVE ===================

    async function completePayment() {
        if (!selectedStudentId) { showToast('يرجى اختيار طالب', 'warning'); return; }
        const student = allStudents.find(s => String(s.id) === String(selectedStudentId));
        
        let paymentData = null;

        if (paymentCategory === 'course') {
            if (!selectedLevelNumber) { showToast('يرجى اختيار المستوى', 'warning'); return; }
            const amountPaid = parseFloat(document.getElementById('amountPaid').value) || 0;
            const discountAmount = parseFloat(document.getElementById('discountAmount').value) || 0;
            const totalFee = parseFloat(document.getElementById('totalLevelFee').value) || 0;
            const receiptNum = document.getElementById('receiptNumber').value.trim();
            const payDate = document.getElementById('paymentDate').value;

            if (amountPaid <= 0 && discountAmount <= 0) { showToast('أدخل المبلغ المدفوع أو الخصم', 'warning'); return; }
            if (totalFee <= 0) { showToast('أدخل إجمالي رسوم المستوى', 'warning'); return; }
            if (!payDate) { showToast('أدخل تاريخ الدفع', 'warning'); return; }
            if (!receiptNum) { showToast('أدخل رقم الإيصال', 'warning'); return; }

            paymentData = {
                id: document.getElementById('editPaymentId').value || null,
                studentId: student.id,
                studentName: student.name,
                levelNumber: selectedLevelNumber,
                paymentType: 'Course Payment',
                totalLevelFee: totalFee,
                amountPaid: amountPaid,
                discountAmount: discountAmount,
                remainingBalance: Math.max(0, totalFee - amountPaid - discountAmount),
                notes: document.getElementById('notes').value,
                receiptNumber: receiptNum,
                paymentDate: payDate,
                createdBy: currentUser.id
            };

        } else {
            if (!selectedAddonId) { showToast('يرجى اختيار الإضافة', 'warning'); return; }
            const addon = allAddOns.find(a => String(a.id) === String(selectedAddonId));
            if (!addon) { showToast('الإضافة غير موجودة', 'error'); return; }
            const payDate = document.getElementById('addonPaymentDate').value;
            const receiptNum = document.getElementById('addonReceiptNumber').value.trim();
            
            if (!payDate) { showToast('أدخل تاريخ الدفع', 'warning'); return; }
            if (!receiptNum) { showToast('أدخل رقم الإيصال', 'warning'); return; }

            paymentData = {
                id: document.getElementById('editPaymentId').value || null,
                studentId: student.id,
                studentName: student.name,
                levelNumber: selectedAddonId,
                paymentType: 'AddOn Payment',
                totalLevelFee: addon.price || 0,
                amountPaid: addon.price || 0,
                discountAmount: 0,
                remainingBalance: 0,
                notes: document.getElementById('addonNotes').value,
                receiptNumber: receiptNum,
                paymentDate: payDate,
                createdBy: currentUser.id
            };
        }

        if (paymentData) {
            await doSave(paymentData);
        }
    }

    async function doSave(paymentData) {
        showLoading(true, 'جاري حفظ الدفعة...');
        try {
            const res = await apiCall('savePayment', { paymentData });
            const msg = (typeof res === 'object' && res.message) ? res.message : 'تم تسجيل الدفعة بنجاح';
            showToast(msg + ' ✅', 'success');
            closeModal();
            await loadData();
        } catch(e) {
            console.error('Save error:', e);
            showToast('خطأ في الحفظ: ' + e.message, 'error');
        }
        showLoading(false);
    }

    window.deletePaymentById = async function(id) {
        if (!id) return;
        if (!confirm('هل أنت متأكد من حذف هذه الدفعة؟')) return;
        showLoading(true, 'جاري الحذف...');
        try {
            await apiCall('deletePayment', { paymentId: id });
            showToast('تم الحذف بنجاح', 'success');
            await loadData();
        } catch(e) {
            showToast('خطأ في الحذف: ' + e.message, 'error');
        }
        showLoading(false);
    };

