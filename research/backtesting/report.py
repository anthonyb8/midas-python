
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class HTMLReportGenerator:
    def __init__(self, file_name:str):
        self.file_path = f"/Users/anthony/git-projects/midas/research/strategies/{file_name}/outputs/{file_name}.html"
        self.html_content = "<html><head><title>Backtest Report</title></head><body>"

    def add_section_title(self, title: str):
        self.html_content += f"<h2>{title}</h2>\n"

    def add_summary(self, summary_dict):
        self.html_content += "<ul>\n"
        for key, value in summary_dict.items():
            self.html_content += f"<li><strong>{key}:</strong> {value}</li>\n"
        self.html_content += "</ul>\n"

    def add_image(self, plot_func, *args, **kwargs):
        image_data = self.get_plot_base64(plot_func, *args, **kwargs)
        self.html_content += f'<img src="data:image/png;base64,{image_data}"><br>'

    def add_table(self, headers, rows):
        self.html_content += "<table border='1'>\n<tr>"
        for header in headers:
            self.html_content += f"<th>{header}</th>"
        self.html_content += "</tr>\n"
        for row in rows:
            self.html_content += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>\n"
        self.html_content += "</table>\n"

    def add_dataframe(self, df: pd.DataFrame, title: str = None):
        if title:
            self.add_section_title(title)
        html_table = df.to_html(index=False, border=1)
        self.html_content += html_table + "\n"

    def add_html(self, html: str):
        self.html_content += html + "\n"
        
    def get_plot_base64(self, plot_func, *args, **kwargs):
        buf = BytesIO()
        plot_func(*args, **kwargs)
        plt.savefig(buf, format='png')
        plt.close()
        return base64.b64encode(buf.getvalue()).decode()

    def complete_report(self):
        self.html_content += "</body></html>"
        with open(self.file_path, "w") as file:
            file.write(self.html_content)