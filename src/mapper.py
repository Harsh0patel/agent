class Mapper:
    def map_to_template(self, structured_output, template_schema):
        template_extract = {
            "template_id": structured_output["template_id"],
            "template_name": template_schema["template_name"],
            "populated_fields":{}
        }

        for field in structured_output["fields"]:
            field_id = field["field_id"]
            template_extract["populated_fields"][field_id] = {
                "name": field["field_id"],
                "value": field["value"],
                "unit": field.get("unit", ""),
                "reasoning": field.get("reasoning", "")
            }
        return template_extract