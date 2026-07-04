import re
from collections import Counter

files = ['floors.html', 'payments.html', 'schedule.html', 'student_profile.html', 'students.html']
for fname in files:
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        scripts = len(re.findall(r'<script>', content))
        funcs = re.findall(r'(?:async )?function (\w+)', content)
        counts = Counter(funcs)
        dups = {k:v for k,v in counts.items() if v > 1}
        dup_str = str(dups) if dups else 'none'
        print(f'{fname}: {scripts} script(s), dups: {dup_str}')
    except Exception as e:
        print(f'{fname}: ERROR - {e}')
