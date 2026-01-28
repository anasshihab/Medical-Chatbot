"""Plan limits and enforcement"""
from app.utils.constants import PlanType, PLAN_LIMITS
from app.utils.errors import PlanLimitReachedException


def get_plan_limit(plan_type: PlanType) -> int:
    """Get question limit for a plan type"""
    return PLAN_LIMITS.get(plan_type, PLAN_LIMITS[PlanType.FREE])


def check_plan_limit(questions_used: int, plan_type: PlanType) -> None:
    """Check if user has exceeded plan limit"""
    limit = get_plan_limit(plan_type)
    
    if questions_used >= limit:
        raise PlanLimitReachedException(
            limit=limit,
            details={
                "questions_used": questions_used,
                "plan_type": plan_type.value
            }
        )


def can_ask_question(questions_used: int, plan_type: PlanType) -> bool:
    """Check if user can ask another question"""
    limit = get_plan_limit(plan_type)
    return questions_used < limit
