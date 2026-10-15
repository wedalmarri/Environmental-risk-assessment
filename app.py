
import io
from datetime import date

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from xml.sax.saxutils import escape


st.set_page_config(
    page_title="Environmental Risk Assessment",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.block-container {
    max-width: 1000px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}
h1 {font-size: 1.8rem !important;}
div[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,.25);
    padding: .8rem;
    border-radius: 12px;
}
.stButton button, .stDownloadButton button {
    width: 100%;
    min-height: 2.8rem;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 1. SCORING CRITERIA
# --------------------------------------------------

FACTORS = {
    "A": (
        "Quantity / Magnitude",
        {
            1: "Low",
            2: "Moderate",
            3: "High",
            4: "Very high",
            5: "Excessive",
        },
    ),
    "B": (
        "Occurrence / Frequency",
        {
            1: "Once a month or less",
            2: "Once a week",
            3: "Once a day",
            4: "Several times a day",
            5: "Continuous",
        },
    ),
    "C": (
        "Duration",
        {
            1: "Less than 1 year",
            2: "More than 1 year, less than project life",
            3: "Greater than project life",
            4: "Not applicable / validate",
            5: "Not applicable / validate",
        },
    ),
    "D": (
        "Scale / Severity",
        {
            1: "Localized / minor discomfort",
            2: "Localized impact or resource consumption",
            3: "Regional impact to flora, fauna or health",
            4: "Regional / serious human-health effect",
            5: "Global scale / potential fatality",
        },
    ),
    "E": (
        "Legislation / Compliance",
        {
            1: "In compliance",
            2: "Not meeting legislation",
        },
    ),
    "F": (
        "Controls and Detection",
        {
            1: "Available and effective",
            2: "Effective but improvements needed",
            3: "Ineffective controls",
            4: "Unreliable controls",
            5: "Absence of control",
        },
    ),
    "G": (
        "Preventive Mechanism",
        {
            1: "Immediately available",
            2: "Available within 2 hours",
            3: "Available within 24 hours",
            4: "Available within a week",
            5: "More than a week / unavailable",
        },
    ),
}

FACTOR_LETTERS = list(FACTORS.keys())


def calculate_impact(scores):
    """Calculate H by multiplying A, B, C, D, E, F and G."""
    result = 1

    for factor in FACTOR_LETTERS:
        result *= int(scores[factor])

    return result


def classify_impact(score):
    # Boundary convention: 25 and 200 are Medium.
    if score < 25:
        return "Low"
    elif score <= 200:
        return "Medium"
    return "High"


def make_summary(pollutants):
    """Create one results row per pollutant."""
    rows = []

    for item in pollutants:
        row = {"Pollutant": item["pollutant"]}

        # Scores before mitigation
        for factor in FACTOR_LETTERS:
            row[f"{factor} (Before)"] = item["before"][factor]

        row["H (Before)"] = calculate_impact(item["before"])
        row["Impact (Before)"] = classify_impact(row["H (Before)"])

        # Scores after mitigation
        for factor in FACTOR_LETTERS:
            row[f"{factor} (After)"] = item["after"][factor]

        row["H (After)"] = calculate_impact(item["after"])
        row["Impact (After)"] = classify_impact(row["H (After)"])

        row["Medium"] = item["medium"]
        row["Source"] = item["source"]

        rows.append(row)

    return pd.DataFrame(rows)


# --------------------------------------------------
# 2. PDF REPORT
# --------------------------------------------------

def build_pdf(project, organization, location, project_type,
              assessment_date, assessor, summary):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=16,
            textColor=colors.HexColor("#234b43"),
        )
    )

    story = [
        Paragraph("Environmental Risk Assessment Report",
                  styles["ReportTitle"]),
        Spacer(1, 8),
        Paragraph(
            "Preliminary screening only. Verify the scoring method "
            "and project-specific requirements before making decisions.",
            styles["BodyText"],
        ),
        Spacer(1, 12),
    ]

    details = [
        ["Project", project],
        ["Location", location or "—"],
        ["Assessment date", str(assessment_date)],
    ]

    detail_table = Table(
        details,
        colWidths=[85, 240, 85, 340],
    )
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("BACKGROUND", (2, 0), (2, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    story.extend([
        detail_table,
        Spacer(1, 12),
        Paragraph("Pollutant impact summary", styles["Heading2"]),
    ])

    # One line for before mitigation and one for after.
    data = [[
        "Pollutant", "Stage", "A", "B", "C", "D", "E", "F", "G",
        "H", "Impact"
    ]]

    for _, row in summary.iterrows():
        for stage in ("Before", "After"):
            factor_values = [
                str(row[f"{factor} ({stage})"])
                for factor in FACTOR_LETTERS
            ]

            data.append([
                str(row["Pollutant"])[:30],
                stage,
                *factor_values,
                str(row[f"H ({stage})"]),
                row[f"Impact ({stage})"],
            ])

    report_table = Table(
        data,
        repeatRows=1,
        colWidths=[105, 48] + [29] * 7 + [48, 58],
    )

    report_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#234b43")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.whitesmoke]),
    ]))

    story.extend([
        report_table,
        Spacer(1, 10),
        Paragraph(
            "Formula: H = A × B × C × D × E × F × G",
            styles["Heading3"],
        ),
        Paragraph(
            "Impact bands used: Low for H < 25; Medium for "
            "25 ≤ H ≤ 200; High for H > 200. The boundary convention "
            "for 25 and 200 should be confirmed against the approved "
            "reference methodology.",
            styles["BodyText"],
        ),
    ])

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------
# 3. APP HEADER AND PROJECT DETAILS
# --------------------------------------------------

if "pollutants" not in st.session_state:
    st.session_state["pollutants"] = []

st.title("🌿 Environmental Risk Assessment")
st.caption("General-purpose, mobile-friendly EIA screening tool")

st.info(
    "For preliminary screening only. Verify the scoring rubric, "
    "factor definitions and risk thresholds for your project."
)

with st.expander("Scoring formula and impact bands"):
    st.latex(r"H = A \times B \times C \times D \times E \times F \times G")

    st.markdown("""
    - **Low:** H < 25
    - **Medium:** 25 ≤ H ≤ 200
    - **High:** H > 200

    This implementation treats H = 25 and H = 200 as Medium to close
    the gaps in the supplied reference. Confirm that convention with
    your instructor or approved assessment procedure.
    """)

st.header("1. Project details")

col1, col2 = st.columns(2)

with col1:
    project = st.text_input(
        "Project name *",
        placeholder="Enter your project name",
    )
    organization = st.text_input("Organization / client")
    location = st.text_input("Project location")

with col2:
    project_type = st.selectbox(
        "Project type",
        [
            "Industrial / chemical",
            "Oil and gas",
            "Power / energy",
            "Construction / infrastructure",
            "Water / wastewater",
            "Mining / minerals",
            "Agriculture",
            "Transport / logistics",
            "Manufacturing",
            "Other",
        ],
    )
    assessment_date = st.date_input(
        "Assessment date",
        value=date.today(),
    )
    assessor = st.text_input("Assessor")


# --------------------------------------------------
# 4. ADD POLLUTANTS
# --------------------------------------------------

st.header("2. Add a pollutant")
st.caption(
    "Enter one pollutant at a time. Repeat this step to add more "
    "pollutants to the final summary."
)

with st.form("pollutant_form", clear_on_submit=True):

    pollutant_name = st.text_input(
        "Pollutant / environmental aspect *",
        placeholder="e.g., NH3, CO2, NOx, wastewater",
    )

    medium = st.selectbox(
        "Environmental medium / pathway",
        [
            "Air emissions",
            "Water / wastewater",
            "Soil / land",
            "Noise / vibration",
            "Waste generation",
            "Resource consumption",
            "Greenhouse gases",
            "Accidental release / spill",
            "Biodiversity / habitat",
            "Other",
        ],
    )

    source = st.text_input(
        "Source / activity",
        placeholder="e.g., process vent, pipeline, discharge",
    )

    receptors = st.text_area(
        "Potential receptors and impacts",
        placeholder="Workers, nearby community, aquatic organisms...",
    )

    scenario = st.text_area(
        "Scenario / evidence / assumptions",
        placeholder="Describe the release or environmental impact.",
    )

    st.subheader("Scores BEFORE mitigation")
    st.caption("Enter the seven factor ratings from 1 to 5.")

    before = {}

    for factor, (label, options) in FACTORS.items():
        before[factor] = st.selectbox(
            f"{factor}. {label}",
            options=[1, 2, 3, 4, 5],
            format_func=lambda value, opts=options:
                f"{value} — {opts[value]}",
            key=f"before_{factor}",
        )

    st.subheader("Scores AFTER mitigation")
    st.caption(
        "Enter the expected factor ratings after mitigation measures "
        "are implemented. Do not automatically assume every factor "
        "will decrease."
    )

    after = {}

    for factor, (label, options) in FACTORS.items():
        after[factor] = st.selectbox(
            f"{factor}. {label} — after mitigation",
            options=[1, 2, 3, 4, 5],
            format_func=lambda value, opts=options:
                f"{value} — {opts[value]}",
            key=f"after_{factor}",
        )

    add_pollutant = st.form_submit_button(
        "➕ Add pollutant to assessment",
        type="primary",
    )

if add_pollutant:
    if not project.strip():
        st.error("Please enter the project name first.")

    elif not pollutant_name.strip():
        st.error("Please enter a pollutant name.")

    else:
        st.session_state["pollutants"].append({
            "pollutant": pollutant_name.strip(),
            "medium": medium,
            "source": source.strip(),
            "receptors": receptors.strip(),
            "scenario": scenario.strip(),
            "before": {k: int(v) for k, v in before.items()},
            "after": {k: int(v) for k, v in after.items()},
        })

        st.success(
            f"{pollutant_name.strip()} added to the assessment."
        )


# --------------------------------------------------
# 5. FINAL POLLUTANT SUMMARY
# --------------------------------------------------

st.header("3. Final pollutant impact summary")

pollutants = st.session_state["pollutants"]

if pollutants:

    summary = make_summary(pollutants)

    st.caption(
        "Each row represents one pollutant. H is calculated by "
        "multiplying factors A–G separately before and after mitigation."
    )

    # Compact view with all pollutants and both H results.
    display_columns = [
        "Pollutant",
        "A (Before)", "B (Before)", "C (Before)",
        "D (Before)", "E (Before)", "F (Before)", "G (Before)",
        "H (Before)", "Impact (Before)",
        "A (After)", "B (After)", "C (After)",
        "D (After)", "E (After)", "F (After)", "G (After)",
        "H (After)", "Impact (After)",
    ]

    st.dataframe(
        summary[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Impact overview")

    before_counts = summary["Impact (Before)"].value_counts()
    after_counts = summary["Impact (After)"].value_counts()

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Pollutants assessed", len(summary))
    metric2.metric(
        "High before mitigation",
        int(before_counts.get("High", 0)),
    )
    metric3.metric(
        "High after mitigation",
        int(after_counts.get("High", 0)),
    )

    # Compare H before and after mitigation.
    chart_df = summary[
        ["Pollutant", "H (Before)", "H (After)"]
    ].set_index("Pollutant")

    st.bar_chart(chart_df)

    st.subheader("Pollutant details")

    selected_pollutant = st.selectbox(
        "Choose a pollutant to review",
        options=list(range(len(pollutants))),
        format_func=lambda index:
            pollutants[index]["pollutant"],
    )

    selected = pollutants[selected_pollutant]

    detail_rows = []

    for factor, (label, _) in FACTORS.items():
        detail_rows.append({
            "Factor": factor,
            "Criterion": label,
            "Before mitigation": selected["before"][factor],
            "After mitigation": selected["after"][factor],
        })

    st.dataframe(
        pd.DataFrame(detail_rows),
        use_container_width=True,
        hide_index=True,
    )

    selected_before = calculate_impact(selected["before"])
    selected_after = calculate_impact(selected["after"])

    left, right = st.columns(2)

    with left:
        st.metric(
            "H before mitigation",
            selected_before,
        )
        st.write(
            "Impact:",
            classify_impact(selected_before),
        )

    with right:
        st.metric(
            "H after mitigation",
            selected_after,
            delta=selected_after - selected_before,
            delta_color="inverse",
        )
        st.write(
            "Impact:",
            classify_impact(selected_after),
        )

    if selected_after > selected_before:
        st.warning(
            "The calculated score increased after mitigation. "
            "Review the factor ratings and mitigation assumptions."
        )

    elif selected_after == selected_before:
        st.info(
            "The calculated score did not change. Check whether "
            "the mitigation measures affect any of the seven factors."
        )

    else:
        st.success(
            "The calculated score decreased after mitigation. "
            "Verify the revised ratings and supporting evidence."
        )

    st.subheader("Assessment notes")

    for item in pollutants:
        with st.expander(
            f"Notes: {item['pollutant']}"
        ):
            st.write("**Source / activity:**", item["source"] or "Not specified")
            st.write("**Medium:**", item["medium"])
            st.write(
                "**Potential receptors and impacts:**",
                item["receptors"] or "Not specified",
            )
            st.write(
                "**Scenario / evidence:**",
                item["scenario"] or "Not specified",
            )

    st.subheader("Download results")

    csv_data = summary.to_csv(index=False).encode("utf-8-sig")

    pdf_data = build_pdf(
        project,
        organization,
        location,
        project_type,
        assessment_date,
        assessor,
        summary,
    )

    download1, download2 = st.columns(2)

    with download1:
        st.download_button(
            "📄 Download PDF report",
            data=pdf_data,
            file_name="environmental_risk_assessment.pdf",
            mime="application/pdf",
        )

    with download2:
        st.download_button(
            "📊 Download full results (CSV)",
            data=csv_data,
            file_name="environmental_risk_assessment.csv",
            mime="text/csv",
        )

    if st.button("🗑️ Clear all pollutants"):
        st.session_state["pollutants"] = []
        st.rerun()

else:
    st.info(
        "No pollutants added yet. Complete the form above and tap "
        "'Add pollutant to assessment' to start your summary table."
    )


st.divider()

st.caption(
    "Environmental Risk Assessment | Preliminary screening tool. "
    "Results depend on the accuracy of the inputs and the approved "
    "assessment methodology. High-consequence hazards may require "
    "specialist assessment regardless of the screening score."
)
