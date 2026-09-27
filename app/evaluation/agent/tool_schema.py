from typing import Any
from pydantic import BaseModel,Field

class ToolEvalSchema(BaseModel):
    id:str
    question:str
    expected_tools:list[str]
    should_call_tool:bool
    expected_arguments:dict[str,dict[str,Any]]=Field(default_factory=dict)


class ToolEvalResult(BaseModel):
    case_id:str
    question:str
    expected_tools:list[str]
    actual_tools:list[str]
    should_call_tool:bool
    tool_was_called:bool
    tool_selection_correct:bool
    tool_sequence_correct:bool
    unexpected_tool_call:bool
    arguments_correct:bool
    final_answer:str
    passed:bool
    latency_seconds:float
    error:str|None = None