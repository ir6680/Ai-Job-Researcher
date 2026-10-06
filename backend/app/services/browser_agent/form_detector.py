"""
Form Detector Component for Phase 6 Controlled Browser-Based Application Agent.
Detects application forms, field inputs, labels, file uploaders, and security barriers (CAPTCHA / OTP / Auth).
CRITICAL: Never bypasses CAPTCHA, OTP, or authentication mechanisms.
"""

import re
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class DetectedField:
    def __init__(
        self,
        field_id: str,
        name: str,
        field_type: str,
        selector: str,
        label: str = "",
        placeholder: str = "",
        required: bool = False,
        detected_category: str = "unknown",
        options: Optional[List[str]] = None,
    ):
        self.field_id = field_id
        self.name = name
        self.field_type = field_type  # text, email, tel, file, textarea, select, checkbox, radio
        self.selector = selector
        self.label = label
        self.placeholder = placeholder
        self.required = required
        self.detected_category = detected_category  # full_name, email, phone, resume, cover_letter, etc.
        self.options = options or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_id": self.field_id,
            "name": self.name,
            "field_type": self.field_type,
            "selector": self.selector,
            "label": self.label,
            "placeholder": self.placeholder,
            "required": self.required,
            "detected_category": self.detected_category,
            "options": self.options,
        }


class FormDetectionResult:
    def __init__(
        self,
        form_found: bool,
        fields: List[DetectedField],
        captcha_detected: bool = False,
        captcha_type: Optional[str] = None,
        otp_detected: bool = False,
        auth_required: bool = False,
        submit_button_selector: Optional[str] = None,
        submit_button_text: Optional[str] = None,
    ):
        self.form_found = form_found
        self.fields = fields
        self.captcha_detected = captcha_detected
        self.captcha_type = captcha_type
        self.otp_detected = otp_detected
        self.auth_required = auth_required
        self.submit_button_selector = submit_button_selector
        self.submit_button_text = submit_button_text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "form_found": self.form_found,
            "fields_count": len(self.fields),
            "fields": [f.to_dict() for f in self.fields],
            "captcha_detected": self.captcha_detected,
            "captcha_type": self.captcha_type,
            "otp_detected": self.otp_detected,
            "auth_required": self.auth_required,
            "has_submit_button": bool(self.submit_button_selector),
        }


class FormDetector:
    """
    Scans the DOM to identify application forms, inputs, file upload areas,
    and detects anti-bot / authentication challenges without attempting bypass.
    """

    # Category matching regex heuristics
    CATEGORY_PATTERNS = {
        "full_name": re.compile(r"\b(full\s*name|your\s*name|applicant\s*name|name)\b", re.I),
        "first_name": re.compile(r"\b(first\s*name|given\s*name|fname)\b", re.I),
        "last_name": re.compile(r"\b(last\s*name|surname|family\s*name|lname)\b", re.I),
        "email": re.compile(r"\b(email|e-mail|mail)\b", re.I),
        "phone": re.compile(r"\b(phone|mobile|cell|contact\s*number|telephone)\b", re.I),
        "location": re.compile(r"\b(location|city|address|current\s*city|residence)\b", re.I),
        "linkedin": re.compile(r"\b(linkedin|linked\s*in)\b", re.I),
        "github": re.compile(r"\b(github|git\s*hub)\b", re.I),
        "portfolio": re.compile(r"\b(portfolio|website|personal\s*site|url)\b", re.I),
        "resume": re.compile(r"\b(resume|cv|curriculum\s*vitae|attach\s*cv|upload\s*resume)\b", re.I),
        "cover_letter": re.compile(r"\b(cover\s*letter|letter|message|note\s*to\s*hiring\s*manager)\b", re.I),
        "salary": re.compile(r"\b(salary|compensation|expected\s*salary|desired\s*salary|remuneration)\b", re.I),
        "notice_period": re.compile(r"\b(notice\s*period|availability|start\s*date|how\s*soon)\b", re.I),
        "work_authorization": re.compile(r"\b(authorized|work\s*permit|sponsorship|eligible\s*to\s*work)\b", re.I),
        "education": re.compile(r"\b(education|degree|university|college|graduation)\b", re.I),
        "experience": re.compile(r"\b(experience|years\s*of\s*experience|total\s*experience)\b", re.I),
    }

    @classmethod
    def detect_security_barriers(cls, page: Page) -> Dict[str, Any]:
        """
        Detects CAPTCHA, OTP, and Login gates.
        Never bypasses them - prompts for human intervention.
        """
        barriers = {
            "captcha": False,
            "captcha_type": None,
            "otp": False,
            "auth": False
        }

        content_lower = page.content().lower()

        # 1. CAPTCHA Detection
        captcha_indicators = [
            ("g-recaptcha", "Google reCAPTCHA"),
            ("recaptcha", "Google reCAPTCHA"),
            ("hcaptcha", "hCaptcha"),
            ("cf-turnstile", "Cloudflare Turnstile"),
            ("arkose", "Arkose Labs"),
            ("funcaptcha", "FunCaptcha"),
            ("captcha", "Generic CAPTCHA"),
        ]
        for pattern, name in captcha_indicators:
            if pattern in content_lower:
                barriers["captcha"] = True
                barriers["captcha_type"] = name
                logger.warning(f"Security Barrier Detected: {name}")
                break

        # 2. OTP Detection
        otp_patterns = [
            "enter one-time password",
            "enter otp",
            "verification code sent",
            "sms code",
            "2-step verification",
            "two-factor authentication"
        ]
        if any(p in content_lower for p in otp_patterns):
            barriers["otp"] = True
            logger.warning("Security Barrier Detected: OTP / 2FA Challenge")

        # 3. Authentication / Login Gate
        auth_patterns = [
            "sign in to apply",
            "log in to apply",
            "login required",
            "create an account to apply"
        ]
        if any(p in content_lower for p in auth_patterns):
            # Check if there is an active password field
            pwd_count = page.locator("input[type='password']").count()
            if pwd_count > 0:
                barriers["auth"] = True
                logger.warning("Security Barrier Detected: Account Authentication Gate")

        return barriers

    @classmethod
    def classify_field(cls, label: str, name: str, placeholder: str, field_type: str) -> str:
        """Classifies a field into a semantic candidate profile category."""
        if field_type == "file":
            return "resume"

        combined_text = f"{label} {name} {placeholder}".lower()

        for category, pattern in cls.CATEGORY_PATTERNS.items():
            if pattern.search(combined_text):
                return category

        return "screening_question" if field_type in ("textarea", "text", "select") else "unknown"

    @classmethod
    def detect_form(cls, page: Page) -> FormDetectionResult:
        """
        Inspects the page and extracts all candidate application inputs.
        """
        # First check security barriers
        barriers = cls.detect_security_barriers(page)

        fields: List[DetectedField] = []

        # Find input, textarea, select elements
        elements = page.query_selector_all("input, textarea, select")

        for idx, el in enumerate(elements):
            tag_name = el.evaluate("e => e.tagName.toLowerCase()")
            input_type = el.get_attribute("type") or ("textarea" if tag_name == "textarea" else "select" if tag_name == "select" else "text")
            input_type = input_type.lower()

            # Skip hidden, submit, reset, button types from field mapping
            if input_type in ("hidden", "submit", "reset", "button", "image"):
                continue

            name = el.get_attribute("name") or ""
            field_id = el.get_attribute("id") or f"field_{idx}"
            placeholder = el.get_attribute("placeholder") or ""
            required = el.get_attribute("required") is not None or "required" in (el.get_attribute("class") or "").lower()

            # Attempt to find associated label
            label = ""
            if field_id:
                label_el = page.query_selector(f"label[for='{field_id}']")
                if label_el:
                    label = label_el.inner_text().strip()

            if not label:
                # Check parent or closest label
                try:
                    label = el.evaluate("""e => {
                        const lbl = e.closest('label');
                        if (lbl) return lbl.innerText.trim();
                        const prev = e.previousElementSibling;
                        if (prev && prev.tagName.toLowerCase() === 'label') return prev.innerText.trim();
                        return e.getAttribute('aria-label') || '';
                    }""") or ""
                except Exception:
                    label = ""

            category = cls.classify_field(label, name, placeholder, input_type)

            # Build safe selector
            if field_id and not field_id.startswith("field_"):
                selector = f"#{field_id}"
            elif name:
                selector = f"{tag_name}[name='{name}']"
            else:
                selector = f"{tag_name}:nth-of-type({idx + 1})"

            # Extract options if select
            options = []
            if tag_name == "select":
                try:
                    options = el.evaluate("e => Array.from(e.options).map(o => o.text.trim())")
                except Exception:
                    options = []

            detected_field = DetectedField(
                field_id=field_id,
                name=name,
                field_type=input_type,
                selector=selector,
                label=label,
                placeholder=placeholder,
                required=required,
                detected_category=category,
                options=options
            )
            fields.append(detected_field)

        # Detect submit button
        submit_btn_selector = None
        submit_btn_text = None

        btn_candidates = page.query_selector_all(
            "button[type='submit'], input[type='submit'], button:not([type]), [role='button']"
        )
        for btn in btn_candidates:
            text = btn.inner_text().strip() if btn.evaluate("e => e.innerText") else ""
            if not text and btn.get_attribute("value"):
                text = btn.get_attribute("value")

            if any(k in text.lower() for k in ["submit", "apply", "send application", "send"]):
                submit_btn_selector = btn.evaluate("""e => {
                    if (e.id) return '#' + e.id;
                    if (e.name) return 'button[name=\"' + e.name + '\"]';
                    return 'button';
                }""")
                submit_btn_text = text
                break

        form_found = len(fields) > 0 or bool(submit_btn_selector)

        return FormDetectionResult(
            form_found=form_found,
            fields=fields,
            captcha_detected=barriers["captcha"],
            captcha_type=barriers["captcha_type"],
            otp_detected=barriers["otp"],
            auth_required=barriers["auth"],
            submit_button_selector=submit_btn_selector,
            submit_button_text=submit_btn_text
        )
