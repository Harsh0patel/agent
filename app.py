import streamlit as st
import json
from src import agent, Audit_logger, mapper, rag, renderer, validator

st.set_page_config(page_title="COREP Reporting Assitant", layout="wide")
st.title("LLM-Assisted PRA COREP Reporting Assistant")
st.markdown("Prototype for own Funds (c 01.00) and Capital Requirement (c 02.00)")

@st.cache_resource
def init_system():
    retriever = rag.RAG()
    try:
        retriever.load_index(
            index_path = 'data/processed/vector_index.faiss',
            metadata_path = 'data/processed/metadata.pkl'
        )
        print("Loaded existing vector index")
    except FileNotFoundError:
        print("Index not found. Building new index...")
        retriever.load_docs([
            'data/rag_text/c01_instructions.txt.txt',
            'data/rag_text/c01_validation_rules.txt.txt',
            'data/rag_text/c02_instructions.txt.txt',
            'data/rag_text/c02_validation_rules.txt.txt'
            ])
        retriever.save_index()
    return retriever

retriever = init_system()

col1, col2 = st.columns(2)

with col1:
    template_choice = st.selectbox(
        "Select COREP Template:",
        ["C_01.00 - Own Funds", "C_02.00 - Capital Requirements"]
    )

    user_question = st.text_area(
        "Your Question:",
        placeholder = "e.g., how do i calculate CET1 capital?",
        height= 100
    )

with col2:
    scenario = st.text_area(
        "Reporting Scenario:",
        placeholder="e.g., Bank has $200M retained earnings, $10B total risk exposure",
        height=100
    )

if st.button("Generate COREP Report", type="primary"):
    if not user_question or not scenario:
        st.error("Please provide both a question and scenario")
    else:
        with st.spinner("Processing..."):
            template_id = "C_01.00" if "C_01.00" in template_choice else "C_02.00"
            schema_file = f"data/tamplates/{'c01' if template_id == 'C_01.00' else 'c02'}_schema.json"

            with open(schema_file) as f:
                template_schema = json.load(f)
            
            st.subheader("step 1: Retrieved Regulatory Text")
            retrieved_rules = retriever.Search(f"{user_question} {scenario}", top_k=2)

            for i, rule in enumerate(retrieved_rules):
                with st.expander(f"Rule {i+1}: {rule['article']} (Score: {rule['relevance_score']:.2f})"):
                    st.markdown(f"**Source:** `{rule['source']}`")
                    st.write(rule['text'])

            st.subheader("Step 2: LLM Structured Output")
            llm = agent.outputGenerator()
            structured_output = llm.generate(user_question, scenario, retrieved_rules, template_schema)
            st.json(structured_output)

            st.header("step 3: Populated Template Extract")
            mapper = mapper.Mapper()
            template_extract = mapper.map_to_template(structured_output, template_schema)

            renderer = renderer.Renderer()
            html_output = renderer.render_html(template_extract, template_schema)
            st.html(html_output, width=400)

            st.subheader("Step 4: Validation Results")
            validator = validator.validator(validation_rules={})
            validation_report = validator.validation(template_extract, template_schema)

            if validation_report["overall_status"] == "PASS":
                st.success("All validation passed")
            else:
                st.error("validation issues found")
            
            for result in validation_report["validation_results"]:
                if result["chunks"]:
                    with st.expander(f"{result['field_name']}"):
                        for check in result["chunks"]:
                            if check["status"] == "PASS":
                                st.success(f"{check['check']}: {check['message']}")
                            else:
                                st.error(f" {check['check']}: {check['message']}")

        st.subheader("Step 5: Audit Log")
        auditor = Audit_logger.Auditlogger()
        audit_log = auditor.generate_audit_log(
            user_question=user_question,scenario=scenario, retrieved_rules=retrieved_rules,
            structured_output=structured_output, validation_report=validation_report
            )
        
        for field_audit in audit_log["fields_audit"]:
            with st.expander(f"{field_audit['field_name']} = {field_audit['populated_value']}"):
                st.markdown(f"**Reasoning:** {field_audit['reasoning']}")
                st.markdown("**Regulatory Justification:**")
                for just in field_audit["regulatory_justification"]:
                    st.markdown(f"""
                                - **{just['article_reference']}** (Relevance: {just['relevance_score']:.2f})
                                - {just['rule_text']}
                                - *Source: {just['source']}*
                                """)
        
        st.subheader("Download outputs")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                "Structured Output (JSON)",
                json.dumps(structured_output, indent=2),
                "structured_output.json",
                "application/json"
            )

        with col2:
            if html_output:
                st.download_button(
                    "Template Extract (HTML)",
                    html_output,
                    "template_extract.html",
                    "text/html"
                )

        with col3:
            st.download_button(
                "Audit Log (JSON)",
                json.dumps(audit_log, indent=2),
                "audit_log.json",
                "application/json"
            )

st.sidebar.markdown("""
### About
This prototype demostrates an LLM-assisted COREP reporting assistant for UK banks.

**Features:**
- RAG retreval of PRA Rulebook & COREP instructions
- Human-readable template extracts
- Basic validation rules
- Compreshensive audit logs

**Scope:**
- C 01.00: Own Funds
- C 02.00: Captial Requirements
""")