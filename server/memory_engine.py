import re

def extract_key_value(prompt: str):
    patterns = [
        (r"my (.+?) is (?:on|at|due|scheduled for) (.+)", 1, 2),
        (r"(?:remember|note) that (.+?) is (.+)", 1, 2),
        (r"(?:store|save) (.+?) as (.+)", 1, 2),
        (r"(.+?) expires on (.+)", 1, 2)
    ]
    
    for pattern, key_idx, value_idx in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            key = match.group(key_idx).strip().replace(" ", "_")
            value = match.group(value_idx).strip()
            return key.lower(), value
    return None, None  
