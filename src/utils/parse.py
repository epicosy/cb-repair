#!/usr/bin/env python3
import re

CWE_REGEX = r'CWE-\d{1,4}'

def cwe_from_info(description: str) -> list:
    return re.findall(CWE_REGEX, description)
