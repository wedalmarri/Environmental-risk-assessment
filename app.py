
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Environmental Risk Assessment",
    page_icon="🌿",
    layout="wide"
)

# --------------------------------------------------
# GREEN DESIGN
# --------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #f4f8f3;
    }

    h1, h2, h3 {
        color: #1c603c;
    }

    .main-title {
        background: linear-gradient(100deg, #14532d, #3b8c5a);
        color: white;
        padding: 24px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 18px;
    }

    .main-title h1 {
        color: white;
        margin-bottom: 8px;
    }

    .main-title p {
        color: white;
        margin-bottom: 0;
    }

    div[data-testid="stMetric"] {
        background-color: white;
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

    div[data-testid="stForm"] {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #d5e6d7;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# EXACT CRITERIA FROM YOUR REFERENCE TABLE
# Each option contains its description and numeric score.
# --------------------------------------------------
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
        "title": "Legislation",
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

# --------------------------------------------------
# RISK CLASSIFICATION
# The reference guide gives 80-100 as Extreme.
# The example contains scores above 100, so scores
# above 100 are also classified as Extreme.
# --------------------------------------------------
def classify_risk(score):
    if score >= 80:
        return "Extreme"
    elif score >= 60:
        return "High"
    elif score >= 40:
        return "Moderate"
    elif score >= 20:
        return "Low"
    else:
        return "Very Low"


def risk_color(level):
    colors = {
        "Very Low": "#d9ead3",
        "Low": "#93c47d",
        "Moderate": "#ffd966",
        "High": "#f6b26b",
        "Extreme": "#e06666",
    }
    return colors.get(level, "#ffffff")


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div class="main-title">
    <h1>🌿 Environmental Risk Assessment</h1>
    <p>Assess environmental pollutants, calculate risk scores,
    and generate a project risk report.</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Enter your project details, assess each pollutant using "
    "criteria A–G, and review the calculated risk score H."
)

# --------------------------------------------------
# PROJECT DETAILS
# --------------------------------------------------
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

# --------------------------------------------------
# POLLUTANT INPUT
# --------------------------------------------------
st.header("2. Pollutant Assessment")

if "pollutants" not in st.session_state:
    st.session_state.pollutants = []

with st.form("pollutant_form", clear_on_submit=False):
    pollutant_name = st.text_input(
        "Pollutant Emitted",
        placeholder="e.g., NO, NO₂, CO₂, wastewater"
    )

    st.caption(
        "Select one option for each criterion. "
        "The score assigned to each option is used automatically."
    )

    selected_scores = {}
    selected_descriptions = {}

    for letter, criterion in CRITERIA.items():
        st.subheader(f"{letter} — {criterion['title']}")

        option_labels = [
            f"{description} — Score {score}"
            for description, score in criterion["options"]
        ]

        selected_label = st.selectbox(
            f"Select {letter}",
            options=option_labels,
            key=f"selection_{letter}"
        )

        selected_index = option_labels.index(selected_label)

        description, score = criterion["options"][selected_index]

        selected_scores[letter] = score
        selected_descriptions[letter] = description

    submitted = st.form_submit_button(
        "➕ Add Pollutant to Assessment",
        use_container_width=True
    )

    if submitted:
        if not pollutant_name.strip():
            st.error("Please enter the pollutant name.")
        else:
            score_h = 1
            for letter in CRITERIA:
                score_h *= selected_scores[letter]

            new_record = {
                "Pollutant Emitted": pollutant_name.strip(),
                "A": selected_scores["A"],
                "B": selected_scores["B"],
                "C": selected_scores["C"],
                "D": selected_scores["D"],
                "E": selected_scores["E"],
                "F": selected_scores["F"],
                "G": selected_scores["G"],
                "H": score_h,
                "Risk Level": classify_risk(score_h),
                "Descriptions": selected_descriptions.copy(),
            }

            st.session_state.pollutants.append(new_record)
            st.success(
                f"{pollutant_name.strip()} added successfully. "
                f"Total risk score H = {score_h} "
                f"({classify_risk(score_h)})."
            )

# --------------------------------------------------
# REMOVE ALL RESULTS
# --------------------------------------------------
if st.session_state.pollutants:
    if st.button("🗑️ Clear All Pollutants"):
        st.session_state.pollutants = []
        st.rerun()

# --------------------------------------------------
# RESULTS
# --------------------------------------------------
if st.session_state.pollutants:
    st.divider()
    st.header("3. Environmental Risk Assessment Results")

    df = pd.DataFrame(st.session_state.pollutants)

    # Main table follows the user's reference:
    # Pollutant Emitted | A | B | C | D | E | F | G | H
    result_columns = [
        "Pollutant Emitted",
        "A", "B", "C", "D", "E", "F", "G", "H"
    ]

    result_table = df[result_columns].copy()

    st.markdown("#### Final Risk Score Table")
    st.dataframe(
        result_table,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "H = A × B × C × D × E × F × G. "
        "Each letter represents the numeric score selected above."
    )

    # --------------------------------------------------
    # RISK SUMMARY
    # --------------------------------------------------
    st.header("4. Risk Overview")

    total_pollutants = len(df)
    extreme_count = (df["Risk Level"] == "Extreme").sum()
    high_count = (df["Risk Level"] == "High").sum()
    moderate_count = (df["Risk Level"] == "Moderate").sum()
    low_count = (df["Risk Level"] == "Low").sum()
    very_low_count = (df["Risk Level"] == "Very Low").sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Pollutants", total_pollutants)
    col2.metric("Highest Risk Score", int(df["H"].max()))
    col3.metric(
        "Highest Risk Level",
        classify_risk(int(df["H"].max()))
    )

    risk_summary = pd.DataFrame({
        "Risk Level": [
            "Very Low",
            "Low",
            "Moderate",
            "High",
            "Extreme",
        ],
        "Number of Pollutants": [
            very_low_count,
            low_count,
            moderate_count,
            high_count,
            extreme_count,
        ],
    })

    st.dataframe(
        risk_summary,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # RISK DETAILS AND SUGGESTED ACTIONS
    # --------------------------------------------------
    st.header("5. Risk Interpretation and Suggested Actions")

    for _, record in df.iterrows():
        level = record["Risk Level"]
        score = int(record["H"])

        with st.expander(
            f"{record['Pollutant Emitted']} — "
            f"{level} Risk (H = {score})",
            expanded=(level in ["High", "Extreme"])
        ):
            st.markdown(
                f"""
                <div style="
                    background-color:{risk_color(level)};
                    padding:12px;
                    border-radius:8px;
                    color:#1f2937;">
                    <strong>Risk level:</strong> {level}<br>
                    <strong>Total score:</strong> {score}
                </div>
                """,
                unsafe_allow_html=True
            )

            if level == "Extreme":
                st.error(
                    "Priority action: Investigate the source, "
                    "evaluate environmental and human-health risks, "
                    "and implement appropriate control measures urgently."
                )
            elif level == "High":
                st.warning(
                    "Action recommended: Review pollution controls, "
                    "identify corrective measures, and monitor performance."
                )
            elif level == "Moderate":
                st.info(
                    "Action recommended: Maintain suitable controls, "
                    "review mitigation opportunities, and monitor the impact."
                )
            elif level == "Low":
                st.success(
                    "Action recommended: Maintain existing controls "
                    "and conduct routine monitoring."
                )
            else:
                st.success(
                    "Action recommended: Continue good environmental "
                    "practices and periodically review the assessment."
                )

            st.markdown("**Selected criterion descriptions**")

            for letter, criterion in CRITERIA.items():
                description = record["Descriptions"][letter]
                score_value = record[letter]

                st.write(
                    f"**{letter} — {criterion['title']}:** "
                    f"{description} (Score {score_value})"
                )

    # --------------------------------------------------
    # CSV DOWNLOAD
    # --------------------------------------------------
    st.divider()
    st.header("6. Download Your Report")

    csv_buffer = result_table.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="📊 Download Results as CSV",
        data=csv_buffer,
        file_name="environmental_risk_assessment.csv",
        mime="text/csv",
        use_container_width=True
    )

    # --------------------------------------------------
    # PDF DOWNLOAD
    # --------------------------------------------------
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
            rightMargin=1.3 * cm,
            leftMargin=1.3 * cm,
            topMargin=1.3 * cm,
            bottomMargin=1.3 * cm,
        )

        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(
            "Environmental Risk Assessment Report",
            styles["Title"]
        ))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph(
            f"<b>Project:</b> {project_name or 'Not provided'}",
            styles["Normal"]
        ))
        story.append(Paragraph(
            f"<b>Location:</b> {project_location or 'Not provided'}",
            styles["Normal"]
        ))
        story.append(Paragraph(
            f"<b>Description:</b> "
            f"{project_description or 'Not provided'}",
            styles["Normal"]
        ))
        story.append(Paragraph(
            f"<b>Report generated:</b> "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 0.5 * cm))

        story.append(Paragraph(
            "Final Risk Score Table",
            styles["Heading2"]
        ))

        pdf_data = [result_columns]

        for _, row in result_table.iterrows():
            pdf_data.append([
                str(row[column]) for column in result_columns
            ])

        pdf_table = Table(
            pdf_data,
            repeatRows=1,
            colWidths=[
                4.0 * cm,
                1.0 * cm, 1.0 * cm, 1.0 * cm,
                1.0 * cm, 1.0 * cm, 1.0 * cm,
                1.0 * cm, 1.2 * cm,
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
        story.append(Spacer(1, 0.5 * cm))

        story.append(Paragraph(
            "Risk Classification",
            styles["Heading2"]
        ))

        risk_data = [
            ["Risk Level", "Total Score (H)"],
            ["Very Low", "Below 20"],
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
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#EDF5ED")
            ]),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))

        story.append(risk_table)

        doc.build(story)
        pdf_buffer.seek(0)

        st.download_button(
            label="📄 Download Full PDF Report",
            data=pdf_buffer.getvalue(),
            file_name="environmental_risk_assessment_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    except ImportError:
        st.warning(
            "PDF export requires ReportLab. "
            "Add reportlab to your requirements.txt file "
            "to enable PDF downloads."
        )

else:
    st.info(
        "No pollutants have been added yet. "
        "Complete the form above and select "
        "'Add Pollutant to Assessment' to begin."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.markdown("""
<div style="text-align:center; color:#47745a; padding:10px;">
    🌱 Environmental Risk Assessment Tool<br>
    <small>Use project-specific data and verify results against
    applicable environmental regulations and assessment guidance.</small>
</div>
""", unsafe_allow_html=True)
