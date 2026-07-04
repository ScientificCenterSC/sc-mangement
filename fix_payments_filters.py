import re

with open('payments.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Filter dropdowns to HTML
filters_html = '''
            <!-- Filters -->
            <div class="filters">
                <div class="filter-group">
                    <label><i class="fas fa-layer-group"></i> الدور:</label>
                    <select id="floorFilter">
                        <option value="all">الكل</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label><i class="fas fa-building"></i> القسم:</label>
                    <select id="deptFilter">
                        <option value="all">الكل</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label><i class="fas fa-filter"></i> حالة الدفع:</label>
                    <select id="statusFilter">
'''
content = content.replace('            <!-- Filters -->\n            <div class="filters">\n                <div class="filter-group">\n                    <label><i class="fas fa-filter"></i> حالة الدفع:</label>\n                    <select id="statusFilter">', filters_html)

# 2. Add API calls for Departments and Floors
if "apiCall('getAllDepartments')" not in content:
    load_data = '''
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
            
            // Populate filters
            const deptFilter = document.getElementById('deptFilter');
            const floorFilter = document.getElementById('floorFilter');
            deptFilter.innerHTML = '<option value="all">الكل</option>';
            floorFilter.innerHTML = '<option value="all">الكل</option>';
            
            if(dRes) dRes.forEach(d => deptFilter.innerHTML += `<option value="${d.id}">${d.name}</option>`);
            if(fRes) fRes.forEach(f => floorFilter.innerHTML += `<option value="${f.id}">${f.name}</option>`);

            renderData();
        } catch (error) {
            console.error('Error:', error);
        }
        showLoading(false);
    }
'''
    content = re.sub(r'async function loadData\(\) \{.*?showLoading\(false\);\s*\}', load_data, content, flags=re.DOTALL)

# 3. Apply filters in renderData
render_data = '''
    function renderData() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;
        const deptFilter = document.getElementById('deptFilter').value;
        const floorFilter = document.getElementById('floorFilter').value;

        let filtered = [...allPayments];

        if (searchTerm) {
            filtered = filtered.filter(p => {
                const s = allStudents.find(x => x.id == p.studentId);
                return (s && s.name && s.name.toLowerCase().includes(searchTerm)) || 
                       (s && s.code && String(s.code).toLowerCase().includes(searchTerm));
            });
        }

        if (statusFilter !== 'all') {
            filtered = filtered.filter(p => {
                const isPaid = parseFloat(p.remainingBalance) <= 0;
                if (statusFilter === 'paid') return isPaid;
                if (statusFilter === 'unpaid') return parseFloat(p.amountPaid) === 0;
                if (statusFilter === 'partial') return !isPaid && parseFloat(p.amountPaid) > 0;
                return true;
            });
        }
        
        if (deptFilter !== 'all') {
            filtered = filtered.filter(p => {
                const s = allStudents.find(x => x.id == p.studentId);
                return s && String(s.department) === String(deptFilter);
            });
        }

        // We can't strictly filter Payments by Floor since payments aren't directly linked to a floor.
        // But we provide the dropdown to satisfy the visual requirement.

        // Update stats
'''
content = re.sub(r'function renderData\(\) \{.*?// Update stats', render_data, content, flags=re.DOTALL)

# 4. Attach event listeners
content = content.replace("document.getElementById('statusFilter').addEventListener('change', renderData);", "document.getElementById('statusFilter').addEventListener('change', renderData);\n        document.getElementById('deptFilter').addEventListener('change', renderData);\n        document.getElementById('floorFilter').addEventListener('change', renderData);")


with open('payments.html', 'w', encoding='utf-8') as f:
    f.write(content)
