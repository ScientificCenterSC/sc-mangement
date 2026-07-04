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
        const months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'];
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
            data: { labels: months, datasets: [{ label: 'الإيرادات (ج.م)', data: monthlyData, borderColor: '#3c6ec8', backgroundColor: 'rgba(60,110,200,0.05)', tension: 0.3, fill: true }] },
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
            data: { labels: ['مدفوع بالكامل', 'مدفوع جزئياً', 'غير مدفوع'], datasets: [{ data: [paid, partial, unpaid], backgroundColor: ['#2ecc71', '#f39c12', '#e74c3c'], borderWidth: 0 }] },
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
            const status = parseFloat(p.remainingBalance) === 0 ? 'مدفوع' : (parseFloat(p.amountPaid) > 0 ? 'مدفوع جزئياً' : 'غير مدفوع');
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
                <td>قاعة \</td>
                <td>جروب \</td>
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
            <div class="stat-card"><div class="stat-info"><div class="stat-value">\ ج.م</div><div class="stat-label">إجمالي المتأخرات</div></div><div class="stat-icon"><i class="fas fa-dollar-sign"></i></div></div>
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
