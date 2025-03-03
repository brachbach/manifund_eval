import streamlit as st
import json 
from dataclasses import dataclass
from utils import clean_xml_string, extract_xml_tag, extract_xml_tags, extract_all_xml_tags_properties

@dataclass
class PossibleImpact:
    impact_statement: str
    pathway_to_impact: str
    barriers_to_impact: str
    likelihood_assessment: str

@dataclass
class ScreeningResult:
    summary: str
    possible_impacts: list[PossibleImpact]
    promise_description: str

def make_screening_result(model_output: str) -> ScreeningResult:
    return ScreeningResult(
        summary=extract_xml_tag(model_output, "what_proposed"),
        possible_impacts=[PossibleImpact(**impact) for impact in extract_all_xml_tags_properties(model_output, "possible_impact", ["impact_statement", "pathway_to_impact", "barriers_to_impact", "likelihood_assessment"])],
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

# Initialize current index in session state if not already present
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

current_result_index = st.session_state.current_index

# Display the current result
if results:
    current_result = results[current_result_index]
    screening_result = make_screening_result(current_result.model_output)
    st.subheader(f"Project {current_result_index + 1} of {len(results)}")
    
    with st.expander("Project Details", expanded=True):
        st.write(f"**Screening score:** {current_result.numeric_score()}")
        st.write(f"**Project title:** {current_result.project_title}")
        st.write(f"**Project link:** "
                 f"https://manifund.org/projects/{current_result.slug}")
        st.write(f"## Summary")
        st.write(screening_result.summary)
        st.write(f"## Possible impacts:")
        for idx, impact in enumerate(screening_result.possible_impacts):
            st.write(f"### Impact {idx + 1}:")
            st.write(impact.impact_statement)
            st.write(f"#### Pathway to impact:")
            st.write(impact.pathway_to_impact)
            st.write(f"#### Barriers to impact:")
            st.write(impact.barriers_to_impact)
            st.write(f"#### Likelihood assessment:")
            st.write(impact.likelihood_assessment)
        st.write(f"## Promise description:")
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

