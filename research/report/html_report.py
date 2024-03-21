
import base64
import pandas as pd
from io import BytesIO
from textwrap import dedent
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Callable

class HTMLReportGenerator:
    def __init__(self, file_name: str) -> None:
        self.file_path = f"/Users/anthony/git-projects/midas_python/research/strategies/{file_name}/outputs/{file_name}.html"
        self.html_content = dedent("""
                                   <!DOCTYPE html>
                                    <html>
                                    <head>
                                        <title>Backtest Report</title>
                                        <link rel="stylesheet" href="../../../report/styles.css">
                                    </head>
                                    <body>
                                        <h1>Backtest Report</h1>
                                    """)

    def add_html(self, html: str) -> None:
        self.html_content += html + "\n"

    def add_image(self, plot_func: Callable, indent: int=0, *args: Any, **kwargs: Any) -> None:
        # Define the base indentation as a string of spaces
        base_indent = "    " * indent

        image_data = self._get_plot_base64(plot_func, *args, **kwargs)
        self.html_content += f'{base_indent}<img src="data:image/png;base64,{image_data}"><br>\n'

    def _get_plot_base64(self, plot_func: Callable, *args: Any, **kwargs: Any) -> None:
        buf = BytesIO()
        plot_func(*args, **kwargs)
        plt.savefig(buf, format='png')
        plt.close()
        return base64.b64encode(buf.getvalue()).decode()

    def add_table(self, headers: List[Any], rows: List[List[Any]], indent: int=0) -> None:
        # Define the base indentation as a string of spaces
        base_indent = "    " * indent
        next_indent = "    " * (indent + 1)  

        self.html_content += f"{base_indent}<table  border='1' class='dataframe'>\n"
        self.html_content += f"{next_indent}<thead>\n"
        self.html_content += f"{next_indent + base_indent}<tr>\n"

        for header in headers:
            self.html_content += f"{next_indent + (base_indent*2)}<th>{header}</th>\n"
        self.html_content += f"{next_indent + base_indent}</tr>\n{next_indent}</thead>\n{next_indent}<tbody>\n"

        for row in rows:
            self.html_content += f"{next_indent + base_indent}<tr>\n"
            for cell in row:
                self.html_content += f"{next_indent + (base_indent*2)}<td>{cell}</td>\n"
            self.html_content += f"{next_indent + base_indent}</tr>\n"
        self.html_content += f"{next_indent}</tbody>\n{base_indent}</table>\n"

    def complete_report(self) -> None:
        """Finalizes the HTML report content and writes it to the specified file."""
        self.html_content += "</body>\n</html>"
        with open(self.file_path, "w") as file:
            file.write(self.html_content)

    def add_section_title(self, title: str) -> None:
        self.html_content += f"<h2>{title}</h2>\n"

    def add_list(self, summary_dict: Dict) -> None:
        self.html_content += "<ul>\n"
        for key, value in summary_dict.items():
            self.html_content += f"<li><strong>{key}:</strong> {value}</li>\n"
        self.html_content += "</ul>\n"

    def add_dataframe(self, df: pd.DataFrame, title: str = None) -> None:
        if title:
            self.add_section_title(title)
        html_table = df.to_html(index=False, border=1)
        self.html_content += html_table + "\n"