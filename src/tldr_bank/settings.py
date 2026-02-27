import re
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '.custom_group_settings')

def load_group_patterns():
    patterns = []
    if not os.path.exists(SETTINGS_FILE):
        return patterns
    with open(SETTINGS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                pattern, label = [p.strip().upper() for p in line.split('=', 1)]
            else:
                pattern = label = line.upper()
            # Normalise pattern the same way _extract_entity does
            pattern = re.sub(r'[^A-Z ]', '', pattern).strip()
            patterns.append((pattern, label))
    return patterns