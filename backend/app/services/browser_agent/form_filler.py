"""
Form Filler Component for Phase 6 Controlled Browser-Based Application Agent.
Populates verified values safely into DOM elements.
Never inputs unverified, guessed, or fabricated data.
"""

from typing import List, Dict, Any
from playwright.sync_api import Page
from backend.app.services.browser_agent.field_mapper import MappedField
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class FilledFieldRecord:
    def __init__(self, field_id: str, name: str, category: str, value: str):
        self.field_id = field_id
        self.name = name
        self.category = category
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_id": self.field_id,
            "name": self.name,
            "category": self.category,
            "value": self.value,
        }


class FormFiller:
    """
    Interacts with browser elements to populate verified candidate data.
    """

    @classmethod
    def fill_form(cls, page: Page, mapped_fields: List[MappedField]) -> List[FilledFieldRecord]:
        """
        Fills only fields that have status 'SUPPORTED' or 'USER_OVERRIDDEN' with non-null values.
        Skips file inputs (handled by FileUploader) and unverified fields.
        """
        filled_records: List[FilledFieldRecord] = []

        for item in mapped_fields:
            # Enforce Field Safety: never populate unverified values
            if item.status not in ("SUPPORTED", "USER_OVERRIDDEN") or not item.value:
                continue

            field = item.field
            if field.field_type == "file" or field.detected_category == "resume":
                # File upload is handled exclusively by FileUploader
                continue

            selector = field.selector
            value_to_fill = str(item.value)

            try:
                locator = page.locator(selector).first
                if not locator.is_visible():
                    logger.debug(f"Element {selector} not currently visible, attempting to scroll into view.")
                    locator.scroll_into_view_if_needed(timeout=2000)

                if field.field_type in ("text", "email", "tel", "url"):
                    locator.fill(value_to_fill)
                    filled_records.append(FilledFieldRecord(
                        field_id=field.field_id,
                        name=field.name,
                        category=field.detected_category,
                        value=value_to_fill
                    ))
                    logger.info(f"Populated input {field.name or field.field_id} ({field.detected_category}).")

                elif field.field_type == "textarea":
                    locator.fill(value_to_fill)
                    filled_records.append(FilledFieldRecord(
                        field_id=field.field_id,
                        name=field.name,
                        category=field.detected_category,
                        value=value_to_fill[:100] + ("..." if len(value_to_fill) > 100 else "")
                    ))
                    logger.info(f"Populated textarea {field.name or field.field_id} ({field.detected_category}).")

                elif field.field_type == "select":
                    # Try selecting by label, value, or index
                    try:
                        locator.select_option(label=value_to_fill)
                    except Exception:
                        try:
                            locator.select_option(value=value_to_fill)
                        except Exception:
                            # Fuzzy match option
                            for opt in field.options:
                                if value_to_fill.lower() in opt.lower():
                                    locator.select_option(label=opt)
                                    break
                    filled_records.append(FilledFieldRecord(
                        field_id=field.field_id,
                        name=field.name,
                        category=field.detected_category,
                        value=value_to_fill
                    ))
                    logger.info(f"Selected option for {field.name or field.field_id}: {value_to_fill}")

            except Exception as e:
                logger.warning(f"Could not populate element {selector}: {e}")

        return filled_records
