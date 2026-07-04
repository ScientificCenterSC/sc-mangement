function renderSidebar() {
    const userStr = sessionStorage.getItem('loggedInUser');
    if (!userStr) {
        if (!window.location.pathname.endsWith('index.html')) {
            window.location.href = 'index.html';
        }
        return;
    }
    const user = JSON.parse(userStr);
    const perms = user.permissions || [];
    
    const currentPath = window.location.pathname.split('/').pop() || 'dashboard.html';
    
    const pageModuleMap = {
        'dashboard.html': 'dashboard',
        'students.html': 'students',
        'trainers.html': 'trainers',
        'schedule.html': 'schedule',
        'payments.html': 'payments',
        'reports.html': 'reports',
        'settings.html': 'settings',
        'departments.html': 'departments',
        'courses.html': 'courses',
        'groups.html': 'groups',
        'floors.html': 'floors',
        'roles.html': 'roles'
    };
    
    const currentModule = pageModuleMap[currentPath];
    let hasEdit = false;
    
    if (currentModule && user.roleId != 1) { // 1 is Super Admin
        const hasView = perms.some(p => p.module === currentModule && (p.action === 'view' || p.action === 'edit'));
        if (!hasView && currentPath !== 'dashboard.html') {
            alert('ليس لديك صلاحية للوصول إلى هذه الصفحة');
            window.location.href = 'dashboard.html';
            return;
        }
        hasEdit = perms.some(p => p.module === currentModule && p.action === 'edit');
        if (!hasEdit) {
            // Hide edit buttons
            const style = document.createElement('style');
            style.innerHTML = `
                .btn-primary, .add-btn, .edit-btn, .delete-btn, .btn-danger, .btn-success, button[type="submit"], .action-buttons {
                    display: none !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    const menuItems = [
        { href: 'dashboard.html', icon: 'fas fa-tachometer-alt', text: 'الرئيسية', module: 'dashboard' },
        { href: 'departments.html', icon: 'fas fa-building', text: 'الأقسام', module: 'departments' },
        { href: 'floors.html', icon: 'fas fa-layer-group', text: 'القاعات والأدوار', module: 'floors' },
        { href: 'courses.html', icon: 'fas fa-book', text: 'الكورسات', module: 'courses' },
        { href: 'groups.html', icon: 'fas fa-layer-group', text: 'الجروبات', module: 'groups' },
        { href: 'addons.html', icon: 'fas fa-plus-circle', text: 'الإضافات', module: 'courses' },
        { href: 'students.html', icon: 'fas fa-users', text: 'الطلاب', module: 'students' },
        { href: 'trainers.html', icon: 'fas fa-chalkboard-user', text: 'المدربين', module: 'trainers' },
        { href: 'schedule.html', icon: 'fas fa-calendar-alt', text: 'الجدول', module: 'schedule' },
        { href: 'payments.html', icon: 'fas fa-money-bill-wave', text: 'المدفوعات', module: 'payments' },
        { href: 'reports.html', icon: 'fas fa-chart-line', text: 'التقارير', module: 'reports' },
        { href: 'roles.html', icon: 'fas fa-user-shield', text: 'الصلاحيات', module: 'roles' },
        { href: 'settings.html', icon: 'fas fa-cog', text: 'الإعدادات', module: 'settings' }
    ];

    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        navMenu.innerHTML = '';
        menuItems.forEach(item => {
            let canView = user.roleId == 1;
            if (!canView) {
                canView = perms.some(p => p.module === item.module && (p.action === 'view' || p.action === 'edit'));
            }
            if (canView) {
                const isActive = currentPath === item.href ? 'active' : '';
                navMenu.innerHTML += `
                    <li class="nav-item">
                        <a href="${item.href}" class="nav-link ${isActive}">
                            <i class="${item.icon}"></i>
                            <span>${item.text}</span>
                        </a>
                    </li>
                `;
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', renderSidebar);
