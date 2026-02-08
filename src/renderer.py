class Renderer:
    def render_html(self, template_extract, template_schema):

        html = """
        <html>
            <head>
                <style>
                    body {font-family: Arial, sans-serif;margin: 20px;background-color: #000000;color: #f1f1f1;}
                    h1 {color: #ffffff;}
                    table {border-collapse: collapse;width: 100%;margin-top: 20px;background-color: #111111;}
                    th, td {border: 1px solid #444444;padding: 12px;text-align: left;color: #f1f1f1;}
                    th {background-color: #1f6feb;color: white;}
                    .populated {background-color: #1e7f5c;color: #ffffff;}
                    .empty {background-color: #8b2c2c;color: #ffffff;}
                </style>
            </head>
            <body>
                <h1>{template_schema['template_name']} ({template_schema['template_id']})</h1>
                <table>
                    <tr>
                        <th>Field ID</th>
                        <th>Field Name</th>
                        <th>Value</th>
                        <th>Unit</th>
                        <th>Status</th>
                    </tr>"""
        
        for field in template_schema["fields"]:
            field_id = field["field_id"]

            if field_id in template_extract["populated_fields"]:
                populated = template_extract["populated_fields"][field_id]
                status_class = "populated"
                value = populated["value"]
                unit = populated["unit"]
                status = "Populated"
            else:
                status_class = "empty"
                value = "-"
                unit = "-"
                status = "x Missing"
            
            html += f"""
                        <tr class="{status_class}">
                            <td>{field_id}</td>
                            <td>{field["field_name"]}</td>
                            <td>{value}</td>
                            <td>{unit}</td>
                            <td>{status}</td>
                        </tr> """
            
            html += """
                        </table>
                    </body>
                    </html>
                    """
            return html