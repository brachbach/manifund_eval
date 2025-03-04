import streamlit as st
import json
from dataclasses import dataclass
from typing import Optional
from utils import extract_xml_tag, extract_all_xml_tags_properties

@dataclass
class PossibleImpact:
    impact_statement: Optional[str] = None
    pathway_to_impact: Optional[str] = None
    barriers_to_impact: Optional[str] = None
    likelihood_assessment: Optional[str] = None

@dataclass
class ScreeningResult:
    summary: Optional[str] = None
    possible_impacts: list[PossibleImpact] = None
    promise_description: Optional[str] = None

def make_screening_result(model_output: str) -> ScreeningResult:
    impacts = extract_all_xml_tags_properties(
        model_output, 
        "possible_impact", 
        ["impact_statement", "pathway_to_impact", 
         "barriers_to_impact", "likelihood_assessment"]
    )
    
    return ScreeningResult(
        summary=extract_xml_tag(model_output, "what_proposed"),
        possible_impacts=[PossibleImpact(**impact) for impact in impacts],
        promise_description=extract_xml_tag(model_output, "promise_description"),
    )


@dataclass
class Result:
    project_id: str
    project_title: str
    score: float
    model_output: str
    slug: str

    def numeric_score(self):
        try:
            # Convert float to string before using strip()
            return int(str(self.score).strip())
        except ValueError:
            return -float('inf')
        



st.title("Review Manifund grant screening results")

with open("screening_results_clean.json", "r") as f:
    results_json = json.load(f)

results = [Result(**result_json) for result_json in results_json]

results = sorted(results, key=lambda x: x.numeric_score(), reverse=True)

# Display a table with all projects
st.subheader("All Projects")
projects_data = {
    "Score": [result.numeric_score() for result in results],
    "Project Title": [result.project_title for result in results],
    "Project Link": [
        f"<a href='https://manifund.org/projects/{result.slug}' target='_blank'>"
        f"View on Manifund</a>" for result in results
    ]
}
projects_df = st.dataframe(
    projects_data, 
    use_container_width=True, 
    hide_index=True, 
    column_config={
        "Project Link": st.column_config.Column(
            "Project Link",
            width="medium",
            help="Click to view on Manifund"
        )
    }
)

# Add selection functionality
selected_project = st.selectbox(
    "Select a project to view details:",
    options=range(len(results)),
    format_func=lambda i: f"{results[i].numeric_score()} - {results[i].project_title}",
    index=0
)

# Initialize current index in session state if not already present
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# Update current index when a project is selected
st.session_state.current_index = selected_project

current_result_index = st.session_state.current_index

# Display the current result
if results:
    current_result = results[current_result_index]
    screening_result = make_screening_result(current_result.model_output)
    st.subheader(f"Project {current_result_index + 1} of {len(results)}")
    
    with st.expander("Project Details", expanded=True):
        st.write(f"**Screening score:** {current_result.numeric_score()}")
        st.write(f"**Project title:** {current_result.project_title}")
        manifund_link = f"https://manifund.org/projects/{current_result.slug}"
        st.write(
            f"**Project link:** {manifund_link}"
        )
        st.write("## Summary")
        st.write(screening_result.summary)
        st.write("## Possible impacts:")
        for idx, impact in enumerate(screening_result.possible_impacts):
            st.write(f"### Impact {idx + 1}:")
            st.write(impact.impact_statement)
            st.write("#### Pathway to impact:")
            st.write(impact.pathway_to_impact)
            st.write("#### Barriers to impact:")
            st.write(impact.barriers_to_impact)
            st.write("#### Likelihood assessment:")
            st.write(impact.likelihood_assessment)
        st.write("## Promise description:")
        st.write(screening_result.promise_description)


    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_result_index > 0:
            if st.button("Previous"):
                st.session_state.current_index -= 1
                st.rerun()
    
    with col3:
        if current_result_index < len(results) - 1:
            if st.button("Next"):
                st.session_state.current_index += 1
                st.rerun()
else:
    st.warning("No results found. Please run the screening process first.")

