import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Environmental Risk Assessment",
    page_icon="🌿",
    layout="wide",
)

# Green visual theme
st.markdown(
    """
    <style>
      .stApp { background: #f5faf6; }
      [data-testid="stHeader"] { background: rgba(245,250,246,0.95); }
      h1, h2, h3 { color: #176b45; }
      div.stButton > button, div.stDownloadButton > button {
        background: #19734a; color: white; border: 0; border-radius: 9px;
        padding: 0.55rem 1rem;
      }
      div.stButton > button:hover, div.stDownloadButton > button:hover {
        background: #125a39; color: white;
      }
      [data-testid="stMetric"] {
        background: white; border: 1px solid #dcebe0; padding: 14px;
        border-radius: 12px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌿 Environmental Risk Assessment")
st.caption("Assess each pollutant separately and compare the results for your project.")

CRITERIA = [
    (
        "A. Quantity / Magnitude",
        [
            "1 - Low",
            "2 - Moderate",
            "3 - High",
            "4 - Very high",
            "5 - Excessive",
        ],
    ),
    (
        "B. Occurrence / Frequency",
        [
            "1 - Once a month or less frequent",
            "2 - Once a week",
            "3 - Once a day",
            "4 - Several times a day",
            "5 - Continuous",
        ],
    ),
    (
        "C. Duration",
        [
            "1 - Less than 1 year",
            "2 - More than 1 year, less than project life",
            "3 - Greater than project life",
            "4 - Not applicable / validate",
            "5 - Not applicable / validate",
        ],
    ),
    (
        "D. Scale / Severity",
        [
            "1 - Localized / minor discomfort",
            "2 - Localized impact or resource consumption",
            "3 - Regional impact to flora/fauna or human health",
            "4 - Regional / serious human-health effect",
            "5 - Global scale / potential fatality",
        ],
    ),
    (
        "E. Legislation / Compliance",
        [
            "1 - In compliance",
            "2 - Minor uncertainty / review needed",
            "3 - Partial non-compliance",
            "4 - Significant non-compliance",
            "5 - Not meeting legislation",
        ],
    ),
    (
        "F. Controls and Detection",
        [
            "1 - Available and effective",
            "2 - Effective but improvements needed",
            "3 - Ineffective controls",
            "4 - Unreliable controls",
            "5 - Absence of control",
        ],
    ),
    (
        "G. Preventive Mechanism",
        [
            "1 - Immediately available",
            "2 - Available within 2 hours",
            "3 - Available within 24 hours",
            "4 - Available within a week",
            "5 - More than a week / unavailable",
        ],
    ),
]

with st.sidebar:
    st.header("Project information")
    project_name = st.text_input("Project name", placeholder="Enter project name")
    project_location = st.text_input("Project location", placeholder="City, country or site")
    project_stage = st.selectbox(
        "Project stage",
        ["Planning / design", "Construction", "Operation", "Decommissioning", "Other"],
    )
    assessor = st.text_input("Assessor", placeholder="Name or organization (optional)")

st.subheader("Pollutants to assess")
st.write("Add each pollutant or environmental aspect separately. Select one score for every criterion.")

if "pollutant_count" not in st.session_state:
    st.session_state.pollutant_count = 1

col_add, col_remove, _ = st.columns([1, 1, 4])
with col_add:
    if st.button("＋ Add pollutant"):
        st.session_state.pollutant_count += 1
with col_remove:
    if st.button("− Remove last") and st.session_state.pollutant_count > 1:
        st.session_state.pollutant_count -= 1

pollutant_results = []

for pollutant_index in range(st.session_state.pollutant_count):
    with st.container(border=True):
        st.markdown(f"### Pollutant {pollutant_index + 1}")
        pollutant_name = st.text_input(
            "Pollutant / environmental aspect",
            key=f"pollutant_name_{pollutant_index}",
            placeholder="e.g., ammonia, NOx, wastewater, noise",
        )
        description = st.text_area(
            "Source or brief description (optional)",
            key=f"pollutant_description_{pollutant_index}",
            placeholder="Describe the source, activity, or potential environmental pathway",
            height=70,
        )

        selected_scores = []
        left, right = st.columns(2)
        for criterion_index, (criterion_name, options) in enumerate(CRITERIA):
            target_column = left if criterion_index % 2 == 0 else right
            with target_column:
                chosen_option = st.selectbox(
                    criterion_name,
                    options,
                    index=0,
                    key=f"score_{pollutant_index}_{criterion_index}",
                )
                selected_scores.append(int(chosen_option.split(" - ", 1)[0]))

        total_score = sum(selected_scores)
        pollutant_results.append(
            {
                "Pollutant": pollutant_name.strip() or f"Pollutant {pollutant_index + 1}",
                "Description": description,
                **{CRITERIA[i][0]: selected_scores[i] for i in range(len(CRITERIA))},
                "Total score": total_score,
                "Maximum possible": 35,
            }
        )

st.divider()
st.subheader("Assessment results")
results_df = pd.DataFrame(pollutant_results)

if not results_df.empty:
    highest_row = results_df.loc[results_df["Total score"].idxmax()]
    total_pollutants = len(results_df)
    highest_score = int(highest_row["Total score"])
    highest_name = str(highest_row["Pollutant"])

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Pollutants assessed", total_pollutants)
    metric2.metric("Highest individual score", f"{highest_score} / 35")
    metric3.metric("Highest-scoring pollutant", highest_name)

    st.info(
        f"Project summary: **{highest_name}** has the highest individual score "
        f"({highest_score} out of 35). This summary uses the highest pollutant score, "
        "not the sum of all pollutant scores."
    )

    chart_df = results_df[["Pollutant", "Total score"]].set_index("Pollutant")
    st.markdown("#### Score comparison")
    st.bar_chart(chart_df, color="#238653")

    st.markdown("#### Detailed results")
    display_columns = ["Pollutant"] + [item[0] for item in CRITERIA] + ["Total score", "Maximum possible"]
    st.dataframe(results_df[display_columns], use_container_width=True, hide_index=True)

    st.caption(
        "The total is the sum of the seven selected criterion scores (minimum 7, maximum 35). "
        "This is a screening aid; confirm scoring definitions, weighting, thresholds, and legal requirements "
        "with the applicable EIA/risk-assessment method and a qualified environmental professional."
    )

    csv_bytes = results_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Download results as CSV",
        data=csv_bytes,
        file_name="environmental_risk_assessment.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # Generate a PDF when ReportLab is installed; otherwise provide a helpful message.
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

        pdf_buffer = io.BytesIO()
        document = SimpleDocTemplate(
            pdf_buffer, pagesize=landscape(A4), rightMargin=24, leftMargin=24,
            topMargin=24, bottomMargin=24
        )
        styles = getSampleStyleSheet()
        story = [Paragraph("Environmental Risk Assessment", styles["Title"]), Spacer(1, 10)]
        meta = [
            ["Project", project_name or "Not provided", "Location", project_location or "Not provided"],
            ["Stage", project_stage, "Assessor", assessor or "Not provided"],
            ["Highest-scoring pollutant", highest_name, "Highest score", f"{highest_score}/35"],
        ]
        meta_table = Table(meta, colWidths=[115, 210, 115, 210])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e3f2e8")),
            ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#e3f2e8")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b9d7c3")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        story.extend([meta_table, Spacer(1, 14)])

        pdf_headers = ["Pollutant"] + [f"{chr(65+i)}" for i in range(7)] + ["Total / 35"]
        pdf_data = [pdf_headers]
        for _, row in results_df.iterrows():
            pdf_data.append(
                [str(row["Pollutant"])]
                + [str(int(row[criterion[0]])) for criterion in CRITERIA]
                + [str(int(row["Total score"]))]
            )
        table = Table(pdf_data, repeatRows=1, colWidths=[210] + [55] * 7 + [70])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#19734a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b9d7c3")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f8f3")]),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.extend([Paragraph("Criterion key: A Quantity; B Frequency; C Duration; D Scale/Severity; E Compliance; F Controls; G Prevention.", styles["BodyText"]), Spacer(1, 8), table])
        document.build(story)
        st.download_button(
            "Download report as PDF",
            data=pdf_buffer.getvalue(),
            file_name="environmental_risk_assessment.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except ImportError:
        st.st.warning("PDF export requires ReportLab. Install it with: pip install reportlab")
