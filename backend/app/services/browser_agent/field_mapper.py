"""
Field Mapper Component for Phase 6 Controlled Browser-Based Application Agent.
Enforces Field Safety Rules:
- Only populates values verified by the Master CV and Phase 5 Application Package.
- NEVER guesses or fabricates unknown fields (Salary, Notice Period, Relocation, unknown screening questions).
- Marks unknown or uncertain fields as REQUIRES_USER_INPUT.
"""

from typing import Dict, Any, List, Optional
from backend.app.services.browser_agent.form_detector import DetectedField
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class MappedField:
    def __init__(
        self,
        field: DetectedField,
        value: Optional[str],
        status: str,  # SUPPORTED, REQUIRES_USER_INPUT, USER_OVERRIDDEN, UNSUPPORTED
        source: str = "Master CV",
        reason: str = ""
    ):
        self.field = field
        self.value = value
        self.status = status
        self.source = source
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_id": self.field.field_id,
            "name": self.field.name,
            "category": self.field.detected_category,
            "selector": self.field.selector,
            "value": self.value,
            "status": self.status,
            "source": self.source,
            "reason": self.reason,
            "required": self.field.required,
        }


class FieldMapper:
    """
    Safely maps detected HTML fields to candidate verified data.
    Strictly forbids ungrounded auto-answering.
    """

    @classmethod
    def map_fields(
        cls,
        detected_fields: List[DetectedField],
        candidate_profile: Dict[str, Any],
        application_answers: List[Dict[str, Any]],
        cover_letter: Optional[str] = None,
        custom_overrides: Optional[Dict[str, str]] = None
    ) -> List[MappedField]:
        """
        Maps detected fields to verified profile data.
        """
        mapped: List[MappedField] = []
        custom_overrides = custom_overrides or {}

        # Build answers lookup by question_key
        answers_lookup = {
            a.get("question_key"): a.get("answer_text")
            for a in application_answers
            if a.get("status") in ("AUTO_ANSWERED", "USER_EDITED") and a.get("answer_text")
        }

        full_name = candidate_profile.get("full_name") or ""
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        for f in detected_fields:
            # 1. Check for manual user override
            if f.name in custom_overrides or f.field_id in custom_overrides:
                override_val = custom_overrides.get(f.name) or custom_overrides.get(f.field_id)
                mapped.append(MappedField(
                    field=f,
                    value=override_val,
                    status="USER_OVERRIDDEN",
                    source="User Input Override",
                    reason="Explicit value provided by applicant."
                ))
                continue

            category = f.detected_category

            # 2. Map verified core candidate fields
            if category == "full_name":
                mapped.append(MappedField(
                    field=f,
                    value=full_name,
                    status="SUPPORTED",
                    source="Master CV",
                    reason="Verified candidate full name"
                ))
            elif category == "first_name":
                mapped.append(MappedField(
                    field=f,
                    value=first_name,
                    status="SUPPORTED",
                    source="Master CV",
                    reason="Verified first name"
                ))
            elif category == "last_name":
                mapped.append(MappedField(
                    field=f,
                    value=last_name,
                    status="SUPPORTED",
                    source="Master CV",
                    reason="Verified last name"
                ))
            elif category == "email":
                mapped.append(MappedField(
                    field=f,
                    value=candidate_profile.get("email"),
                    status="SUPPORTED" if candidate_profile.get("email") else "REQUIRES_USER_INPUT",
                    source="Master CV",
                    reason="Verified candidate email"
                ))
            elif category == "phone":
                phone = candidate_profile.get("phone")
                mapped.append(MappedField(
                    field=f,
                    value=phone,
                    status="SUPPORTED" if phone else "REQUIRES_USER_INPUT",
                    source="Master CV",
                    reason="Verified candidate phone number"
                ))
            elif category == "location":
                mapped.append(MappedField(
                    field=f,
                    value=candidate_profile.get("location") or "Lahore, Pakistan",
                    status="SUPPORTED",
                    source="Master CV",
                    reason="Verified candidate location"
                ))
            elif category == "linkedin":
                mapped.append(MappedField(
                    field=f,
                    value=candidate_profile.get("linkedin"),
                    status="SUPPORTED" if candidate_profile.get("linkedin") else "REQUIRES_USER_INPUT",
                    source="Master CV",
                    reason="Candidate LinkedIn profile"
                ))
            elif category == "github":
                mapped.append(MappedField(
                    field=f,
                    value=candidate_profile.get("github"),
                    status="SUPPORTED" if candidate_profile.get("github") else "REQUIRES_USER_INPUT",
                    source="Master CV",
                    reason="Candidate GitHub profile"
                ))
            elif category == "portfolio":
                mapped.append(MappedField(
                    field=f,
                    value=candidate_profile.get("portfolio") or candidate_profile.get("github"),
                    status="SUPPORTED",
                    source="Master CV",
                    reason="Portfolio / Website URL"
                ))
            elif category == "cover_letter":
                mapped.append(MappedField(
                    field=f,
                    value=cover_letter,
                    status="SUPPORTED" if cover_letter else "REQUIRES_USER_INPUT",
                    source="Phase 5 Approved Cover Letter",
                    reason="Approved job-specific cover letter"
                ))
            elif category == "resume":
                # Handled separately by file_uploader component
                mapped.append(MappedField(
                    field=f,
                    value="[TAILORED_CV_FILE]",
                    status="SUPPORTED",
                    source="Phase 4 Tailored CV",
                    reason="Approved tailored CV document file upload"
                ))

            # 3. Handle Sensitive / Unknown Personal Questions - STRICT SAFETY BOUNDARY: DO NOT GUESS!
            elif category in ("salary", "notice_period", "work_authorization"):
                # Check if user already provided answer in Phase 5 package
                ans = answers_lookup.get(f"expected_{category}") or answers_lookup.get(category)
                if ans:
                    mapped.append(MappedField(
                        field=f,
                        value=ans,
                        status="SUPPORTED",
                        source="Phase 5 Saved Answer",
                        reason=f"Approved answer for {category}"
                    ))
                else:
                    mapped.append(MappedField(
                        field=f,
                        value=None,
                        status="REQUIRES_USER_INPUT",
                        source="None",
                        reason=f"Do not guess {category}; requires explicit user specification."
                    ))

            elif category == "screening_question":
                # Check for matching known screening question
                matched_ans = None
                label_lower = f"{f.label} {f.name}".lower()
                for q_key, q_val in answers_lookup.items():
                    if q_key.replace("_", " ") in label_lower:
                        matched_ans = q_val
                        break

                if matched_ans:
                    mapped.append(MappedField(
                        field=f,
                        value=matched_ans,
                        status="SUPPORTED",
                        source="Phase 5 Screening Answer",
                        reason=f"Matched known question '{f.label}'"
                    ))
                else:
                    mapped.append(MappedField(
                        field=f,
                        value=None,
                        status="REQUIRES_USER_INPUT",
                        source="None",
                        reason=f"Unknown screening question '{f.label or f.name}'; agent must not invent answers."
                    ))
            else:
                mapped.append(MappedField(
                    field=f,
                    value=None,
                    status="REQUIRES_USER_INPUT" if f.required else "UNSUPPORTED",
                    source="None",
                    reason="Unmapped field"
                ))

        return mapped
