import re

with open('courses.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove AddOns section from courses.html HTML
addons_html = r'<!-- AddOns Section -->.*?<!-- Course Modal -->'
content = re.sub(addons_html, '<!-- Course Modal -->', content, flags=re.DOTALL)

# Remove AddOn Modal from courses.html HTML
addon_modal = r'<!-- AddOn Modal -->.*?<script>'
content = re.sub(addon_modal, '<script>', content, flags=re.DOTALL)

# Remove AddOns from JS
content = re.sub(r"document\.getElementById\('addAddonBtn'\)\.addEventListener\('click', \(\) => openAddonModal\(\)\);", '', content)
content = re.sub(r"document\.getElementById\('closeAddonModal'\)\.addEventListener\('click', \(\) => closeModals\(\)\);", '', content)
content = re.sub(r"document\.getElementById\('cancelAddonModal'\)\.addEventListener\('click', \(\) => closeModals\(\)\);", '', content)
content = re.sub(r"document\.getElementById\('saveAddonBtn'\)\.addEventListener\('click', \(\) => saveAddon\(\)\);", '', content)

content = re.sub(r"apiCall\('getAllAddOns'\)", '', content)
content = re.sub(r"const \[coursesRes, deptsRes, addonsRes\] = await Promise\.all\(\[", "const [coursesRes, deptsRes] = await Promise.all([", content)
content = re.sub(r"allAddOns = addonsRes \|\| \[\];", "", content)
content = re.sub(r"const addonCourseSelect = document\.getElementById\('addonCourseId'\);.*?\.join\(''\);", "", content, flags=re.DOTALL)

content = re.sub(r"let filteredAddons = allAddOns\.filter.*?renderAddons\(filteredAddons\);", "", content, flags=re.DOTALL)

content = re.sub(r"function renderAddons\(data\) \{.*?\n    \}", "", content, flags=re.DOTALL)

content = re.sub(r"// --- ADDONS ---.*?function closeModals\(\)", "function closeModals()", content, flags=re.DOTALL)
content = re.sub(r"document\.getElementById\('addonModal'\)\.classList\.remove\('show'\);", "", content)

content = re.sub(r"window\.editAddon = editAddon; window\.deleteAddon = deleteAddon;", "", content)

with open('courses.html', 'w', encoding='utf-8') as f:
    f.write(content)
