
    // Ø§Ù„Ø±Ø§Ø¨Ø· Ø§Ù„Ø¬Ø¯ÙŠØ¯ Ù„Ù€ Google Apps Script
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';
    
    let currentUser = null;
    let allStudents = [];
    let allPayments = [];
    let allTrainers = [];
    let allBookings = [];
    let monthlyRevenueChart, paymentDistributionChart;
    
    // Toast Notification
    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    // Centralized API Call
    async function apiCall(action, data = {}) {
        try {
            const response = await fetch(SCRIPT_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                body: JSON.stringify({ action, ...data })
            });
            const result = await response.json();
            if (result.success === false) {
                throw new Error(result.message || 'Ø­Ø¯Ø« Ø®Ø·Ø£ ØºÙŠØ± Ù…Ø¹Ø±ÙˆÙ');
            }
            return result.data !== undefined ? result.data : result;
        } catch (error) {
            if (error.message && !error.message.includes('fetch')) {
                showToast(error.message, 'error');
            } else {
                showToast('Ø­Ø¯Ø« Ø®Ø·Ø£ ÙÙŠ Ø§Ù„Ø§ØªØµØ§Ù„ Ø¨Ø§Ù„Ø®Ø§Ø¯Ù…', 'error');
            }
            throw error;
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        const userStr = sessionStorage.getItem('loggedInUser');
        if (!userStr) { window.location.href = 'index.html'; return; }
        
        try {
            currentUser = JSON.parse(userStr);
        } catch(e) {
            sessionStorage.removeItem('loggedInUser');
            window.location.href = 'index.html';
            return;
        }
        updateUserUI();
        setupEventListeners();
        loadData();
        
        // Set default dates
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        document.getElementById('financialFromDate').valueAsDate = firstDay;
        document.getElementById('financialToDate').valueAsDate = today;
        document.getElementById('paymentsFromDate').valueAsDate = firstDay;
        document.getElementById('paymentsToDate').valueAsDate = today;
        
        // Set default week
        const year = today.getFullYear();
        const week = Math.ceil((((today - new Date(year, 0, 1)) / 86400000) + 1) / 7);
        document.getElementById('attendanceWeek').value = `${year}-W${week.toString().padStart(2, '0')}`;
    });

    function updateUserUI() {
        document.getElementById('userName').textContent = currentUser.fullName || currentUser.username;
        const roleNames = {1: 'Ù…Ø¯ÙŠØ± Ø§Ù„Ù†Ø¸Ø§Ù…', 2: 'Ù…Ø­Ø§Ø³Ø¨', 3: 'Ù…Ø¯ÙŠØ± Ø¯ÙˆØ±', 4: 'Ù…Ø³Ø¤ÙˆÙ„ Ø­Ø¬ÙˆØ²Ø§Øª', 5: 'Ù…Ø´Ø§Ù‡Ø¯'};
        document.getElementById('userRole').textContent = roleNames[currentUser.roleId] || 'Ù…Ø³ØªØ®Ø¯Ù…';
    }

    function setupEventListeners() {
        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.toggle('open'));
        document.getElementById('logoutBtn').addEventListener('click', () => { sessionStorage.removeItem('loggedInUser'); window.location.href = 'index.html'; });
        
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                document.querySelectorAll('.report-section').forEach(section => {
                    section.classList.remove('active');
                });
                document.getElementById(this.dataset.tab + 'Report').classList.add('active');
                
                refreshCurrentReport();
            });
        });
        
        // Filter buttons
        document.getElementById('applyFinancialFilter').addEventListener('click', () => refreshFinancialReport());
        document.getElementById('applyPaymentsFilter').addEventListener('click', () => refreshPaymentsReport());
        document.getElementById('applyAttendanceFilter').addEventListener('click', () => refreshAttendanceReport());
        document.getElementById('studentDeptFilter').addEventListener('change', () => refreshStudentsReport());
        document.getElementById('overdueDeptFilter').addEventListener('change', () => refreshOverdueReport());
        
        // Printing is now handled natively via window.print() on the buttons
    }

    async function loadData() {
        showLoading(true);
        try {
            allStudents = await apiCall('getAllStudents');
            allPayments = await apiCall('getAllPayments');
            allTrainers = await apiCall('getAllTrainers');
            allBookings = await apiCall('getAllBookings');
            allGroups = await apiCall('getAllGroups');
            allCourses = await apiCall('getAllCourses');
            
            populateGlobalFilters();
            
            refreshFinancialReport();
            refreshStudentsReport();
            refreshPaymentsReport();
            refreshAttendanceReport();
            refreshOverdueReport();
            
            // Update trainer filter
            const trainerFilter = document.getElementById('attendanceTrainerFilter');
            trainerFilter.innerHTML = '<option value="all">الكل</option>';
            allTrainers.forEach(t => {
                trainerFilter.innerHTML += `<option value="${t.id}">${t.name}</option>`;
            });
        } catch(e) { 
            console.error(e); 
            // Error handled in apiCall
        }
        showLoading(false);
    }



    function getAggregatedPaymentsData(paymentsList) {
        let grouped = {};
        paymentsList.forEach(p => {
            const key = p.studentId + '__' + p.levelNumber + '__' + p.paymentType;
            if (!grouped[key]) {
                grouped[key] = { ...p, amountPaid: parseFloat(p.amountPaid)||0, discountAmount: parseFloat(p.discountAmount)||0 };
            } else {
                grouped[key].amountPaid += parseFloat(p.amountPaid)||0;
                grouped[key].discountAmount += parseFloat(p.discountAmount)||0;
                if (p.id > grouped[key].id) {
                    grouped[key].remainingBalance = p.remainingBalance;
                    grouped[key].id = p.id;
                }
            }
        });

        if (typeof allStudents !== 'undefined') {
            allStudents.forEach(s => {
                if (s.groupId) {
                    const group = allGroups.find(g => String(g.id) === String(s.groupId));
                    if (group) {
                        const course = allCourses.find(c => String(c.id) === String(group.courseId));
                        if (course) {
                            const targetLevel = '1';
                            const hasPayment = Object.values(grouped).some(p => String(p.studentId) === String(s.id) && String(p.levelNumber) === String(targetLevel));
                            if (!hasPayment) {
                                const coursePrice = parseFloat(course.pricePerLevel) || 0;
                                const key = s.id + '__' + targetLevel + '__Unpaid';
                                grouped[key] = {
                                    studentId: s.id,
                                    studentName: s.name,
                                    levelNumber: targetLevel,
                                    paymentType: '-',
                                    paymentDate: s.createdAt,
                                    amountPaid: 0,
                                    remainingBalance: coursePrice,
                                    totalFee: coursePrice
                                };
                            }
                        }
                    }
                }
            });
        }
        return Object.values(grouped);
    }

    function populateGlobalFilters() {
        const deptFilter = document.getElementById('globalDeptFilter');
        const courseFilter = document.getElementById('globalCourseFilter');
        const groupFilter = document.getElementById('globalGroupFilter');
        
        deptFilter.innerHTML = '<option value="all">الكل</option>' + 
            '<option value="1">تقنية المعلومات</option>' +
            '<option value="2">اللغات</option>' +
            '<option value="3">إدارة الأعمال</option>' +
            '<option value="4">التصميم</option>';

        deptFilter.addEventListener('change', () => {
            const dId = deptFilter.value;
            courseFilter.innerHTML = '<option value="all">الكل</option>';
            groupFilter.innerHTML = '<option value="all">الكل</option>';
            if(dId !== 'all') {
                const courses = allCourses.filter(c => String(c.deptId) === String(dId));
                courses.forEach(c => courseFilter.innerHTML += `<option value="${c.id}">${c.name}</option>`);
            }
            refreshCurrentReport();
        });

        courseFilter.addEventListener('change', () => {
            const cId = courseFilter.value;
            groupFilter.innerHTML = '<option value="all">الكل</option>';
            if(cId !== 'all') {
                const groups = allGroups.filter(g => String(g.courseId) === String(cId));
                groups.forEach(g => groupFilter.innerHTML += `<option value="${g.id}">${g.name}</option>`);
            }
            refreshCurrentReport();
        });

        groupFilter.addEventListener('change', refreshCurrentReport);
        document.getElementById('globalStatusFilter').addEventListener('change', refreshCurrentReport);
        document.getElementById('applyGlobalFilter').addEventListener('click', refreshCurrentReport);
    }

    function refreshCurrentReport() {
        const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
        if(activeTab === 'financial') refreshFinancialReport();
        else if(activeTab === 'students') refreshStudentsReport();
        else if(activeTab === 'payments') refreshPaymentsReport();
        else if(activeTab === 'attendance') refreshAttendanceReport();
        else if(activeTab === 'overdue') refreshOverdueReport();
    }

        function applyGlobalFiltersToStudents(students) {
        const deptFilter = document.getElementById('globalDeptFilter').value;
        const courseFilter = document.getElementById('globalCourseFilter').value;
        const groupFilter = document.getElementById('globalGroupFilter');

        let filtered = [...students];
        if (deptFilter !== 'all') filtered = filtered.filter(s => String(s.deptId) === String(deptFilter));
        if (groupFilter !== 'all') filtered = filtered.filter(s => String(s.groupId) === String(groupFilter));
        else if (courseFilter !== 'all') {
            const courseGroups = allGroups.filter(g => String(g.courseId) === String(courseFilter)).map(g => String(g.id));
            filtered = filtered.filter(s => courseGroups.includes(String(s.groupId)));
        }
        return filtered;
    }

    function applyGlobalFiltersToPayments(payments, isAggregated = false) {
        const deptFilter = document.getElementById('globalDeptFilter').value;
        const courseFilter = document.getElementById('globalCourseFilter').value;
        const groupFilter = document.getElementById('globalGroupFilter');
        const statusFilter = document.getElementById('globalStatusFilter').value;

        return payments.filter(p => {
            const s = allStudents.find(st => String(st.id) === String(p.studentId));
            if (!s) return false;
            
            if (deptFilter !== 'all' && String(s.deptId) !== String(deptFilter)) return false;
            if (groupFilter !== 'all' && String(s.groupId) !== String(groupFilter)) return false;
            if (courseFilter !== 'all') {
                const g = allGroups.find(gr => String(gr.id) === String(s.groupId));
                if (!g || String(g.courseId) !== String(courseFilter)) return false;
            }
            
            if (isAggregated && statusFilter !== 'all') {
                const isPaid = parseFloat(p.remainingBalance) === 0;
                const isPartial = parseFloat(p.remainingBalance) > 0 && parseFloat(p.amountPaid) > 0;
                const isUnpaid = parseFloat(p.amountPaid) <= 0;
                
                if (statusFilter === 'paid' && !isPaid) return false;
                if (statusFilter === 'partial' && !isPartial) return false;
                if (statusFilter === 'unpaid' && !isUnpaid) return false;
            }
            return true;
        });
    }

    function refreshFinancialReport() {
        const fromDate = document.getElementById('financialFromDate').value;
        const toDate = document.getElementById('financialToDate').value;
        
        let filteredPayments = [...allPayments];
        if (fromDate) filteredPayments = filteredPayments.filter(p => p.paymentDate >= fromDate);
        if (toDate) filteredPayments = filteredPayments.filter(p => p.paymentDate <= toDate);
        
        filteredPayments = applyGlobalFiltersToPayments(filteredPayments, false);
        let aggregated = getAggregatedPaymentsData(filteredPayments);
        aggregated = applyGlobalFiltersToPayments(aggregated, true);
        
        const totalRevenue = filteredPayments.reduce((sum, p) => sum + (parseFloat(p.amountPaid) || 0), 0);
        const totalRemaining = aggregated.reduce((sum, p) => sum + (parseFloat(p.remainingBalance) || 0), 0);
        const totalTransactions = filteredPayments.length;
        
        document.getElementById('financialStats').innerHTML = \
            <div class="stat-card"><div class="stat-info"><div class="stat-value">\ ج.م</div><div class="stat-label">إجمالي الإيرادات</div></div><div class="stat-icon"><i class="fas fa-dollar-sign"></i></div></div>
            <div class="stat-card"><div class="stat-info"><div class="stat-value">\ ج.م</div><div class="stat-label">المتبقي</div></div><div class="stat-icon"><i class="fas fa-clock"></i></div></div>
            <div class="stat-card"><div class="stat-info"><div class="stat-value">\</div><div class="stat-label">عدد المعاملات</div></div><div class="stat-icon"><i class="fas fa-receipt"></i></div></div>
        \;
        
        updateMonthlyRevenueChart(filteredPayments);
        updatePaymentDistributionChart(aggregated);
    }

    function updateMonthlyRevenueChart(payments) {
        const months = ['يناير', 'ÙØ¨Ø±Ø§ÙŠØ±', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'Ù†ÙˆÙÙ…Ø¨Ø±', 'ديسمبر'];
        const monthlyData = new Array(12).fill(0);
        
        payments.forEach(p => {
            if (p.paymentDate) {
                const month = new Date(p.paymentDate).getMonth();
                monthlyData[month] += parseFloat(p.amountPaid) || 0;
            }
        });
        
        const ctx = document.getElementById('monthlyRevenueChart').getContext('2d');
        if (monthlyRevenueChart) monthlyRevenueChart.destroy();
        monthlyRevenueChart = new Chart(ctx, {
            type: 'line',
            data: { labels: months, datasets: [{ label: 'Ø§Ù„Ø¥ÙŠØ±Ø§Ø¯Ø§Øª (ج.م)', data: monthlyData, borderColor: '#3c6ec8', backgroundColor: 'rgba(60,110,200,0.05)', tension: 0.3, fill: true }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'top' } } }
        });
    }

    function updatePaymentDistributionChart(payments) {
        let paid = 0, partial = 0;
        const studentPayments = {};
        payments.forEach(p => {
            if (!studentPayments[p.studentId]) studentPayments[p.studentId] = { totalPaid: 0, totalFee: 0, remainingBalance: 0 };
            studentPayments[p.studentId].totalPaid += parseFloat(p.amountPaid) || 0;
            studentPayments[p.studentId].totalFee += parseFloat(p.totalFee) || parseFloat(p.totalLevelFee) || 0;
            studentPayments[p.studentId].remainingBalance += parseFloat(p.remainingBalance) || 0;
        });
        
        Object.values(studentPayments).forEach(s => {
            if (s.totalPaid > 0 && s.remainingBalance <= 0) paid++;
            else if (s.totalPaid > 0 && s.remainingBalance > 0) partial++;
        });
        
        const filteredStudents = applyGlobalFiltersToStudents(allStudents);
        const unpaid = Math.max(0, filteredStudents.length - paid - partial);
        
        const ctx = document.getElementById('paymentDistributionChart').getContext('2d');
        if (paymentDistributionChart) paymentDistributionChart.destroy();
        paymentDistributionChart = new Chart(ctx, {
            type: 'doughnut',
            data: { labels: ['Ù…Ø¯ÙÙˆØ¹ Ø¨Ø§Ù„ÙƒØ§Ù…Ù„', 'Ù…Ø¯ÙÙˆØ¹ Ø¬Ø²Ø¦ÙŠØ§Ù‹', 'ØºÙŠØ± Ù…Ø¯ÙÙˆØ¹'], datasets: [{ data: [paid, partial, unpaid], backgroundColor: ['#2ecc71', '#f39c12', '#e74c3c'], borderWidth: 0 }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom' } } }
        });
    }

    function refreshStudentsReport() {
        let filtered = applyGlobalFiltersToStudents(allStudents);
        
        const deptNames = {1: 'IT', 2: 'LANG', 3: 'BUS', 4: 'GD'};
        document.getElementById('studentsReportBody').innerHTML = filtered.map(s => \
            <tr>
                <td>\</td>
                <td>\</td>
                <td>\</td>
                <td>\</td>
                <td>\</td>
                <td>\</td>
            </tr>
        \).join('');
    }

    function refreshPaymentsReport() {
        const fromDate = document.getElementById('paymentsFromDate').value;
        const toDate = document.getElementById('paymentsToDate').value;
        
        let filtered = getAggregatedPaymentsData(allPayments);
        if (fromDate) filtered = filtered.filter(p => p.paymentDate >= fromDate);
        if (toDate) filtered = filtered.filter(p => p.paymentDate <= toDate);
        
        filtered = applyGlobalFiltersToPayments(filtered, true);
        
        document.getElementById('paymentsReportBody').innerHTML = filtered.map(p => {
            const status = parseFloat(p.remainingBalance) === 0 ? 'Ù…Ø¯ÙÙˆØ¹' : (parseFloat(p.amountPaid) > 0 ? 'Ù…Ø¯ÙÙˆØ¹ Ø¬Ø²Ø¦ÙŠØ§Ù‹' : 'ØºÙŠØ± Ù…Ø¯ÙÙˆØ¹');
            const statusClass = parseFloat(p.remainingBalance) === 0 ? 'status-paid' : (parseFloat(p.amountPaid) > 0 ? 'status-partial' : 'status-unpaid');
            return \
                <tr>
                    <td>\</td>
                    <td>\</td>
                    <td>المستوى \</td>
                    <td>\ ج.م</td>
                    <td>\</td>
                    <td><span class="status-badge \">\</span></td>
                </tr>
            \;
        }).join('');
    }

    function refreshAttendanceReport() {
        const trainerFilter = document.getElementById('attendanceTrainerFilter').value;
        let filtered = [...allBookings];
        if (trainerFilter !== 'all') filtered = filtered.filter(b => String(b.trainerId) === String(trainerFilter));
        
        const groupFilter = document.getElementById('globalGroupFilter').value;
        if (groupFilter !== 'all') {
            filtered = filtered.filter(b => String(b.groupId) === String(groupFilter));
        } else {
            const courseFilter = document.getElementById('globalCourseFilter').value;
            if (courseFilter !== 'all') {
                const courseGroups = allGroups.filter(g => String(g.courseId) === String(courseFilter)).map(g => String(g.id));
                filtered = filtered.filter(b => courseGroups.includes(String(b.groupId)));
            }
        }
        
        const trainerNames = {};
        allTrainers.forEach(t => { trainerNames[t.id] = t.name; });
        
        document.getElementById('attendanceBody').innerHTML = filtered.map(b => \
            <tr>
                <td>\</td>
                <td>\ - \</td>
                <td>\</td>
                <td>Ù‚Ø§Ø¹Ø© \</td>
                <td>Ø¬Ø±ÙˆØ¨ \</td>
            </tr>
        \).join('');
        
        document.getElementById('attendanceHeader').innerHTML = '<th>اليوم</th><th>الوقت</th><th>المدرب</th><th>القاعة</th><th>الجروب</th>';
    }

    function refreshOverdueReport() {
        let aggregated = getAggregatedPaymentsData(allPayments);
        aggregated = applyGlobalFiltersToPayments(aggregated, true);
        
        const studentBalance = {};
        aggregated.forEach(p => {
            if (!studentBalance[p.studentId]) studentBalance[p.studentId] = { balance: 0, lastPayment: p.paymentDate };
            studentBalance[p.studentId].balance += parseFloat(p.remainingBalance) || 0;
            if (p.paymentDate > studentBalance[p.studentId].lastPayment) {
                studentBalance[p.studentId].lastPayment = p.paymentDate;
            }
        });
        
        let overdueStudents = allStudents.filter(s => (studentBalance[s.id]?.balance || 0) > 0);
        overdueStudents = applyGlobalFiltersToStudents(overdueStudents);
        
        const totalOverdue = overdueStudents.reduce((sum, s) => sum + (studentBalance[s.id].balance || 0), 0);
        
        document.getElementById('overdueStats').innerHTML = \
            <div class="stat-card"><div class="stat-info"><div class="stat-value">\</div><div class="stat-label">عدد الطلاب المتأخرين</div></div><div class="stat-icon"><i class="fas fa-users"></i></div></div>
            <div class="stat-card"><div class="stat-info"><div class="stat-value">\ ج.م</div><div class="stat-label">Ø¥Ø¬Ù…Ø§Ù„ÙŠ المتأخرات</div></div><div class="stat-icon"><i class="fas fa-dollar-sign"></i></div></div>
        \;
        
        const deptNames = {1: 'IT', 2: 'LANG', 3: 'BUS', 4: 'GD'};
        document.getElementById('overdueBody').innerHTML = overdueStudents.map(s => {
            const sBal = studentBalance[s.id];
            return \
                <tr>
                    <td>\</td>
                    <td>\</td>
                    <td>\</td>
                    <td>\</td>
                    <td style="color: #e74c3c; font-weight: 600;">\ ج.م</td>
                    <td>\</td>
                </tr>
            \;
        }).join('');
    }


    function showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) overlay.classList.add('show');
        else overlay.classList.remove('show');
    }

    function exportToExcel(btnElement) {
        // Find the closest report container and then the table
        const container = btnElement.closest('.report-container');
        const table = container.querySelector('table');
        if (!table) return;

        let csv = '\uFEFF'; // Add BOM for Excel Arabic support
        const rows = table.querySelectorAll('tr');
        
        for (let i = 0; i < rows.length; i++) {
            const row = [], cols = rows[i].querySelectorAll('td, th');
            for (let j = 0; j < cols.length; j++) {
                // Get text and escape quotes
                let data = cols[j].innerText.replace(/"/g, '""');
                row.push('"' + data + '"');
            }
            csv += row.join(',') + '\n';
        }
        
        // Download
        const tabName = document.querySelector('.tab-btn.active').innerText.trim() || 'ØªÙ‚Ø±ÙŠØ±';
        const filename = tabName + '_' + new Date().toLocaleDateString('ar-EG') + '.csv';
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

