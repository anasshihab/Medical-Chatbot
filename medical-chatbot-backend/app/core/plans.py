"""Plan limits, word-count enforcement, and 6-hour window gating"""
import math
from datetime import datetime
from app.utils.constants import PlanType, PLAN_LIMITS, WORD_LIMITS
from app.utils.errors import PlanLimitReachedException, ValidationException
from app.core.usage import next_reset_time


def get_plan_limit(plan_type: PlanType) -> int:
    """Get question limit per 6-hour window for a plan type."""
    return PLAN_LIMITS.get(plan_type, PLAN_LIMITS[PlanType.FREE])


def get_word_limit(plan_type: PlanType) -> int:
    """Get word limit per message for a plan type."""
    return WORD_LIMITS.get(plan_type, WORD_LIMITS[PlanType.FREE])


def count_words(text: str) -> int:
    """
    Character-based word counter.
    1 word = exactly 5 characters (including spaces and punctuation).

    Algorithm:
      1. Strip leading/trailing whitespace so padding cannot skew the count.
      2. If the result is empty, return 0.
      3. Otherwise: math.ceil(char_count / 5.0)

    Examples:
      ""          ->  0  (empty)
      "hi"        ->  1  (ceil(2/5)  = 1)
      "hello"     ->  1  (ceil(5/5)  = 1)
      "hello!"    ->  2  (ceil(6/5)  = 2)
      12-char str ->  3  (ceil(12/5) = 3)
    """
    clean_text = text.strip() if text else ""
    char_count = len(clean_text)
    if char_count == 0:
        return 0
    return math.ceil(char_count / 5.0)


def check_word_limit(message: str, plan_type: PlanType) -> None:
    """
    Validate that the message does not exceed the word limit for the plan.
    Word count is calculated using the character-based formula: math.ceil(len(message) / 5).
    Raises ValidationException (HTTP 400) if exceeded.
    """
    word_count = count_words(message)
    limit = get_word_limit(plan_type)
    if word_count > limit:
        raise ValidationException(
            message=f"Message exceeds the {limit}-word limit for your plan ({word_count} words used).",
            details={
                "word_count": word_count,
                "word_limit": limit,
                "plan_type": plan_type.value,
            }
        )


def check_plan_limit(
    question_count: int,
    plan_type: PlanType,
    last_reset_at: datetime,
) -> None:
    """
    Check if the user/guest has exhausted their 6-hour question window.
    Raises PlanLimitReachedException (HTTP 403) with next_reset_time if so.
    """
    limit = get_plan_limit(plan_type)

    if question_count >= limit:
        reset_at = next_reset_time(last_reset_at)
        raise PlanLimitReachedException(
            limit=limit,
            plan_type=plan_type.value,
            details={
                "question_count": question_count,
                "next_reset_time": reset_at.isoformat(),
            }
        )


def can_ask_question(question_count: int, plan_type: PlanType) -> bool:
    """Return True if the user can still ask a question in the current window."""
    return question_count < get_plan_limit(plan_type)
