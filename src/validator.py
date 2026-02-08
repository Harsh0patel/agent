class validator:
    def __init__(self, validation_rules):
        self.rules = validation_rules

    def validation(self, template_extract, template_schema):

        validation_report = {
            "template_id": template_extract["template_id"],
            "validation_results":[],
            "overall_status": "PASS"
        }

        for field in template_schema["fields"]:
            field_id = field["field_id"]
            result = {
                "field_id":field_id,
                "field_name": field["field_name"],
                "chunks": []
            }

            if field.get("validation", "").startswith("required"):
                if field_id not in template_extract["populated_fields"]:
                    result["chunks"].append({
                        "check": "Required field",
                        "status": "FAIL",
                        "message": f"Field {field_id} is required but missing"
                    })
                    validation_report["overall_status"] = "FAIL"
                else:
                    result["chunks"].append({
                        "check": "Required field",
                        "status": "PASS",
                        "message": "Field is populated"
                    })
            
            if field_id in template_extract["populated_fields"]:
                value = template_extract["populated_fields"][field_id]["value"]

                if field["data_type"] == "numeric" and not isinstance(value, (int, float)):
                    result["chunks"].append({
                        "check": "Data type",
                        "status": "FAIL",
                        "message": f"Expected numeric got {type(value).__name__}"
                    })
                    validation_report["overall_status"] = "FAIL"
                
            if "must be >=" in field.get("validation", ""):
                threshold_str = field["validation"].split(">=")[1].strip()
                threshold_str = threshold_str.split("%")[0].strip()
                threshold = float(threshold_str)

                if isinstance(value, (int, float)) and value < threshold:
                    result["chunks"].append({
                        "check": "Threshold check",
                        "status": "FAIL",
                        "message": f"Value {value} below minimum {threshold}"
                    })
                    validation_report["overall_status"] = "FAIL"
                else:
                    result["chunks"].append({
                        "check": "Threshold check",
                        "status": "PASS",
                        "message": f"Value {value} meets minimum requirement"
                    })

            validation_report["validation_results"].append(result)
        return validation_report