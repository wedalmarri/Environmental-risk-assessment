
import io
from datetime import datetime
from html import escape

import pandas as pd
import streamlit as st

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------
st.set_page_config(
    page_title="Environmental Risk Assessment",
    page_icon="🌿",
    layout="wide",
)

# --------------------------------------------------
# GREEN DESIGN
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #f5faf5;
}
h1, h2, h3 {
    color: #176b45;
}
div.stButton > button,
div.stDownloadButton > button {
    background-color: #176b45;
    color: white;
    border-radius: 8px;
    border: none;
    min-height: 42px;
}
div.stButton > button:hover,
div.stDownloadButton > button:hover {
    background-color: #0f5132;
    color: white;
}
.result-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #d9e8dc;
}
</style>
""", unsafe_allow_html=True)

st.title("🌿 Environmental Risk Assessment")
st.write(
    "Evaluate potential environmental impacts, calculate risk scores, "
    "and generate automatic conclusions for project pollutants."
)

st.caption(
    "Screening tool: results depend on the selected criteria and "
    "the scoring methodology used."
)

# --------------------------------------------------
# CRITERIA AND DROPDOWN OPTIONS
# --------------------------------------------------
# Replace these generic names and score descriptions with the
# exact A-G criteria and scoring definitions from your methodology.

CRITERIA = {
    "A": "Criterion A",
    "B": "Criterion B",
    "C": "Criterion C",
    "D": "Criterion D",
    "E": "Criterion E",
    "F": "Criterion F",
    "G": "Criterion G",
}

SCORE_LABELS = {
    1: "1 — Very low",
    2: "2 — Low",
    3: "3 — Moderate",
    4: "4 — High",
    5: "5 — Very high",
}

SCORE_OPTIONS = list(SCORE_LABELS.keys())


# --------------------------------------------------
# RISK CALCULATION AND CONCLUSION
# --------------------------------------------------
def calculate_risk(scores):
    """Multiply the seven criterion scores."""
    result = 1
    for score in scores:
        result *= int(score)
    return result


def classify_risk(score):
    """Classify the calculated impact using the current thresholds."""
    if score < 25:
        return (
            "Low Impact",
            "The calculated environmental impact is low. "
            "Maintain existing environmental controls and continue "
            "routine monitoring.",
        )

    if score <= 200:
        return (
            "Medium Impact",
            "The calculated environmental impact is medium. "
            "Review existing controls, consider additional mitigation "
            "measures, and maintain appropriate monitoring.",
        )

    return (
        "High Impact",
        "The calculated environmental impact is high. "
        "Prioritize additional mitigation measures and arrange an "
        "appropriate environmental review before proceeding.",
    )


def make_assessment(pollutant, scores, stage):
    risk_score = calculate_risk(scores)
    classification, conclusion = classify_risk(risk_score)

    result = {
        "Pollutant": pollutant,
        "Assessment Stage": stage,
    }

    for factor in CRITERIA:
        result[factor] = scores[factor]

    result["Risk Score (H)"] = risk_score
    result["Impact Classification"] = classification
    result["Conclusion"] = conclusion

    return result


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "pollutants" not in st.session_state:
    st.session_state["pollutants"] = []

if "latest_result" not in st.session_state:
    st.session_state["latest_result"] = None


# --------------------------------------------------
# PROJECT INFORMATION
# Project Type and Assessor have been removed.
# --------------------------------------------------
st.header("1. Project Information")

project_name = st.text_input(
    "Project Name",
    placeholder="Enter your project name",
)

project_location = st.text_input(
    "Project Location",
    placeholder="Enter the project location",
)

project_description = st.text_area(
    "Project Description",
    placeholder="Briefly describe the project and its activities",
)

st.divider()

# --------------------------------------------------
# POLLUTANT ASSESSMENT
# --------------------------------------------------
st.header("2. Pollutant Assessment")

st.write(
    "Enter one pollutant at a time. Select a score for each criterion "
    "before and after mitigation. The application calculates both "
    "scores automatically."
)

with st.form("pollutant_assessment_form", clear_on_submit=True):

    pollutant_name = st.text_input(
        "Pollutant or Environmental Aspect",
        placeholder="e.g., NOx, wastewater, dust, or noise",
    )

    st.subheader("Before Mitigation")

    before = {}
    before_columns = st.columns(2)

    for index, (factor, label) in enumerate(CRITERIA.items()):
        with before_columns[index % 2]:
            before[factor] = st.selectbox(
                f"{factor}. {label}",
                options=SCORE_OPTIONS,
                format_func=lambda value: SCORE_LABELS.get(
                    value, str(value)
                ),
                key=f"before_{factor}",
            )

    st.subheader("After Mitigation")

    after = {}
    after_columns = st.columns(2)

    for index, (factor, label) in enumerate(CRITERIA.items()):
        with after_columns[index % 2]:
            after[factor] = st.selectbox(
                f"{factor}. {label}",
                options=SCORE_OPTIONS,
                format_func=lambda value: SCORE_LABELS.get(
                    value, str(value)
                ),
                key=f"after_{factor}",
            )

    submitted = st.form_submit_button(
        "Calculate Environmental Risk",
        use_container_width=True,
    )

    if submitted:
        if not pollutant_name.strip():
            st.error("Please enter a pollutant or environmental aspect.")

        else:
            before_result = make_assessment(
                pollutant_name.strip(),
                before,
                "Before Mitigation",
            )

            after_result = make_assessment(
                pollutant_name.strip(),
                after,
                "After Mitigation",
            )

            st.session_state["pollutants"].append({
                "Pollutant": pollutant_name.strip(),
                "Before Scores": before.copy(),
                "After Scores": after.copy(),
                "Before H": before_result["Risk Score (H)"],
                "Before Classification":
                    before_result["Impact Classification"],
                "Before Conclusion": before_result["Conclusion"],
                "After H": after_result["Risk Score (H)"],
                "After Classification":
                    after_result["Impact Classification"],
                "After Conclusion": after_result["Conclusion"],
            })

            st.session_state["latest_result"] = {
                "before": before_result,
                "after": after_result,
            }

            st.success(
                f"Assessment calculated for {pollutant_name.strip()}."
            )


# --------------------------------------------------
# AUTOMATIC RESULTS AND CONCLUSIONS
# --------------------------------------------------
latest = st.session_state["latest_result"]

if latest:
    st.divider()
    st.header("3. Assessment Results")

    before_result = latest["before"]
    after_result = latest["after"]

    result_columns = st.columns(2)

    for column, result, heading in [
        (result_columns[0], before_result, "Before Mitigation"),
        (result_columns[1], after_result, "After Mitigation"),
    ]:
        with column:
            st.subheader(heading)
            st.metric(
                "Calculated Risk Score (H)",
                result["Risk Score (H)"],
            )

            classification = result["Impact Classification"]

            if classification == "Low Impact":
                st.success(f"🌱 {classification}")
            elif classification == "Medium Impact":
                st.warning(f"⚠️ {classification}")
            else:
                st.error(f"🚨 {classification}")

            st.write("**Automatic Conclusion**")
            st.write(result["Conclusion"])

    before_score = before_result["Risk Score (H)"]
    after_score = after_result["Risk Score (H)"]

    if before_score > 0:
        reduction = (before_score - after_score) / before_score * 100

        if after_score < before_score:
            st.info(
                f"The calculated score decreased by {reduction:.1f}% "
                "after mitigation. Confirm that the selected scores "
                "accurately reflect the proposed controls."
            )
        elif after_score == before_score:
            st.info(
                "The calculated score did not change after mitigation. "
                "Review whether the proposed measures affect the "
                "selected criteria."
            )
        else:
            st.warning(
                "The calculated score increased after mitigation. "
                "Review the selected scores and proposed controls."
            )


# --------------------------------------------------
# FINAL SUMMARY TABLE
# --------------------------------------------------
st.divider()
st.header("4. Final Environmental Risk Summary")

records = st.session_state["pollutants"]

if records:

    summary_rows = []

    for item in records:
        row = {
            "Pollutant": item["Pollutant"],
        }

        for factor in CRITERIA:
            row[f"{factor} Before"] = item["Before Scores"][factor]

        row["H Before"] = item["Before H"]
        row["Impact Before"] = item["Before Classification"]

        for factor in CRITERIA:
            row[f"{factor} After"] = item["After Scores"][factor]

        row["H After"] = item["After H"]
        row["Impact After"] = item["After Classification"]
        row["Conclusion After"] = item["After Conclusion"]

        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Impact Overview")

    low_count = sum(
        1 for item in records
        if item["After Classification"] == "Low Impact"
    )

    medium_count = sum(
        1 for item in records
        if item["After Classification"] == "Medium Impact"
    )

    high_count = sum(
        1 for item in records
        if item["After Classification"] == "High Impact"
    )

    metric_columns = st.columns(3)
    metric_columns[0].metric("Low Impact", low_count)
    metric_columns[1].metric("Medium Impact", medium_count)
    metric_columns[2].metric("High Impact", high_count)

    st.subheader("Download Your Results")

    csv_data = summary_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "📥 Download CSV Summary",
        data=csv_data,
        file_name="environmental_risk_assessment.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # --------------------------------------------------
    # PDF REPORT
    # --------------------------------------------------
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )

        pdf_buffer = io.BytesIO()

        pdf_doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=landscape(A4),
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "GreenTitle",
            parent=styles["Title"],
            textColor=colors.HexColor("#176b45"),
            alignment=TA_CENTER,
            fontSize=18,
            leading=22,
        )

        body_style = styles["BodyText"]
        small_style = ParagraphStyle(
            "SmallText",
            parent=body_style,
            fontSize=7,
            leading=9,
        )

        story = [
            Paragraph(
                "Environmental Risk Assessment Report",
                title_style,
            ),
            Spacer(1, 8 * mm),
            Paragraph(
                f"<b>Project:</b> {escape(project_name or 'Not provided')}",
                body_style,
            ),
            Paragraph(
                f"<b>Location:</b> "
                f"{escape(project_location or 'Not provided')}",
                body_style,
            ),
            Paragraph(
                f"<b>Description:</b> "
                f"{escape(project_description or 'Not provided')}",
                body_style,
            ),
            Paragraph(
                f"<b>Report date:</b> {datetime.now().strftime('%Y-%m-%d')}",
                body_style,
            ),
            Spacer(1, 5 * mm),
            Paragraph(
                "<b>Calculation:</b> H = A × B × C × D × E × F × G",
                body_style,
            ),
            Paragraph(
                "Current classification thresholds: Low H &lt; 25; "
                "Medium 25 ≤ H ≤ 200; High H &gt; 200.",
                body_style,
            ),
            Spacer(1, 5 * mm),
        ]

        pdf_headers = (
            ["Pollutant", "Stage"]
            + list(CRITERIA.keys())
            + ["H", "Impact"]
        )

        pdf_data = [pdf_headers]

        for item in records:
            for stage, scores_key, score_key, class_key in [
                (
                    "Before",
                    "Before Scores",
                    "Before H",
                    "Before Classification",
                ),
                (
                    "After",
                    "After Scores",
                    "After H",
                    "After Classification",
                ),
            ]:
                pdf_data.append(
                    [
                        str(item["Pollutant"])[:35],
                        stage,
                    ]
                    + [
                        str(item[scores_key][factor])
                        for factor in CRITERIA
                    ]
                    + [
                        str(item[score_key]),
                        item[class_key],
                    ]
                )

        table = Table(
            pdf_data,
            repeatRows=1,
        )

        table.setStyle(TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#176b45"),
            ),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("LEADING", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#f0f7f1"),
            ]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        story.append(table)
        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph(
            "<b>Conclusions after mitigation</b>",
            body_style,
        ))

        for item in records:
            story.append(Paragraph(
                f"<b>{escape(item['Pollutant'])} — "
                f"{escape(item['After Classification'])}:</b> "
                f"{escape(item['After Conclusion'])}",
                small_style,
            ))
            story.append(Spacer(1, 2 * mm))

        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(
            "This report is an automated screening aid. Verify the "
            "scoring methodology and conclusions with a qualified "
            "environmental professional.",
            small_style,
        ))

        pdf_doc.build(story)
        pdf_data = pdf_buffer.getvalue()

        st.download_button(
            "📄 Download PDF Report",
            data=pdf_data,
            file_name="environmental_risk_assessment.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    except ImportError:
        st.warning(
            "PDF generation requires the reportlab package. "
            "The CSV download is available without it."
        )

    if st.button("Clear All Pollutants"):
        st.session_state["pollutants"] = []
        st.session_state["latest_result"] = None
        st.rerun()

else:
    st.info(
        "No pollutants have been assessed yet. Complete the dropdown "
        "menus above and click Calculate Environmental Risk."
    )

st.divider()

st.caption(
    "Environmental Risk Assessment | Automated screening results "
    "do not replace a formal environmental impact assessment."
)
