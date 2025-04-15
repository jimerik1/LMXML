# services/xml/utils.py
import random
import string
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

def generate_random_id(length: int = 5) -> str:
    """Generate a random alphanumeric ID of specified length."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def calculate_emw(pressure: float, depth: float) -> float:
    """
    Calculate Equivalent Mud Weight (EMW) from pressure and depth.
    
    Args:
        pressure: Pressure value
        depth: Depth value
        
    Returns:
        float: Calculated EMW
    """
    if depth <= 0:
        return 0.0
    return pressure / (0.052 * depth)

def format_xpath(tag: str, attr: str, value: str) -> str:
    """
    Format an XPath expression for finding elements.
    
    Args:
        tag: Element tag name
        attr: Attribute name
        value: Attribute value
        
    Returns:
        str: Formatted XPath expression
    """
    return f".//{tag}[@{attr}='{value}']"