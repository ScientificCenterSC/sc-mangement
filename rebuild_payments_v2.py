with open('payments.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.index('<script>')
html_part = content[:idx]

# Fix the modal HTML - remove old modal, insert new one before script
# Find end of old modal
old_modal_start = '<!-- Add Payment Modal -->'
modal_end_marker = '</div>\n\n<script>'
modal_end_idx = html_part.rfind('</div>')
# Just rebuild from the modal section onwards

# Keep HTML until the paymentModal
modal_idx = html_part.find('<!-- Add Payment Modal -->')
if modal_idx == -1:
    modal_idx = html_part.find('<div class="modal" id="paymentModal">')

if modal_idx != -1:
    html_base = html_part[:modal_idx]
else:
    html_base = html_part

new_modal = """<!-- Add Payment Modal -->
<div class="modal" id="paymentModal">
    <div class="modal-content" style="max-width:700px;">
        <div class="modal-header">
            <h3 id="modalTitle">تسجيل دفعة جديدة</h3>
            <button class="close-modal" id="closeModal">&times;</button>
        </div>
        <div class="modal-body">
            <!-- Step 1: Search Student -->
            <div id="step1">
                <div class="form-group">
                    <label><i class="fas fa-search"></i> البحث عن طالب</label>
                    <input type="text" id="studentSearchInput" placeholder="ابحث باسم الطالب أو كوده..." style="width:100%;padding:12px;border:2px solid #e9ecef;border-radius:10px;">
                </div>
                <div id="studentResults" style="max-height:300px;overflow-y:auto;margin-top:10px;"></div>
            </div>

            <!-- Step 2: Choose what to pay -->
            <div id="step2" style="display:none;">
                <div id="studentInfoBar" style="background:linear-gradient(135deg,#1a2a6c,#2a4a9c);color:white;padding:15px;border-radius:12px;margin-bottom:20px;">
                    <div style="font-size:16px;font-weight:700;" id="selectedStudentDisplay"></div>
                    <div style="font-size:13px;opacity:0.8;margin-top:4px;" id="selectedStudentCourse"></div>
                </div>

                <div style="display:flex;gap:10px;margin-bottom:20px;">
                    <button onclick="choosePaymentCategory('level')" id="btnPayLevel" style="flex:1;padding:20px;border:2px solid #e9ecef;border-radius:12px;cursor:pointer;background:white;transition:all 0.2s;" onmouseover="this.style.borderColor='#3c6ec8'" onmouseout="if(this.id!='btnPayLevel' || !this.classList.contains('selected')) this.style.borderColor='#e9ecef'">
                        <i class="fas fa-graduation-cap" style="font-size:24px;color:#3c6ec8;display:block;margin-bottom:8px;"></i>
                        <div style="font-weight:700;">دفع كورس / مستوى</div>
                        <div style="font-size:12px;color:#666;margin-top:4px;">دفع قسط مستوى من الكورس</div>
                    </button>
                    <button onclick="choosePaymentCategory('addon')" id="btnPayAddon" style="flex:1;padding:20px;border:2px solid #e9ecef;border-radius:12px;cursor:pointer;background:white;transition:all 0.2s;" onmouseover="this.style.borderColor='#f4a261'" onmouseout="if(this.id!='btnPayAddon' || !this.classList.contains('selected')) this.style.borderColor='#e9ecef'">
                        <i class="fas fa-plus-circle" style="font-size:24px;color:#f4a261;display:block;margin-bottom:8px;"></i>
                        <div style="font-weight:700;">دفع إضافة (AddOn)</div>
                        <div style="font-size:12px;color:#666;margin-top:4px;">دفع مقابل خدمة إضافية</div>
                    </button>
                </div>
            </div>

            <!-- Step 3A: Level Payment -->
            <div id="step3Level" style="display:none;">
                <div style="margin-bottom:15px;">
                    <label style="font-weight:700;display:block;margin-bottom:8px;">اختر المستوى</label>
                    <div id="levelButtons" style="display:flex;flex-wrap:wrap;gap:10px;"></div>
                </div>
                <div id="levelPaymentDetails" style="display:none;background:#f8f9fa;padding:15px;border-radius:12px;margin-bottom:15px;">
                    <div id="levelStatusBanner" style="padding:10px;border-radius:8px;margin-bottom:12px;text-align:center;font-weight:700;"></div>
                    <div id="levelPayHistory"></div>
                </div>
                <div id="levelPayForm" style="display:none;">
                    <div class="form-group" style="margin-bottom:12px;">
                        <label>إجمالي رسوم المستوى (ج.م)</label>
                        <input type="number" id="totalLevelFee" placeholder="مثلاً: 1500" style="width:100%;padding:10px;border:2px solid #e9ecef;border-radius:8px;">
                    </div>
                    <div style="margin-bottom:12px;">
                        <label style="font-weight:700;display:block;margin-bottom:8px;">طريقة الدفع</label>
                        <div style="display:flex;gap:10px;">
                            <label style="flex:1;padding:12px;border:2px solid #e9ecef;border-radius:10px;cursor:pointer;display:flex;align-items:center;gap:8px;">
                                <input type="radio" name="payMode" value="full" onchange="onPayModeChange()"> دفع كامل
                            </label>
                            <label style="flex:1;padding:12px;border:2px solid #e9ecef;border-radius:10px;cursor:pointer;display:flex;align-items:center;gap:8px;">
                                <input type="radio" name="payMode" value="partial" onchange="onPayModeChange()"> دفع جزئي
                            </label>
                        </div>
                    </div>
                    <div class="form-group" style="margin-bottom:12px;">
                        <label>المبلغ المدفوع (ج.م)</label>
                        <input type="number" id="amountPaid" placeholder="المبلغ المدفوع" style="width:100%;padding:10px;border:2px solid #e9ecef;border-radius:8px;" oninput="updateRemainingPreview()">
                    </div>
                    <div class="form-group" style="margin-bottom:12px;">
                        <label>خصم (ج.م) - اختياري</label>
                        <input type="number" id="discountAmount" placeholder="0" value="0" style="width:100%;padding:10px;border:2px solid #e9ecef;border-radius:8px;" oninput="updateRemainingPreview()">
                    </div>
                    <div id="remainingPreview" style="background:#e8f5e9;border:1px solid #4caf50;border-radius:8px;padding:10px;margin-bottom:12px;text-align:center;font-weight:700;display:none;"></div>
                    <div class="form-group" style="margin-bottom:12px;">
                        <label>ملاحظات</label>
                        <input type="text" id="notes" placeholder="ملاحظات إضافية" style="width:100%;padding:10px;border:2px solid #e9ecef;border-radius:8px;">
                    </div>
                    <div class="form-group">
                        <label>تاريخ الدفع</label>
                        <input type="date" id="paymentDate" style="width:100%;padding:10px;border:2px solid #e9ecef;border-radius:8px;">
                    </div>
                </div>
            </div>

            <!-- Step 3B: AddOn Payment -->
            <div id="step3Addon" style="display:none;">
                <div id="addonList" style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:15px;"></div>
                <div id="addonPayForm" style="display:none;">
                    <div id="addonSelectedInfo" style="background:#fff3e0;padding:12px;border-radius:8px;margin-bottom:12px;font-weight:700;"></div>
                    <div class="form-group" style="margin-bottom:12px;">
                        <label>تاريخ الدفع</label>
                        <input type="date" id="addonPaymentDate" style="width:100%;padding:10px;border:2px solid #e9ecef;border-radius:8px;">
                    </div>
                    <div class="form-group">
                        <label>ملاحظات</label>
                        <input type="text" id="addonNotes" placeholder="ملاحظات" style="width:100%;padding:10px;border:2px solid #e9ecef;border-radius:8px;">
                    </div>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn-cancel" id="cancelModal">إلغاء</button>
            <button class="btn-cancel" id="backBtn" style="display:none;" onclick="goBack()"><i class="fas fa-arrow-right"></i> رجوع</button>
            <button class="btn-save" id="savePayment" style="display:none;" onclick="completePayment()">
                <i class="fas fa-save"></i> تسجيل الدفعة
            </button>
        </div>
    </div>
</div>

"""

new_script = """<script>
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwIqJ0hC7xzs4I6--ocDyCHkwxwmVUk-Y0eOwYsTUCiP39MH2oetro_9ssGTniJOztRjw/exec';
    
    let currentUser = null;
    let allPayments = [];
    let allStudents = [];
    let allCourses = [];
    let allGroups = [];
    let allAddOns = [];
    let paymentChart, revenueChart;

    // Modal state
    let selectedStudentId = null;
    let selectedLevelNumber = null;
    let selectedAddonId = null;
    let paymentCategory = null; // 'level' or 'addon'

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
        const seen = new Set();
        allPayments.forEach(p => {
            totalPaid += parseFloat(p.amountPaid) || 0;
            // For remaining, count per student-level combo (last remaining)
            const key = `${p.studentId}-${p.levelNumber}`;
            seen.add(key);
        });
        // Calculate total remaining per student-level
        const latestRemaining = {};
        allPayments.forEach(p => {
            const key = `${p.studentId}-${p.levelNumber}`;
            if (!latestRemaining[key] || p.id > latestRemaining[key].id) {
                latestRemaining[key] = p;
            }
        });
        Object.values(latestRemaining).forEach(p => {
            const r = parseFloat(p.remainingBalance) || 0;
            totalRemaining += r;
            if (r > 0) overdueCount++;
        });

        document.getElementById('totalPaid').textContent = totalPaid.toLocaleString() + ' ج.م';
        document.getElementById('totalRemaining').textContent = totalRemaining.toLocaleString() + ' ج.م';
        document.getElementById('totalStudents').textContent = allStudents.length;
        document.getElementById('overdueCount').textContent = overdueCount;
    }

    function updateCharts() {
        let paid = 0, remaining = 0;
        allPayments.forEach(p => { paid += parseFloat(p.amountPaid)||0; remaining += parseFloat(p.remainingBalance)||0; });
        
        const ctx1 = document.getElementById('paymentChart');
        if (!ctx1) return;
        if (paymentChart) paymentChart.destroy();
        paymentChart = new Chart(ctx1.getContext('2d'), {
            type: 'doughnut',
            data: { labels: ['مدفوع', 'متبقي'], datasets: [{ data: [paid, remaining], backgroundColor: ['#2ecc71', '#e74c3c'], borderWidth: 0 }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', rtl: true } } }
        });

        const ctx2 = document.getElementById('revenueChart');
        if (!ctx2) return;
        if (revenueChart) revenueChart.destroy();
        revenueChart = new Chart(ctx2.getContext('2d'), {
            type: 'line',
            data: { labels: ['يناير','فبراير','مارس','أبريل','مايو','يونيو'], datasets: [{ label: 'الإيرادات', data: [8500,9200,7800,10500,12400,14500], borderColor: '#3c6ec8', tension: 0.3, fill: true, backgroundColor:'rgba(60,110,200,0.08)' }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } } }
        });
    }

    function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;
        
        // Group payments by student+level to show summary rows
        const grouped = {};
        allPayments.forEach(p => {
            const key = `${p.studentId}_${p.levelNumber}_${p.paymentType}`;
            if (!grouped[key]) grouped[key] = { ...p, allAmounts: [] };
            grouped[key].allAmounts.push({ amount: parseFloat(p.amountPaid)||0, date: p.paymentDate, id: p.id });
            grouped[key].remainingBalance = parseFloat(p.remainingBalance) || 0;
            grouped[key].totalPaid = (grouped[key].totalPaid || 0) + (parseFloat(p.amountPaid) || 0);
        });
        
        let rows = Object.values(grouped);
        
        if (searchTerm) {
            rows = rows.filter(p => {
                const s = allStudents.find(st => st.id == p.studentId);
                return (p.studentName||'').toLowerCase().includes(searchTerm) || (s?.code||'').toLowerCase().includes(searchTerm);
            });
        }
        if (statusFilter === 'paid') rows = rows.filter(p => p.remainingBalance === 0);
        else if (statusFilter === 'partial') rows = rows.filter(p => p.remainingBalance > 0 && p.totalPaid > 0);
        else if (statusFilter === 'unpaid') rows = rows.filter(p => !p.totalPaid);
        
        renderTable(rows);
    }

    function renderTable(rows) {
        const tbody = document.getElementById('paymentsTableBody');
        if (!rows || rows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="11" style="text-align:center;padding:30px;color:var(--gray)">لا توجد مدفوعات</td></tr>';
            return;
        }
        
        tbody.innerHTML = rows.map(p => {
            const student = allStudents.find(s => s.id == p.studentId);
            const remaining = parseFloat(p.remainingBalance) || 0;
            const paid = p.totalPaid || 0;
            const status = remaining === 0 ? 'مدفوع' : (paid > 0 ? 'جزئي' : 'غير مدفوع');
            const statusClass = remaining === 0 ? 'status-paid' : (paid > 0 ? 'status-partial' : 'status-unpaid');
            const latestDate = p.allAmounts.length > 0 ? p.allAmounts[p.allAmounts.length-1].date : p.paymentDate;
            const dateStr = latestDate ? new Date(latestDate).toLocaleDateString('ar-EG') : '-';
            const payType = p.paymentType === 'Course Payment' ? 'كورس' : p.paymentType === 'AddOn Payment' ? 'إضافة' : p.paymentType || '-';
            
            // Show payment breakdown if multiple
            let paidDisplay = paid.toLocaleString() + ' ج.م';
            if (p.allAmounts && p.allAmounts.length > 1) {
                paidDisplay = `<span title="${p.allAmounts.map(a=>a.amount.toLocaleString()+' ج.م').join(' + ')}">${paid.toLocaleString()} ج.م <small style="color:#3c6ec8">(${p.allAmounts.length} دفعات)</small></span>`;
            }
            
            return `
                <tr>
                    <td><strong>${p.studentName || '-'}</strong></td>
                    <td>${student?.code || '-'}</td>
                    <td>المستوى ${p.levelNumber || 1}</td>
                    <td>${payType}</td>
                    <td style="color:var(--success);font-weight:600">${paidDisplay}</td>
                    <td>${(parseFloat(p.discountAmount)||0).toLocaleString()} ج.م</td>
                    <td>${(parseFloat(p.totalFee)||0).toLocaleString()} ج.م</td>
                    <td style="color:${remaining>0?'var(--danger)':'var(--success)'};font-weight:700">${remaining.toLocaleString()} ج.م</td>
                    <td>${p.notes || '-'}</td>
                    <td>${dateStr}</td>
                    <td class="action-buttons">
                        <button class="btn-icon btn-delete" onclick="deletePaymentById(${p.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    // =================== MODAL FLOW ===================

    function openAddPaymentModal() {
        resetModal();
        document.getElementById('paymentModal').classList.add('show');
    }

    function resetModal() {
        selectedStudentId = null;
        selectedLevelNumber = null;
        selectedAddonId = null;
        paymentCategory = null;
        
        document.getElementById('step1').style.display = 'block';
        document.getElementById('step2').style.display = 'none';
        document.getElementById('step3Level').style.display = 'none';
        document.getElementById('step3Addon').style.display = 'none';
        document.getElementById('backBtn').style.display = 'none';
        document.getElementById('savePayment').style.display = 'none';
        document.getElementById('studentSearchInput').value = '';
        document.getElementById('studentResults').innerHTML = '<div style="padding:15px;text-align:center;color:gray">ابحث باسم الطالب أو الكود...</div>';
    }

    function closeModal() {
        document.getElementById('paymentModal').classList.remove('show');
    }

    window.goBack = function() {
        if (paymentCategory !== null) {
            // Go back to category selection
            paymentCategory = null;
            document.getElementById('step3Level').style.display = 'none';
            document.getElementById('step3Addon').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
            document.getElementById('savePayment').style.display = 'none';
        } else {
            // Go back to student search
            document.getElementById('step2').style.display = 'none';
            document.getElementById('step1').style.display = 'block';
            document.getElementById('backBtn').style.display = 'none';
            selectedStudentId = null;
        }
    };

    function searchStudents(query) {
        const results = document.getElementById('studentResults');
        if (!query.trim()) {
            results.innerHTML = '<div style="padding:15px;text-align:center;color:gray">ابحث باسم الطالب أو الكود...</div>';
            return;
        }
        const filtered = allStudents.filter(s => 
            (s.name||'').toLowerCase().includes(query.toLowerCase()) || 
            (s.code||'').toLowerCase().includes(query.toLowerCase())
        );
        if (!filtered.length) { results.innerHTML = '<div style="padding:15px;text-align:center;color:gray">لا توجد نتائج</div>'; return; }
        results.innerHTML = filtered.map(s => `
            <div onclick="selectStudent(${s.id})" style="padding:12px 15px;cursor:pointer;border:1px solid #e9ecef;border-radius:10px;margin-bottom:8px;transition:all 0.15s;background:white;" onmouseover="this.style.background='#f0f4ff';this.style.borderColor='#3c6ec8'" onmouseout="this.style.background='white';this.style.borderColor='#e9ecef'">
                <div style="font-weight:700;color:#1a2a6c;">${s.name}</div>
                <div style="font-size:12px;color:#666;">${s.code || ''}</div>
            </div>
        `).join('');
    }

    window.selectStudent = function(id) {
        const student = allStudents.find(s => s.id == id);
        if (!student) return;
        selectedStudentId = id;

        // Show step 2
        document.getElementById('step1').style.display = 'none';
        document.getElementById('step2').style.display = 'block';
        document.getElementById('backBtn').style.display = 'inline-block';
        
        // Find course info
        let courseName = '-';
        if (student.groupId) {
            const group = allGroups.find(g => g.id == student.groupId);
            if (group) courseName = group.courseName || group.name;
        }
        document.getElementById('selectedStudentDisplay').textContent = `${student.name} (${student.code || ''})`;
        document.getElementById('selectedStudentCourse').textContent = `الكورس: ${courseName}`;
    };

    window.choosePaymentCategory = function(cat) {
        paymentCategory = cat;
        document.getElementById('step2').style.display = 'none';
        document.getElementById('btnPayLevel').classList.remove('selected');
        document.getElementById('btnPayAddon').classList.remove('selected');

        if (cat === 'level') {
            document.getElementById('step3Level').style.display = 'block';
            buildLevelButtons();
        } else {
            document.getElementById('step3Addon').style.display = 'block';
            buildAddonList();
        }
    };

    function buildLevelButtons() {
        const student = allStudents.find(s => s.id == selectedStudentId);
        if (!student) return;
        
        let totalLevels = 1;
        let pricePerLevel = 0;
        if (student.groupId) {
            const group = allGroups.find(g => g.id == student.groupId);
            if (group) {
                const course = allCourses.find(c => c.id == group.courseId);
                if (course) {
                    totalLevels = course.durationLevels || group.levelCount || 1;
                    pricePerLevel = course.pricePerLevel || 0;
                }
            }
        }

        const container = document.getElementById('levelButtons');
        container.innerHTML = '';
        for (let i = 1; i <= totalLevels; i++) {
            const levelPayments = allPayments.filter(p => p.studentId == selectedStudentId && p.levelNumber == i && p.paymentType === 'Course Payment');
            const totalPaid = levelPayments.reduce((sum, p) => sum + (parseFloat(p.amountPaid)||0), 0);
            const totalDiscount = levelPayments.reduce((sum, p) => sum + (parseFloat(p.discountAmount)||0), 0);
            const remaining = Math.max(0, pricePerLevel - totalPaid - totalDiscount);
            const isPaid = remaining === 0 && totalPaid > 0;
            const isPartial = totalPaid > 0 && remaining > 0;

            const bg = isPaid ? '#e8f5e9' : isPartial ? '#fff3e0' : 'white';
            const border = isPaid ? '#4caf50' : isPartial ? '#ff9800' : '#e9ecef';
            const badge = isPaid ? '<span style="color:#2e7d32;font-size:10px;"><i class="fas fa-check-circle"></i> مدفوع</span>' 
                        : isPartial ? `<span style="color:#e65100;font-size:10px;"><i class="fas fa-exclamation-circle"></i> جزئي (متبقي: ${remaining.toLocaleString()})</span>`
                        : '<span style="color:#c62828;font-size:10px;"><i class="fas fa-times-circle"></i> غير مدفوع</span>';

            container.innerHTML += `
                <div onclick="selectLevel(${i}, ${pricePerLevel})" style="flex:1;min-width:80px;padding:12px;border:2px solid ${border};border-radius:10px;cursor:pointer;text-align:center;background:${bg};transition:all 0.15s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    <div style="font-weight:700;font-size:16px;color:#1a2a6c;">L${i}</div>
                    <div style="font-size:11px;color:#666;margin:4px 0;">${pricePerLevel.toLocaleString()} ج.م</div>
                    ${badge}
                </div>
            `;
        }
    }

    window.selectLevel = function(levelNum, pricePerLevel) {
        selectedLevelNumber = levelNum;
        
        const levelPayments = allPayments.filter(p => p.studentId == selectedStudentId && p.levelNumber == levelNum && p.paymentType === 'Course Payment');
        const totalPaid = levelPayments.reduce((sum, p) => sum + (parseFloat(p.amountPaid)||0), 0);
        const totalDiscount = levelPayments.reduce((sum, p) => sum + (parseFloat(p.discountAmount)||0), 0);
        const remaining = Math.max(0, pricePerLevel - totalPaid - totalDiscount);
        const isPaid = remaining === 0 && totalPaid > 0;

        const details = document.getElementById('levelPaymentDetails');
        const banner = document.getElementById('levelStatusBanner');
        const history = document.getElementById('levelPayHistory');
        const form = document.getElementById('levelPayForm');

        details.style.display = 'block';

        if (isPaid) {
            banner.style.background = '#e8f5e9';
            banner.style.color = '#2e7d32';
            banner.innerHTML = '<i class="fas fa-check-circle"></i> هذا المستوى مدفوع بالكامل';
            document.getElementById('savePayment').style.display = 'none';
            form.style.display = 'none';
        } else {
            if (remaining === pricePerLevel) {
                banner.style.background = '#fdecea';
                banner.style.color = '#c62828';
                banner.innerHTML = `<i class="fas fa-times-circle"></i> لم يتم الدفع بعد - المطلوب: ${pricePerLevel.toLocaleString()} ج.م`;
            } else {
                banner.style.background = '#fff3e0';
                banner.style.color = '#e65100';
                banner.innerHTML = `<i class="fas fa-exclamation-circle"></i> دفع جزئي - المتبقي: ${remaining.toLocaleString()} ج.م`;
            }
            form.style.display = 'block';
            document.getElementById('totalLevelFee').value = pricePerLevel;
            document.getElementById('amountPaid').value = '';
            document.getElementById('discountAmount').value = '0';
            document.getElementById('paymentDate').valueAsDate = new Date();
            document.getElementById('savePayment').style.display = 'inline-block';
            updateRemainingPreview();
        }

        if (levelPayments.length > 0) {
            history.innerHTML = `
                <div style="font-weight:700;margin-bottom:8px;color:#1a2a6c;">سجل الدفعات السابقة:</div>
                <table style="width:100%;border-collapse:collapse;font-size:12px;">
                    <tr style="background:#e9ecef;"><th style="padding:6px;border:1px solid #dee2e6;">#</th><th style="padding:6px;border:1px solid #dee2e6;">التاريخ</th><th style="padding:6px;border:1px solid #dee2e6;">المبلغ</th><th style="padding:6px;border:1px solid #dee2e6;">خصم</th></tr>
                    ${levelPayments.map((p, idx) => `<tr><td style="padding:6px;border:1px solid #dee2e6;text-align:center;">${idx+1}</td><td style="padding:6px;border:1px solid #dee2e6;">${p.paymentDate ? new Date(p.paymentDate).toLocaleDateString('ar-EG') : '-'}</td><td style="padding:6px;border:1px solid #dee2e6;font-weight:bold;color:var(--success);">${(parseFloat(p.amountPaid)||0).toLocaleString()} ج.م</td><td style="padding:6px;border:1px solid #dee2e6;">${(parseFloat(p.discountAmount)||0).toLocaleString()} ج.م</td></tr>`).join('')}
                    <tr style="background:#f8f9fa;font-weight:bold;"><td colspan="2" style="padding:6px;border:1px solid #dee2e6;">الإجمالي</td><td style="padding:6px;border:1px solid #dee2e6;color:var(--success);">${totalPaid.toLocaleString()} ج.م</td><td style="padding:6px;border:1px solid #dee2e6;">${totalDiscount.toLocaleString()} ج.م</td></tr>
                </table>
            `;
        } else {
            history.innerHTML = '';
        }
    };

    window.onPayModeChange = function() {
        const mode = document.querySelector('input[name="payMode"]:checked')?.value;
        const totalFee = parseFloat(document.getElementById('totalLevelFee').value) || 0;
        if (mode === 'full') {
            document.getElementById('amountPaid').value = totalFee;
            document.getElementById('amountPaid').readOnly = true;
            document.getElementById('amountPaid').style.background = '#f0f0f0';
        } else {
            document.getElementById('amountPaid').readOnly = false;
            document.getElementById('amountPaid').style.background = '';
            document.getElementById('amountPaid').value = '';
        }
        updateRemainingPreview();
    };

    window.updateRemainingPreview = function() {
        const total = parseFloat(document.getElementById('totalLevelFee').value) || 0;
        const paid = parseFloat(document.getElementById('amountPaid').value) || 0;
        const discount = parseFloat(document.getElementById('discountAmount').value) || 0;

        // Account for previous payments on this level
        const prevPayments = allPayments.filter(p => p.studentId == selectedStudentId && p.levelNumber == selectedLevelNumber && p.paymentType === 'Course Payment');
        const prevPaid = prevPayments.reduce((sum, p) => sum + (parseFloat(p.amountPaid)||0), 0);
        const prevDiscount = prevPayments.reduce((sum, p) => sum + (parseFloat(p.discountAmount)||0), 0);

        const newRemaining = Math.max(0, total - prevPaid - prevDiscount - paid - discount);
        const preview = document.getElementById('remainingPreview');
        if (paid > 0 || discount > 0) {
            preview.style.display = 'block';
            if (newRemaining === 0) {
                preview.style.background = '#e8f5e9';
                preview.style.borderColor = '#4caf50';
                preview.style.color = '#2e7d32';
                preview.innerHTML = '<i class="fas fa-check-circle"></i> سيتم سداد المبلغ بالكامل';
            } else {
                preview.style.background = '#fff3e0';
                preview.style.borderColor = '#ff9800';
                preview.style.color = '#e65100';
                preview.innerHTML = `<i class="fas fa-info-circle"></i> المتبقي بعد هذه الدفعة: <strong>${newRemaining.toLocaleString()} ج.م</strong>`;
            }
        } else {
            preview.style.display = 'none';
        }
    };

    function buildAddonList() {
        const student = allStudents.find(s => s.id == selectedStudentId);
        if (!student) return;
        
        let courseId = null;
        if (student.groupId) {
            const group = allGroups.find(g => g.id == student.groupId);
            if (group) courseId = group.courseId;
        }

        const relevantAddons = allAddOns.filter(a => !a.courseId || a.courseId == courseId);
        
        if (!relevantAddons.length) {
            document.getElementById('addonList').innerHTML = '<div style="padding:20px;text-align:center;color:gray;">لا توجد إضافات متاحة لهذا الطالب</div>';
            return;
        }

        document.getElementById('addonList').innerHTML = relevantAddons.map(a => {
            const alreadyPaid = allPayments.some(p => p.studentId == selectedStudentId && p.levelNumber == a.id && p.paymentType === 'AddOn Payment');
            const bg = alreadyPaid ? '#f5f5f5' : 'white';
            const opacity = alreadyPaid ? '0.6' : '1';
            const cursor = alreadyPaid ? 'not-allowed' : 'pointer';
            const badge = alreadyPaid ? '<span style="color:#2e7d32;font-size:11px;display:block;margin-top:6px;"><i class="fas fa-check-circle"></i> مدفوع بالفعل</span>' : '';
            
            return `
                <div onclick="${alreadyPaid ? '' : `selectAddon(${a.id}, '${a.name}', ${a.price||0})`}" 
                     style="flex:1;min-width:140px;padding:15px;border:2px solid ${alreadyPaid ? '#4caf50' : '#e9ecef'};border-radius:12px;cursor:${cursor};text-align:center;background:${bg};opacity:${opacity};transition:all 0.15s;"
                     ${!alreadyPaid ? 'onmouseover="this.style.borderColor=\'#3c6ec8\';this.style.transform=\'scale(1.03)\'" onmouseout="this.style.borderColor=\'#e9ecef\';this.style.transform=\'scale(1)\'"' : ''}>
                    <i class="fas fa-puzzle-piece" style="font-size:22px;color:#f4a261;display:block;margin-bottom:8px;"></i>
                    <div style="font-weight:700;">${a.name}</div>
                    <div style="color:#3c6ec8;font-weight:700;margin-top:4px;">${(a.price||0).toLocaleString()} ج.م</div>
                    ${badge}
                </div>
            `;
        }).join('');
    }

    window.selectAddon = function(addonId, addonName, addonPrice) {
        selectedAddonId = addonId;
        document.getElementById('addonPayForm').style.display = 'block';
        document.getElementById('addonSelectedInfo').innerHTML = `
            <i class="fas fa-puzzle-piece" style="color:#f4a261;"></i>
            الإضافة: <strong>${addonName}</strong> - السعر: <strong>${addonPrice.toLocaleString()} ج.م</strong>
        `;
        document.getElementById('addonPaymentDate').valueAsDate = new Date();
        document.getElementById('savePayment').style.display = 'inline-block';
    };

    async function completePayment() {
        if (!selectedStudentId) { showToast('يرجى اختيار طالب', 'warning'); return; }

        if (paymentCategory === 'level') {
            if (!selectedLevelNumber) { showToast('يرجى اختيار المستوى', 'warning'); return; }
            const amountPaid = parseFloat(document.getElementById('amountPaid').value) || 0;
            const totalFee = parseFloat(document.getElementById('totalLevelFee').value) || 0;
            const discount = parseFloat(document.getElementById('discountAmount').value) || 0;
            if (amountPaid <= 0 && discount <= 0) { showToast('أدخل المبلغ أو الخصم', 'warning'); return; }

            const prevPayments = allPayments.filter(p => p.studentId == selectedStudentId && p.levelNumber == selectedLevelNumber && p.paymentType === 'Course Payment');
            const prevPaid = prevPayments.reduce((sum, p) => sum + (parseFloat(p.amountPaid)||0), 0);
            const prevDiscount = prevPayments.reduce((sum, p) => sum + (parseFloat(p.discountAmount)||0), 0);
            const newRemaining = Math.max(0, totalFee - prevPaid - prevDiscount - amountPaid - discount);

            const paymentData = {
                studentId: selectedStudentId,
                levelNumber: selectedLevelNumber,
                paymentType: 'Course Payment',
                totalLevelFee: totalFee,
                amountPaid,
                discountAmount: discount,
                remainingBalance: newRemaining,
                notes: document.getElementById('notes').value,
                paymentDate: document.getElementById('paymentDate').value,
                createdBy: currentUser.id
            };
            await doSave(paymentData);

        } else if (paymentCategory === 'addon') {
            if (!selectedAddonId) { showToast('يرجى اختيار الإضافة', 'warning'); return; }
            const addon = allAddOns.find(a => a.id == selectedAddonId);
            const paymentData = {
                studentId: selectedStudentId,
                levelNumber: selectedAddonId, // use addon id as level number for AddOns
                paymentType: 'AddOn Payment',
                totalLevelFee: addon?.price || 0,
                amountPaid: addon?.price || 0,
                discountAmount: 0,
                remainingBalance: 0,
                notes: document.getElementById('addonNotes').value,
                paymentDate: document.getElementById('addonPaymentDate').value,
                createdBy: currentUser.id
            };
            await doSave(paymentData);
        }
    }

    async function doSave(paymentData) {
        showLoading(true);
        try {
            const res = await apiCall('savePayment', { paymentData });
            showToast(res.message || 'تم تسجيل الدفعة بنجاح', 'success');
            closeModal();
            loadData();
        } catch(e) {}
        showLoading(false);
    }

    window.deletePaymentById = async function(id) {
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

new_content = html_base + new_modal + new_script

with open('payments.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done - payments.html rebuilt with full/partial payment system")
