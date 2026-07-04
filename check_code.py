with open('code.gs', 'r', encoding='utf-8') as f:
    content = f.read()

for q in ['Halls', 'Trainers', 'Groups', 'Floors', 'Departments', 'Bookings', 'Payments', 'Students']:
    if f'getSheetByName("{q}")' in content:
        print(f'{q} sheet exists in code')
    else:
        print(f'{q} sheet MISSING in code')
