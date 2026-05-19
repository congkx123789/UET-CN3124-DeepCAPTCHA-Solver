import markdown

with open('23020014_UETCN3124_CTF_Report.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Enable extra, tables, and fenced_code
html = markdown.markdown(text, extensions=['extra', 'tables', 'fenced_code', 'codehilite'])

full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 20mm;
}}
body {{ 
    font-family: 'Times New Roman', serif; 
    line-height: 1.5; 
    font-size: 14pt;
    color: #000;
}}
h1 {{ 
    text-align: center; 
    font-size: 24pt;
    margin-bottom: 20px;
    text-transform: uppercase;
}}
h2 {{ 
    font-size: 18pt;
    margin-top: 40px;
    margin-bottom: 15px;
    page-break-before: always;
    text-transform: uppercase;
    border-bottom: 1px solid #000;
}}
h3 {{ 
    font-size: 16pt;
    margin-top: 25px;
}}
h4 {{
    font-size: 14pt;
    font-style: italic;
}}
p {{ 
    text-align: justify; 
    margin-bottom: 15px;
    text-indent: 1cm;
}}
pre {{
    background-color: #f4f4f4;
    border: 1px solid #ddd;
    padding: 10px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 11pt;
    white-space: pre-wrap;
    word-wrap: break-word;
}}
code {{
    font-family: 'Courier New', Courier, monospace;
    background-color: #f4f4f4;
    padding: 2px 4px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}}
th, td {{
    border: 1px solid #000;
    padding: 8px;
    text-align: left;
}}
th {{
    background-color: #f2f2f2;
}}
.cover-page {{
    text-align: center;
    page-break-after: always;
    margin-top: 50px;
}}
.cover-title {{
    font-size: 28pt;
    font-weight: bold;
    margin: 100px 0;
}}
.cover-info {{
    font-size: 16pt;
    text-align: left;
    margin-left: 20%;
    line-height: 2;
}}
</style>
</head>
<body>
<div class="cover-page">
    <h2>TRƯỜNG ĐẠI HỌC CÔNG NGHỆ<br>ĐẠI HỌC QUỐC GIA HÀ NỘI</h2>
    <div class="cover-title">BÁO CÁO ĐỒ ÁN<br>THỰC HÀNH CTF JEOPARDY</div>
    <h3>Chủ đề: Tự động hóa giải quyết CAPTCHA bằng<br>Trí tuệ Nhân tạo (Deep Learning)</h3>
    <br><br><br>
    <div class="cover-info">
        <b>Mã và tên học phần:</b> UET.CN3124 - An toàn và an ninh mạng<br>
        <b>Họ tên sinh viên:</b> Hà Vũ Công<br>
        <b>Mã số sinh viên:</b> 23020014<br>
        <b>Ngày thực hiện:</b> Tháng 5/2026
    </div>
</div>
{html}
</body>
</html>"""

with open('report.html', 'w', encoding='utf-8') as f:
    f.write(full_html)
