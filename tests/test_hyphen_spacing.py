import pytest
import re

from src.core.generation.tag_generator import wrap_with_marker
from src.core.generation import template_processor

def format_desc_and_weight(desc, weight):
    # Simulate the logic from tag_generator.py for combining desc and weight
    if desc:
        desc = re.sub(r'[-\s]+$', '', desc)
    # Always format weight as '1g x 2 Pack' if it matches '1gx2Pack' or similar
    match = re.match(r"([0-9.]+)g\s*x?\s*([0-9]+)\s*Pack", weight, re.IGNORECASE)
    if not match:
        match = re.match(r"([0-9.]+)g\s*x?\s*([0-9]+)", weight, re.IGNORECASE)
    if match:
        g, n = match.groups()
        weight = f"{g}g x {n} Pack"
    if desc and weight:
        lines = desc.splitlines()
        if lines:
            lines[-1] = f"{lines[-1].rstrip()} \u00AD\u00A0{weight}"
            combined = "\n".join(lines)
        else:
            combined = f"\u00AD\u00A0{weight}"
    else:
        combined = desc or weight
    return wrap_with_marker(combined, "DESC")

def test_soft_hyphen_and_nonbreaking_space():
    desc = "Amnesia Lemon Pre-Roll"
    weight = "1g x 2 Pack"
    result = format_desc_and_weight(desc, weight)
    # The expected separator is soft hyphen + non-breaking space
    expected = "Amnesia Lemon Pre-Roll \u00AD\u00A01g x 2 Pack"
    assert expected in result, f"Expected '{expected}' in '{result}'"

def test_descandweight_tag_generator_preserves_spaces():
    desc = "Test Pre-Roll"
    joint_ratio = "1g x 2 Pack"
    result = format_desc_and_weight(desc, joint_ratio)
    assert "1g x 2 Pack" in result, "Spaces in JointRatio should be preserved in tag_generator.py logic"

def test_descandweight_template_processor_preserves_spaces():
    # Simulate the context as built in template_processor.py
    record = {
        'Description': 'Test Pre-Roll',
        'WeightUnits': '1g x 2 Pack',
        'Product Type*': 'pre-roll',
    }
    # Provide required arguments for TemplateProcessor
    tp = template_processor.TemplateProcessor(template_type='vertical', font_scheme='Arial')
    context = tp._build_label_context(record, doc=None)
    # Now we expect spaces to be preserved in DescAndWeight
    assert '1g x 2 Pack' in context['DescAndWeight'], "Spaces in JointRatio/WeightUnits should be preserved in DescAndWeight"

def test_hanging_hyphen_removed():
    desc = "Test Pre-Roll -"
    weight = "1g x 2 Pack"
    result = format_desc_and_weight(desc, weight)
    # The hyphen at the end of desc should not result in a double hyphen or hanging hyphen
    # It should be: 'Test Pre-Roll \u00AD\u00A01g x 2 Pack' (no extra hyphen)
    expected = "Test Pre-Roll \u00AD\u00A01g x 2 Pack"
    assert expected in result, f"Expected no hanging hyphen, got: {result}" 