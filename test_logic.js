function updateLevelFilters() {
    const deptId = document.getElementById('deptFilter')?.value;
    const levelFilter = document.getElementById('levelFilter');
    
    if (levelFilter) {
        let maxLevels = 0;
        let filteredCourses = typeof allCourses !== 'undefined' ? allCourses : [];
        if (deptId !== 'all' && deptId) {
            filteredCourses = filteredCourses.filter(c => c.deptId == deptId);
        }
        
        filteredCourses.forEach(c => {
            const lvls = parseInt(c.durationLevels) || 1;
            if (lvls > maxLevels) maxLevels = lvls;
        });
        
        let levelHtml = '<option value="all">الكل</option>';
        for (let i = 1; i <= maxLevels; i++) {
            levelHtml += <option value="">Level </option>;
        }
        levelFilter.innerHTML = levelHtml;
        
        // Reset children
        const programFilter = document.getElementById('programFilter');
        if (programFilter) programFilter.innerHTML = '<option value="all">الكل</option>';
        const groupFilter = document.getElementById('groupFilter');
        if (groupFilter) groupFilter.innerHTML = '<option value="all">الكل</option>';
    }
}

function updateProgramFilters() {
    const deptId = document.getElementById('deptFilter')?.value;
    const levelId = document.getElementById('levelFilter')?.value;
    const programFilter = document.getElementById('programFilter');
    
    if (programFilter) {
        let filteredCourses = typeof allCourses !== 'undefined' ? allCourses : [];
        
        if (deptId !== 'all' && deptId) {
            filteredCourses = filteredCourses.filter(c => c.deptId == deptId);
        }
        if (levelId !== 'all' && levelId) {
            // Only keep courses that have this level (durationLevels >= levelId)
            const lvl = parseInt(levelId);
            filteredCourses = filteredCourses.filter(c => (parseInt(c.durationLevels) || 1) >= lvl);
        }
        
        let programHtml = '<option value="all">الكل</option>';
        filteredCourses.forEach(c => programHtml += <option value=""></option>);
        programFilter.innerHTML = programHtml;
        
        // Reset children
        const groupFilter = document.getElementById('groupFilter');
        if (groupFilter) groupFilter.innerHTML = '<option value="all">الكل</option>';
    }
}

function updateGroupFilters() {
    const deptId = document.getElementById('deptFilter')?.value;
    // Note: The user said levelFilter filters Programs, and Group filter filters groups. 
    // In code.gs, group does NOT necessarily have a level (we rely on course). 
    // Wait, the user specifically said: "سيتم الاعتماد على خاصية level المسجلة في الجروب لفلترة الجروبات."
    // Ah! "We will depend on the level property recorded in the Group to filter groups."
    // So Groups DO have a level!
    const levelId = document.getElementById('levelFilter')?.value;
    const progId = document.getElementById('programFilter')?.value;
    
    const groupFilter = document.getElementById('groupFilter');
    const studentGroup = document.getElementById('studentGroup');
    
    let filteredGroups = typeof groups !== 'undefined' ? groups : (typeof allGroups !== 'undefined' ? allGroups : []);
    
    if (deptId !== 'all' && deptId) filteredGroups = filteredGroups.filter(g => g.deptId == deptId);
    if (levelId !== 'all' && levelId) filteredGroups = filteredGroups.filter(g => String(g.level) === String(levelId));
    if (progId !== 'all' && progId) filteredGroups = filteredGroups.filter(g => g.courseId == progId);
    
    let options = '<option value="all">الكل</option>';
    let modalOptions = '<option value="">اختر الجروب</option>';
    
    filteredGroups.forEach(g => {
        options += <option value=""></option>;
        modalOptions += <option value=""></option>;
    });
    
    if (groupFilter) groupFilter.innerHTML = options;
    if (studentGroup) studentGroup.innerHTML = modalOptions;
}
