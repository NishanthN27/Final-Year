import json

from jinja2 import Environment, FileSystemLoader

from interview_system.orchestration.state import SessionState
from interview_system.schemas.agent_outputs import ReportGenOutput
from interview_system.services.llm_clients import get_llm


def generate_report(session_state: SessionState) -> ReportGenOutput:
    """
    Generates a final HTML report for the interview session.

    Args:
        session_state: The complete final state of the interview.

    Returns:
        A Pydantic object containing the HTML report and summary data.
    """
    env = Environment(loader=FileSystemLoader("src/interview_system/prompts/"))
    template = env.get_template("report_generator.j2")

    prompt = template.render(session_history=session_state["question_history"])

    llm = get_llm(
        model_type="pro"
    )  # Use Pro for a comprehensive and well-formatted report
    response = llm.invoke(prompt)

    try:
        start_index = response.content.find("{")
        end_index = response.content.rfind("}") + 1
        json_str = response.content[start_index:end_index]
        response_data = json.loads(json_str)
        return ReportGenOutput(**response_data)
    except (json.JSONDecodeError, KeyError) as exc:
        raise ValueError(
            f"ReportGenAgent returned malformed JSON: {response.content}"
        ) from exc
