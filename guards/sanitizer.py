"""
Input Sanitizer for Customer Support Pipeline.
Satisfies SPEC §5.4, S-1, S-2, and TECHNICAL §4 Stage 6.
"""

import re
from typing import Tuple

MAX_MESSAGE_LENGTH = 1000

# Obvious forbidden null-bytes or binary control characters (S-1)
FORBIDDEN_CHARS_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

def sanitize_input(text: str) -> Tuple[bool, str]:
    """
    Validates user input length and basic character cleanliness.
    Per SPEC S-2, standard punctuation (apostrophes, #, $, :, ;, @) is explicitly allowed.
    Returns (is_valid, reason_or_detail).
    """
    if not text or not text.strip():
        return False, "Message is empty"
    
    if len(text) > MAX_MESSAGE_LENGTH:
        return False, f"Message exceeds length limit of {MAX_MESSAGE_LENGTH} characters"
    
    if FORBIDDEN_CHARS_PATTERN.search(text):
        return False, "Input contains forbidden control characters or null bytes"
        
    return True, "Input passed length and character hygiene checks"
