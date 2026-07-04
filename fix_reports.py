import os

filepath = "c:/Users/shahd/Downloads/ss/reports.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add buttons
content = content.replace('<button class="btn-print" onclick="window.print()"><i class="fas fa-print"></i> طباعة / تصدير PDF</button>', 
                          '<button class="btn-export" onclick="exportToExcel(this)"><i class="fas fa-file-excel"></i> تصدير Excel</button>\n                    <button class="btn-print" onclick="window.print()"><i class="fas fa-print"></i> طباعة / تصدير PDF</button>')

# Add JS logic for exportToExcel
export_js = """
    function exportToExcel(btnElement) {
        // Find the closest report container and then the table
        const container = btnElement.closest('.report-container');
        const table = container.querySelector('table');
        if (!table) return;

        let csv = '\\uFEFF'; // Add BOM for Excel Arabic support
        const rows = table.querySelectorAll('tr');
        
        for (let i = 0; i < rows.length; i++) {
            const row = [], cols = rows[i].querySelectorAll('td, th');
            for (let j = 0; j < cols.length; j++) {
                // Get text and escape quotes
                let data = cols[j].innerText.replace(/"/g, '""');
                row.push('"' + data + '"');
            }
            csv += row.join(',') + '\\n';
        }
        
        // Download
        const tabName = document.querySelector('.tab-btn.active').innerText.trim() || 'تقرير';
        const filename = tabName + '_' + new Date().toLocaleDateString('ar-EG') + '.csv';
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
</script>
"""
content = content.replace('</script>', export_js)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated reports.html with Excel Export")
