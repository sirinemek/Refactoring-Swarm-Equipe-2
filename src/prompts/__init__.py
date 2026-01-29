"""
Prompts système pour les agents
"""
from .auditor_prompts import (
    AUDITOR_SYSTEM_PROMPT,
    get_auditor_analysis_prompt,
    get_auditor_reanalysis_prompt
)

from .fixer_prompts import (
    FIXER_SYSTEM_PROMPT,
    get_fixer_correction_prompt,
    get_fixer_iteration_prompt
)

from .tester_prompts import (
    TESTER_SYSTEM_PROMPT,
    get_tester_validation_prompt,
    get_tester_iteration_feedback
)

__all__ = [
    'AUDITOR_SYSTEM_PROMPT',
    'get_auditor_analysis_prompt',
    'get_auditor_reanalysis_prompt',
    'FIXER_SYSTEM_PROMPT',
    'get_fixer_correction_prompt',
    'get_fixer_iteration_prompt',
    'TESTER_SYSTEM_PROMPT',
    'get_tester_validation_prompt',
    'get_tester_iteration_feedback'
]
