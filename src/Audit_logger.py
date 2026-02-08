from datetime import datetime

class Auditlogger:
    def generate_audit_log(self, user_question, scenario, retrieved_rules, structured_output, validation_report):

        rules_dict = {r['paragraph_id']: r for r in retrieved_rules}

        audit_log = {
            "timestamp": datetime.now().isoformat(),
            "user_question": user_question,
            "scenario": scenario,
            "template_id": structured_output["template_id"],
            "fields_audit": []
        }

        for field in structured_output["fields"]:
            field_audit = {
                "field_id": field["field_id"],
                "field_name": field["field_name"],
                "populated_value": field["value"],
                "unit": field.get("unit", ""),
                "reasoning": field.get("reasoning", ""),
                "regulatory_justification":[]
            }

            for para_id in field.get("used_rules", []):
                if para_id in rules_dict:
                    rule = rules_dict[para_id]
                    field_audit["regulatory_justification"].append({
                        "paragraph_id": para_id,
                        "article_reference": rule["article"],
                        "rule_text": rule["text"],
                        "source": rule["source"],
                        "relevance_score": rule["relevance_score"]
                    })

            field_validation = next((v for v in validation_report["validation_results"] if v["field_id"] == field["field_id"]),None)

            if field_validation:
                field_audit["validation_status"] = field_validation["chunks"]
            
            audit_log["fields_audit"].append(field_audit)
        audit_log["overall_validation"] = validation_report["overall_status"]

        return audit_log