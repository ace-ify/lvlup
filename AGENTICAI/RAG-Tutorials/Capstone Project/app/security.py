import re
from typing import Tuple, List, Dict, Optional
from langsmith import traceable

class InputSanitizer:
    INJECTION_PATTERNS = [
        r"ignore\s+all\s+previous\s+instructions",
        r"---\s*end\s*(of)?\s*prompt",
        r"pretend\s+you\s+are",
        r"act\s+as\s+(if\s+)?you",
        r"bypass\s+(all\s+)?restrictions",
        r"reveal\s+(your|the)\s+(system|instructions|prompt)",
        r"you\s+are\s+now\s+(DAN|jailbroken)",
    ]

    def __init__(self):
        self.patterns = [
            re.compile(p, re.IGNORECASE)
            for p in self.INJECTION_PATTERNS
        ]
        
    @traceable(run_type="chain", name="Sanitize_Input")
    def check(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if input is safe.
        Returns: (is_safe, rejection_reason)
        """
        for pattern in self.patterns:
            if pattern.search(text):
                return False, "Blocked: potential prompt injection detected"
        return True, None

    def clean(self, text: str) -> str:
        """Remove potentially dangerous delimiters from input."""
        text = re.sub(r'[-]{3,}', '', text)
        text = re.sub(r'[=]{3,}', '', text)
        text = text.replace('{{', '{ {').replace('}}', '} }')
        return text.strip()


class PIIDetector:
    PATTERNS = {
        "EMAIL": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
        "PHONE": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
        "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b")
    }
    
    MASK_MAP = {
        "EMAIL": "[EMAIL REDACTED]",
        "PHONE": "[PHONE REDACTED]",
        "SSN": "[SSN REDACTED]",
        "CREDIT_CARD": "[CREDIT CARD REDACTED]"
    }

    @traceable(run_type="chain", name="Detect_PII")
    def detect(self, text: str) -> dict[str, list[str]]:
        """Detect PII types present in text."""
        found = {}
        for pii_type, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                found[pii_type] = matches
        return found

    @traceable(run_type="chain", name="Mask_PII")
    def mask(self, text: str) -> str:
        """Replace all PII with redaction markers."""
        masked = text
        for pii_type, pattern in self.PATTERNS.items():
            masked = pattern.sub(self.MASK_MAP[pii_type], masked)
        return masked


class OutputValidator:
    """
    Validate LLM output before returning to the client.
    Catches PII leakage and harmful content in responses.
    """

    HARMFUL_PATTERNS = [
        re.compile(r"here('s|\s+is)\s+(how|the\s+way)\s+to\s+(hack|steal|attack)", re.I),
        re.compile(r"password\s+is\s+", re.I),
        re.compile(r"api[_\s]?key\s*[:=]", re.I),
    ]

    def __init__(self):
        self.pii_detector = PIIDetector()

    @traceable(run_type="chain", name="Validate_Output")
    def validate(self, output: str) -> Tuple[str, List[str]]:
        """
        Validate and clean output.
        Returns: (cleaned_output, list_of_warnings)
        """
        warnings = []

        # Check for PII leakage in output
        pii_found = self.pii_detector.detect(output)
        if pii_found:
            output = self.pii_detector.mask(output)
            warnings.append(f"PII masked in output: {list(pii_found.keys())}")

        # Check for harmful content
        for pattern in self.HARMFUL_PATTERNS:
            if pattern.search(output):
                output = "[Response blocked: potentially harmful content]"
                warnings.append("Harmful content detected and blocked")
                break
                
        return output, warnings
