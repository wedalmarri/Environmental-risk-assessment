
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from html import escape

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Environmental Risk Assessment",
    page_icon="🌿",
    layout="wide"
)

# ==================================================
# GREEN DESIGN
# ==================================================
st.markdown("""
<style>
.stApp {
    background-color: #f4f8f3;
}
h1, h2, h3 {
    color: #205c3b;
}
.main-title {
    background: linear-gradient(110deg, #14532d, #4c956c);
    color: white;
    padding: 24px;
    border-radius: 14px;
    text-align: center;
    margin-bottom: 20px;
}
.main-title h1 {
    color: white;
}
.main-title p {
    color: white;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #d5e6d7;
    padding: 14px;
    border-radius: 12px;
}
div.stButton > button {
    background-color: #26734d;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}
div.stButton > button:hover {
    background-color: #14532d;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# CRITERIA AND EXACT SCORES FROM YOUR REFERENCE
# ==================================================
CRITERIA = {
    "A": {
        "title": "Quantity / Magnitude",
        "options": [
            ("Low", 1),
            ("Moderate", 2),
            ("High", 3),
            ("Very High", 4),
            ("Excessive", 5),
        ],
    },
    "B": {
        "title": "Occurrence / Frequency",
        "options": [
            ("Once a Month or Less Frequent", 1),
            ("Once a Week", 2),
            ("Once a Day", 3),
            ("Several Times a Day", 4),
            ("Continuous", 5),
        ],
    },
    "C": {
        "title": "Duration",
        "options": [
            ("Less than 1 year", 1),
            ("More than 1 year, less than life of project", 2),
            ("Greater than life of project", 3),
        ],
    },
    "D": {
        "title": "Scale / Severity",
        "options": [
            ("Small Area / Negligible Impact", 1),
            ("Localized / Cause Discomfort", 2),
            ("Localized Deposition Impact or Resource Consumption", 3),
            ("Regional / Affect Flora & Fauna", 3),
            ("Regional / Kills Flora & Fauna", 3),
            ("Regional / Human Health Effect", 4),
            ("Global Scale / Cause Human Fatality", 5),
        ],
    },
    "E": {
        "title": "Legislation / Compliance",
        "options": [
            ("In Compliance", 1),
            ("Not Meeting Legislation", 2),
        ],
    },
    "F": {
        "title": "Controls and Detection",
        "options": [
            ("Available and Effective", 1),
            ("Not Reliable Control", 2),
            ("Ineffective Controls", 3),
            ("Absence of Control", 4),
        ],
    },
    "G": {
        "title": "Preventive Mechanism",
        "options": [
            ("Immediately Available", 1),
            ("Available within 2 hours", 2),
            ("Available within 24 hours", 3),
            ("More than a week", 4),
            ("More than a month", 5),
        ],
    },
}

# ==================================================
# RISK CLASSIFICATION
# Reference: 7–19 Very Low, 20–39 Low,
# 40–59 Moderate, 60–79 High, 80–100 Extreme.
# Scores over 100 are also Extreme.
# ==================================================
def classify_risk(score):
    if score >= 80:
        return "Extreme"
    if score >= 60:
        return "High"
    if score >= 40:
        return "Moderate"
    if score >= 20:
        return "Low"
    return "Very Low"


def risk_color(level):
    return {
        "Very Low": "#d9ead3",
        "Low": "#93c47d",
        "Moderate": "#ffd966",
        "High": "#f6b26b",
        "Extreme": "#e06666",
    }.get(level, "#ffffff")


def calculate_score(scores):
    result = 1
    for letter in CRITERIA:
        result *= scores[letter]
    return result


# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="main-title">
    <h1>🌿 Environmental Risk Assessment</h1>
    <p>Assess pollutants, calculate environmental risk,
    and prepare your assessment report.</p>
</div>
""", unsafe_allow_html=True)

st.write(
    "Enter your project details and assess each pollutant "
    "using the seven criteria. Add as many pollutants as needed."
)

# ==================================================
# PROJECT INFORMATION
# ==================================================
st.header("1. Project Information")

project_name = st.text_input(
    "Project Name",
    placeholder="Enter your project name"
)

project_location = st.text_input(
    "Project Location",
    placeholder="Enter the project location"
)

project_description = st.text_area(
    "Project Description",
    placeholder="Describe the project and its activities"
)

st.divider()

# ==================================================
# SESSION STATE
# ==================================================
if "pollutants" not in st.session_state:
    st.session_state.pollutants = []

if "pollutant_counter" not in st.session_state:
    st.session_state.pollutant_counter = 0

# ==================================================
# POLLUTANT ASSESSMENT FORM
# ==================================================
st.header("2. Assess a Pollutant")

with st.form("pollutant_assessment_form", clear_on_submit=True):
    pollutant_name = st.text_input(
        "Pollutant Emitted",
        placeholder="e.g., NO, NO₂, CO₂, wastewater"
    )

    st.caption(
        "Choose one description for each criterion. "
        "The corresponding numeric score is assigned automatically."
    )

    selected_scores = {}
    selected_descriptions = {}

    for letter, criterion in CRITERIA.items():
        st.subheader(f"{letter} — {criterion['title']}")

        # Dropdown displays the description only.
        # The numeric score remains in the background.
        descriptions = [
            description
            for description, score in criterion["options"]
        ]

        selected_description = st.selectbox(
            f"Select {letter}",
            options=descriptions,
            key=f"assessment_{letter}"
        )

        matching_score = next(
            score
            for description, score in criterion["options"]
            if description == selected_description
        )

        selected_scores[letter] = matching_score
        selected_descriptions[letter] = selected_description

    add_pollutant = st.form_submit_button(
        "➕ Add Pollutant to Assessment",
        use_container_width=True
    )

    if add_pollutant:
        if not pollutant_name.strip():
            st.error("Please enter the pollutant name.")
        else:
            h_value = calculate_score(selected_scores)

            st.session_state.pollutant_counter += 1

            st.session_state.pollutants.append({
                "ID": st.session_state.pollutant_counter,
                "Pollutant Emitted": pollutant_name.strip(),
                "A": selected_scores["A"],
                "B": selected_scores["B"],
                "C": selected_scores["C"],
                "D": selected_scores["D"],
                "E": selected_scores["E"],
                "F": selected_scores["F"],
                "G": selected_scores["G"],
                "H": h_value,
                "Risk Level": classify_risk(h_value),
                "Descriptions": selected_descriptions.copy(),
            })

            st.success(
                f"{pollutant_name.strip()} was added successfully. "
                f"Total score H = {h_value} "
                f"({classify_risk(h_value)})."
            )

# ==================================================
# RESULTS TABLE
# ==================================================
if st.session_state.pollutants:
    st.divider()
    st.header("3. Final Environmental Risk Assessment Table")

    all_records = st.session_state.pollutants
    df = pd.DataFrame(all_records)

    result_columns = [
        "Pollutant Emitted",
        "A", "B", "C", "D", "E", "F", "G", "H"
    ]

    result_table = df[result_columns].copy()

    st.caption(
        "Each row represents one pollutant. "
        "H = A × B × C × D × E × F × G."
    )

    st.dataframe(
        result_table,
        use_container_width=True,
        hide_index=True
    )

    # ==================================================
    # RISK OVERVIEW
    # ==================================================
    st.header("4. Risk Overview")

    total_pollutants = len(df)
    highest_score = int(df["H"].max())
    highest_level = classify_risk(highest_score)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Pollutants", total_pollutants)
    col2.metric("Highest Score (H)", highest_score)
    col3.metric("Highest Risk Level", highest_level)

    risk_order = [
        "Very Low", "Low", "Moderate", "High", "Extreme"
    ]

    risk_summary = pd.DataFrame({
        "Risk Level": risk_order,
        "Number of Pollutants": [
            int((df["Risk Level"] == level).sum())
            for level in risk_order
        ],
    })

    st.dataframe(
        risk_summary,
        use_container_width=True,
        hide_index=True
    )

    # ==================================================
    # RISK INTERPRETATION AND ACTIONS
    # ==================================================
    st.header("5. Risk Interpretation and Suggested Actions")

    for record in all_records:
        level = record["Risk Level"]
        h_value = int(record["H"])

        with st.expander(
            f"{record['Pollutant Emitted']} — "
            f"{level} Risk (H = {h_value})"
        ):
            st.markdown(
                f"""
                <div style="
                    background-color:{risk_color(level)};
                    color:#222;
                    padding:12px;
                    border-radius:8px;">
                    <strong>Risk level:</strong> {level}<br>
                    <strong>Total score:</strong> {h_value}
                </div>
                """,
                unsafe_allow_html=True
            )

            if level == "Extreme":
                st.error(
                    "Priority action: Investigate the source, "
                    "review potential environmental and health impacts, "
                    "and implement appropriate controls urgently."
                )
            elif level == "High":
                st.warning(
                    "Review pollution controls, identify corrective "
                    "measures, and strengthen monitoring."
                )
            elif level == "Moderate":
                st.info(
                    "Maintain suitable controls, review improvements, "
                    "and monitor the environmental impact."
                )
            elif level == "Low":
                st.success(
                    "Maintain existing controls and conduct routine monitoring."
                )
            else:
                st.success(
                    "Continue good environmental practices and periodically "
                    "review the assessment."
                )

            st.markdown("**Selected descriptions**")

            for letter, criterion in CRITERIA.items():
                st.write(
                    f"**{letter} — {criterion['title']}:** "
                    f"{record['Descriptions'][letter]} "
                    f"(numeric value: {record[letter]})"
                )

    # ==================================================
    # REMOVE A POLLUTANT
    # ==================================================
    st.header("6. Manage Pollutants")

    pollutant_choices = {
        f"{record['ID']} — {record['Pollutant Emitted']}": record["ID"]
        for record in all_records
    }

    selected_to_remove = st.selectbox(
        "Select a pollutant to remove",
        options=list(pollutant_choices.keys()),
        key="remove_pollutant_choice"
    )

    col_remove, col_clear = st.columns(2)

    with col_remove:
        if st.button("Remove Selected Pollutant", use_container_width=True):
            remove_id = pollutant_choices[selected_to_remove]

            st.session_state.pollutants = [
                record
                for record in st.session_state.pollutants
                if record["ID"] != remove_id
            ]
            st.rerun()

    with col_clear:
        if st.button("Clear All Pollutants", use_container_width=True):
            st.session_state.pollutants = []
            st.rerun()

    # ==================================================
    # DOWNLOAD CSV
    # ==================================================
    st.divider()
    st.header("7. Download Reports")

    csv_data = result_table.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "📊 Download Results as CSV",
        data=csv_data,
        file_name="environmental_risk_assessment.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ==================================================
    # PDF REPORT
    # ==================================================
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )

        pdf_buffer = BytesIO()

        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=landscape(A4),
            rightMargin=1.2 * cm,
            leftMargin=1.2 * cm,
            topMargin=1.2 * cm,
            bottomMargin=1.2 * cm,
        )

        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(
            "Environmental Risk Assessment Report",
            styles["Title"]
        ))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph(
            f"<b>Project:</b> {escape(project_name or 'Not provided')}",
            styles["Normal"]
        ))
        story.append(Paragraph(
            f"<b>Location:</b> {escape(project_location or 'Not provided')}",
            styles["Normal"]
        ))
        story.append(Paragraph(
            f"<b>Description:</b> "
            f"{escape(project_description or 'Not provided')}",
            styles["Normal"]
        ))
        story.append(Paragraph(
            f"<b>Generated:</b> "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph(
            "Final Risk Score Table",
            styles["Heading2"]
        ))

        pdf_data = [result_columns]

        for _, row in result_table.iterrows():
            pdf_data.append([
                str(row[column])
                for column in result_columns
            ])

        pdf_table = Table(
            pdf_data,
            repeatRows=1,
            colWidths=[
                4.3 * cm,
                1.1 * cm, 1.1 * cm, 1.1 * cm,
                1.1 * cm, 1.1 * cm, 1.1 * cm,
                1.1 * cm, 1.2 * cm,
            ],
        )

        pdf_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#205C3B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#EDF5ED")
            ]),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        story.append(pdf_table)
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph(
            "Risk Classification",
            styles["Heading2"]
        ))

        risk_data = [
            ["Risk Level", "Total Score (H)"],
            ["Very Low", "7–19"],
            ["Low", "20–39"],
            ["Moderate", "40–59"],
            ["High", "60–79"],
            ["Extreme", "80 and above"],
        ]

        risk_table = Table(
            risk_data,
            colWidths=[5 * cm, 5 * cm]
        )

        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#205C3B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))

        story.append(risk_table)

        doc.build(story)
        pdf_buffer.seek(0)

        st.download_button(
            "📄 Download Full PDF Report",
            data=pdf_buffer.getvalue(),
            file_name="environmental_risk_assessment_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    except ImportError:
        st.warning(
            "PDF export requires ReportLab. Add reportlab to "
            "requirements.txt to enable PDF downloads."
        )

else:
    st.info(
        "No pollutants added yet. Complete the form above and tap "
        "'Add Pollutant to Assessment'. Your final table and reports "
        "will appear after you add the first pollutant."
    )

# ==================================================
# FOOTER
# ==================================================
st.divider()

st.markdown("""
<div style="text-align:center; color:#47745a; padding:10px;">
    🌱 Environmental Risk Assessment Tool<br>
    <small>Verify the assessment results against applicable
    environmental requirements and project-specific guidance.</small>
</div>
""", unsafe_allow_html=True)
