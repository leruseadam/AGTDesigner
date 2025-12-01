"""
Inventory List Generator

This module generates inventory list documents directly from Excel-selected products.
It replaces the old inventory "slip" template with a category-grouped, alphabetized list.
"""

import logging
from collections import defaultdict
from typing import List, Dict, Any, Optional

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH


logger = logging.getLogger(__name__)


def _get_product_name(record: Dict[str, Any]) -> str:
    """
    Best-effort extraction of product name from a record using the same
    shortening rules as Excel tag processing:
    - Start from Product Name* / ProductName / Description
    - Remove everything from ' by ' onward
    - Then remove trailing weight info after ' - ' when it looks like weight.
    """
    name = (
        record.get("Product Name*")
        or record.get("ProductName")
        or record.get("Description")
        or ""
    )
    full_name = str(name).strip()
    if not full_name:
        return ""

    # Reuse the same logic as excel_processor._extract_product_name_from_full_name
    text = full_name
    if " by " in text and " - " in text:
        return text.split(" by ")[0].strip()
    if " by " in text:
        return text.split(" by ")[0].strip()
    if " - " in text:
        import re

        if re.search(r" - [\d.]", text):
            # Remove weight part but preserve the dash in product names
            return re.sub(r" - [\d.].*$", "", text).strip()
    return text.strip()


def _get_product_type(record: Dict[str, Any]) -> str:
    """Product type/category text for a dedicated column."""
    value = (
        record.get("Product Type*")
        or record.get("ProductType")
        or record.get("inventory_type")
        or record.get("Inventory Type")
        or ""
    )
    return str(value).strip()


def _get_brand(record: Dict[str, Any]) -> str:
    """Brand text for a dedicated column."""
    value = (
        record.get("Product Brand")
        or record.get("Brand")
        or record.get("brand")
        or ""
    )
    return str(value).strip()


def _get_weight(record: Dict[str, Any]) -> str:
    """Weight text for a dedicated column."""
    value = (
        record.get("WeightUnits")
        or record.get("CombinedWeight")
        or record.get("Weight*")
        or record.get("Weight")
        or ""
    )
    return str(value).strip()


def _get_vendor(record: Dict[str, Any]) -> str:
    """Vendor text for a dedicated column."""
    value = (
        record.get("Vendor/Supplier*")
        or record.get("Vendor")
        or record.get("vendor")
        or ""
    )
    return str(value).strip()


def _get_category(record: Dict[str, Any]) -> str:
    """
    Determine category for grouping.
    Prefer canonical product type from Excel; fall back to any inventory_type-style fields.
    """
    category = (
        record.get("Product Type*")
        or record.get("ProductType")
        or record.get("inventory_type")
        or record.get("Inventory Type")
        or ""
    )
    category = str(category).strip()
    if not category:
        category = "Uncategorized"
    return category


def _get_quantity(record: Dict[str, Any]) -> str:
    """
    Quantity to display in list.
    Prefer selling quantity, then received quantity.
    """
    qty = (
        record.get("Quantity*")
        or record.get("Quantity")
        or record.get("Quantity Received*")
        or ""
    )
    return str(qty).strip()


def _get_barcode(record: Dict[str, Any]) -> str:
    """Barcode to display in list."""
    barcode = record.get("Barcode*") or record.get("Barcode") or ""
    return str(barcode).strip()


def _get_accepted_date(record: Dict[str, Any]) -> str:
    """Accepted date to display in list."""
    accepted = record.get("Accepted Date") or ""
    return str(accepted).strip()


def _get_room(record: Dict[str, Any]) -> str:
    """Room to display in list."""
    room = record.get("Room*") or record.get("Room") or ""
    return str(room).strip()


def generate_inventory_list(records: List[Dict[str, Any]]) -> Optional[Document]:
    """
    Generate an inventory list document from selected Excel products.

    Behaviour:
    - Uses whatever products are currently selected in the UI (records list).
    - Groups items by category (product type) and sorts categories alphabetically.
    - Within each category, products are sorted alphabetically by product name.
    - Each distinct record is preserved (NO deduplication), so items with different
      barcodes will appear multiple times as required.
    - Columns include:
      Product Name, Product Type, Brand, Weight, Vendor,
      Quantity, Barcode, Accepted Date, Room.
    """
    try:
        if not records:
            logger.info("INVENTORY LIST: No records provided, skipping list generation")
            return None

        # Build groups by category
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        total_rows = 0

        for record in records:
            name = _get_product_name(record)
            if not name:
                # Skip completely nameless records
                continue
            category = _get_category(record)
            grouped[category].append(record)
            total_rows += 1

        if not grouped:
            logger.info("INVENTORY LIST: No groupable records found")
            return None

        doc = Document()

        # Make document landscape to maximize horizontal space
        try:
            section = doc.sections[0]
            # Swap orientation to landscape
            new_width, new_height = section.page_height, section.page_width
            section.page_width = new_width
            section.page_height = new_height
            # Tighten margins a bit to fit more columns/rows on the page
            section.left_margin = Inches(0.25)
            section.right_margin = Inches(0.25)
            section.top_margin = Inches(0.25)
            section.bottom_margin = Inches(0.25)
        except Exception as e:
            logger.warning(f"INVENTORY LIST: Failed to set landscape orientation: {e}")

        # Title
        title = doc.add_heading("Current Inventory", level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Smaller title to save vertical space
        for run in title.runs:
            run.font.size = Pt(14)

        # Sort categories alphabetically
        for category in sorted(grouped.keys(), key=lambda c: c.lower()):
            items = grouped[category]
            if not items:
                continue

            # Category heading
            heading = doc.add_heading(category, level=1)
            heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in heading.runs:
                run.font.size = Pt(9)
            # Remove extra spacing before/after heading
            for paragraph in heading._element.xpath(".//w:p"):
                p = paragraph
                # We can't easily wrap as Paragraph, but heading spacing is already small; skip heavy XML tweaks

            # Table with 9 columns - use a plain grid style to minimize ink (no colored fills)
            table = doc.add_table(rows=1, cols=9)
            table.style = "Table Grid"
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            headers = [
                "Product Name",
                "Product Type",
                "Brand",
                "Weight",
                "Vendor",
                "Quantity",
                "Barcode",
                "Accepted Date",
                "Room",
            ]
            header_cells = table.rows[0].cells
            for idx, text in enumerate(headers):
                header_cells[idx].text = text
                for paragraph in header_cells[idx].paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.size = Pt(7)
                    # Compact header spacing
                    paragraph.paragraph_format.space_before = Pt(0)
                    paragraph.paragraph_format.space_after = Pt(0)
                    paragraph.paragraph_format.line_spacing = 1.0

            # Make header row more compact
            header_row = table.rows[0]
            header_row.height = Pt(10)
            header_row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST

            # Sort items within category alphabetically by product name
            items_sorted = sorted(
                items,
                key=lambda r: _get_product_name(r).lower(),
            )

            for record in items_sorted:
                row_cells = table.add_row().cells
                row_cells[0].text = _get_product_name(record)
                row_cells[1].text = _get_product_type(record)
                row_cells[2].text = _get_brand(record)
                row_cells[3].text = _get_weight(record)
                row_cells[4].text = _get_vendor(record)
                row_cells[5].text = _get_quantity(record)
                row_cells[6].text = _get_barcode(record)
                row_cells[7].text = _get_accepted_date(record)
                row_cells[8].text = _get_room(record)

                # Make body font very compact to maximize rows per page
                for cell in row_cells:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.size = Pt(6)
                        paragraph.paragraph_format.space_before = Pt(0)
                        paragraph.paragraph_format.space_after = Pt(0)
                        paragraph.paragraph_format.line_spacing = 1.0

                # Compact row height
                row = table.rows[-1]
                row.height = Pt(9)
                row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST

        logger.info(
            f"INVENTORY LIST: Generated inventory list with "
            f"{len(grouped)} categories and {total_rows} rows"
        )
        return doc
    except Exception as e:
        logger.warning(f"INVENTORY LIST: Failed to create inventory list document: {e}")
        return None


