"""Application constants and enums"""
from enum import Enum


class ErrorCode(str, Enum):
    """Error codes for unified error responses"""
    PLAN_LIMIT_REACHED = "PLAN_LIMIT_REACHED"
    UNAUTHORIZED = "UNAUTHORIZED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    OPENAI_ERROR = "OPENAI_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"


class PlanType(str, Enum):
    """User plan types"""
    FREE = "free"
    PRO = "pro"


class FeedbackType(str, Enum):
    """Feedback types"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"


# Plan limits configuration
PLAN_LIMITS = {
    PlanType.FREE: 100,
    PlanType.PRO: 999999  # Essentially unlimited for MVP
}

# Emergency keywords that trigger immediate emergency response
EMERGENCY_KEYWORDS = [
    # Cardiac
    "chest pain", "heart attack", "cardiac arrest",
    # Breathing
    "can't breathe", "cannot breathe", "shortness of breath", "difficulty breathing",
    # Bleeding
    "severe bleeding", "profuse bleeding", "hemorrhage",
    # Consciousness
    "unconscious", "passed out", "unresponsive",
    # Mental health emergencies
    "suicide", "self-harm", "kill myself",
    # Stroke
    "stroke", "facial drooping", "can't move arm",
    # Severe pain
    "severe abdominal pain", "worst headache",
    # Allergic reaction
    "anaphylaxis", "throat swelling",
]

# Approved medical domains for keyword search
# مصادر طبية موثوقة فقط - Trusted medical sources only
# WebTeb is prioritized as the PRIMARY source
APPROVED_DOMAINS = [
    "webteb.com",           # WebTeb (PRIMARY - Arabic/English Medical Content)
    "nih.gov",              # NIH (National Institutes of Health)
    "medlineplus.gov",      # MedlinePlus (NIH)
    "mayoclinic.org",       # Mayo Clinic
    "webmd.com",            # WebMD
    "healthline.com",       # Healthline
    "who.int",              # World Health Organization
    "cdc.gov",              # CDC (Centers for Disease Control)
    "pubmed.ncbi.nlm.nih.gov", # PubMed
]

# Domain priority for ranking search results (lower number = higher priority)
DOMAIN_PRIORITY = {
    "webteb.com": 0,        # HIGHEST PRIORITY - Primary source
    "who.int": 1,           # Global authority
    "cdc.gov": 1,           # National authority
    "nih.gov": 1,           # Research authority
    "medlineplus.gov": 2,
    "mayoclinic.org": 2,
    "pubmed.ncbi.nlm.nih.gov": 2,
    "webmd.com": 3,
    "healthline.com": 4,
}

# Special case keywords requiring extra caution
SPECIAL_CASE_KEYWORDS = {
    "children": ["child", "baby", "infant", "toddler", "kid", "pediatric"],
    "pregnancy": ["pregnant", "pregnancy", "expecting", "prenatal"],
}
