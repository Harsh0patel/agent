import json
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()
def get_secrate(key):
    if key in st.secrets:
        return st.secrets[key]
    else:
        os.getenv(key)

class outputGenerator():
    def __init__(self):
        self.client = Groq(api_key = get_secrate("GROQ_API_KEY"))

    def generate(self, user_question,scenario, retrived_rules, template_schema):

        rules_context = "\n\n".join([
            f"[Rule {r['paragraph_id']}] {r['article']}\n{r['text']}"
            for r in retrived_rules
        ])

        example_fields = []
        for field in template_schema['fields']:
            example_fields.append({
                "field_id": field['field_id'],
                "field_name": field['field_name']
            })

        prompt = f"""You are a precise COREP regulatory reporting assistant. You MUST return ONLY valid JSON - absolutely nothing else.
                USER QUESTION: {user_question}
                REPORTING SCENARIO: {scenario}
                RELEVANT REGULATORY RULES:{rules_context}
                TEMPLATE: {template_schema['template_name']} ({template_schema['template_id']})
                FIELDS TO POPULATE: {json.dumps(example_fields, indent=2)}
                CRITICAL INSTRUCTIONS:
                1. Return ONLY a JSON object - no explanations, no markdown, no preamble
                2. Do NOT use markdown code blocks (```json)
                3. Do NOT include any text before or after the JSON
                4. Calculate values correctly based on the scenario
                5. Use numeric values only (no currency symbols, no strings for numbers)
                EXACT OUTPUT FORMAT (copy this structure):
                {{
                "template_id": "{template_schema['template_id']}",
                "fields": [
                    {{
                    "field_id": "exact_field_id_from_schema",
                    "field_name": "exact_field_name_from_schema",
                    "value": 750000,
                    "unit": "thousands_EUR",
                    "used_rules": ["0", "1"],
                    "reasoning": "Share capital 500M + Retained earnings 200M + Share premium 100M - Goodwill 50M = 750M"
                    }}
                ]
                }}
                CALCULATION EXAMPLE for CET1:
                - If scenario says "Share capital: £500M, Retained earnings: £200M, Goodwill: £50M"
                - CET1 Capital = 500 + 200 - 50 = 650 (in millions) = 650000 (in thousands)
                - If Total Risk Exposure = £10B = 10000M = 10000000 (in thousands)
                - CET1 Ratio = (650 / 10000) × 100 = 6.5%
                Now analyze the scenario and return ONLY the JSON object:"""
        
        response = self.client.chat.completions.create(
            model= 'llama-3.3-70b-versatile',
            messages = [{
                "role": "user",
                "content": prompt
            }],
            temperature = 0.3,
            max_tokens = 1500,
            response_format = {"type": "json_object"}
        )

        response_text = response.choices[0].message.content
        json_text = json.loads(response_text)
        return json_text