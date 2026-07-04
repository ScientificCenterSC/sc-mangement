import os

filepath = "c:/Users/shahd/Downloads/ss/courses.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the content-area div
start_idx = content.find('<div class="content-area">')
end_idx = content.find('<!-- Course Modal -->')

new_html = """<div class="content-area">
            <!-- Toolbar -->
            <div class="toolbar" style="margin-bottom: 25px;">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="بحث باسم الكورس أو الإضافة...">
                    <button id="searchBtn"><i class="fas fa-search"></i> بحث</button>
                </div>
            </div>

            <!-- Courses Section -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: var(--dark-blue); margin: 0;"><i class="fas fa-book"></i> الكورسات الأساسية</h3>
                <button class="btn-add" id="addBtn" style="padding: 10px 20px; background: var(--success); color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold;"><i class="fas fa-plus"></i> إضافة كورس</button>
            </div>
            
            <div class="users-table-container" id="coursesSection" style="margin-bottom: 40px; background: white; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow-x: auto;">
                <table class="users-table" style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: var(--dark-blue); color: white;">
                            <th style="padding: 15px; text-align: right;">ID</th>
                            <th style="padding: 15px; text-align: right;">اسم الكورس</th>
                            <th style="padding: 15px; text-align: right;">القسم</th>
                            <th style="padding: 15px; text-align: right;">سعر المستوى (ج.م)</th>
                            <th style="padding: 15px; text-align: right;">عدد المستويات</th>
                            <th style="padding: 15px; text-align: center;">الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="coursesTableBody">
                        <tr><td colspan="6" style="text-align: center; padding: 20px;">جاري التحميل...</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- AddOns Section -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: var(--dark-blue); margin: 0;"><i class="fas fa-plus-circle"></i> الملحقات والإضافات (AddOns)</h3>
                <button class="btn-add" id="addAddonBtn" style="padding: 10px 20px; background: var(--info); color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold;"><i class="fas fa-plus"></i> إضافة ملحق</button>
            </div>

            <div class="users-table-container" id="addonsSection" style="margin-bottom: 20px; background: white; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow-x: auto;">
                <table class="users-table" style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: var(--dark-blue); color: white;">
                            <th style="padding: 15px; text-align: right;">ID</th>
                            <th style="padding: 15px; text-align: right;">اسم الإضافة</th>
                            <th style="padding: 15px; text-align: right;">السعر (ج.م)</th>
                            <th style="padding: 15px; text-align: right;">الكورس المرتبط</th>
                            <th style="padding: 15px; text-align: center;">الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="addonsTableBody">
                        <tr><td colspan="5" style="text-align: center; padding: 20px;">جاري التحميل...</td></tr>
                    </tbody>
                </table>
            </div>

        </div>
    </main>
</div>
"""
content = content[:start_idx] + new_html + content[end_idx:]

# Fix JS to match the layout
js_start = content.find('function setupEvents() {')
js_end = content.find('function switchTab', js_start)

new_events = """function setupEvents() {
        document.getElementById('searchBtn').addEventListener('click', () => filterAndRender());
        document.getElementById('searchInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') filterAndRender(); });
        
        document.getElementById('addBtn').addEventListener('click', () => openCourseModal());
        document.getElementById('addAddonBtn').addEventListener('click', () => openAddonModal());
        
        document.getElementById('closeCourseModal').addEventListener('click', () => closeModals());
        document.getElementById('cancelCourseModal').addEventListener('click', () => closeModals());
        document.getElementById('saveCourseBtn').addEventListener('click', () => saveCourse());
        
        document.getElementById('closeAddonModal').addEventListener('click', () => closeModals());
        document.getElementById('cancelAddonModal').addEventListener('click', () => closeModals());
        document.getElementById('saveAddonBtn').addEventListener('click', () => saveAddon());
    }
"""
content = content[:js_start] + new_events + content[js_end:]

# Fix filterAndRender to render both
filter_start = content.find('function filterAndRender() {')
filter_end = content.find('function renderCourses', filter_start)
new_filter = """function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        
        let filteredCourses = allCourses.filter(s => (s.name && s.name.toLowerCase().includes(searchTerm)) || (s.deptName && s.deptName.toLowerCase().includes(searchTerm)));
        renderCourses(filteredCourses);
        
        let filteredAddons = allAddOns.filter(s => s.name && s.name.toLowerCase().includes(searchTerm));
        renderAddons(filteredAddons);
    }
"""
content = content[:filter_start] + new_filter + content[filter_end:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Reverted courses.html style")
