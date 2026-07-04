import os

directory = "c:/Users/shahd/Downloads/ss"
for filename in os.listdir(directory):
    if filename.endswith(".html"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "sidebar.js" not in content:
            content = content.replace("</body>", '<script src="sidebar.js"></script>\n</body>')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
print("Successfully injected sidebar.js into all HTML files.")
