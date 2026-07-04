const globalFilterHtml = 
<div class="global-filter-bar" style="background: var(--white); padding: 15px 25px; border-radius: 16px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <div style="display: flex; gap: 15px; flex-wrap: wrap; align-items: flex-end;">
        <div class="filter-group">
            <label><i class="fas fa-building"></i> القسم</label>
            <select id="globalDeptFilter"><option value="all">الكل</option></select>
        </div>
        <div class="filter-group">
            <label><i class="fas fa-book"></i> الكورس</label>
            <select id="globalCourseFilter"><option value="all">الكل</option></select>
        </div>
        <div class="filter-group">
            <label><i class="fas fa-users"></i> الجروب</label>
            <select id="globalGroupFilter"><option value="all">الكل</option></select>
        </div>
        <div class="filter-group">
            <label><i class="fas fa-money-check-alt"></i> حالة الدفع</label>
            <select id="globalStatusFilter">
                <option value="all">الكل</option>
                <option value="paid">مدفوع بالكامل</option>
                <option value="partial">مدفوع جزئياً</option>
                <option value="unpaid">غير مدفوع</option>
            </select>
        </div>
        <button class="btn-filter" id="applyGlobalFilter" style="padding: 10px 20px; background: var(--primary-blue); color: white; border: none; border-radius: 10px; height: 42px; cursor: pointer;">
            <i class="fas fa-filter"></i> تطبيق الفلاتر
        </button>
    </div>
</div>
;
