import markdown

# Read the markdown file
with open('AUTOMATION_VALUE_ANALYSIS.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Convert to HTML
html_body = markdown.markdown(content, extensions=['tables', 'fenced_code'])

# Create full HTML document
html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dashboard Deployment Automation - Time Savings Analysis</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }
        h3 {
            color: #7f8c8d;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: Consolas, monospace;
        }
        pre {
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        ul {
            margin: 10px 0;
        }
        li {
            margin: 5px 0;
        }
        .checkmark {
            color: #27ae60;
            font-weight: bold;
        }
    </style>
</head>
<body>
''' + html_body + '''
</body>
</html>'''

# Write the HTML file
with open('AUTOMATION_VALUE_ANALYSIS.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("HTML file generated successfully!")

# Made with Bob
