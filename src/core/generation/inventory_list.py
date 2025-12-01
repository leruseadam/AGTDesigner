"""
Inventory List Generator

This module generates inventory list documents directly from Excel-selected products.
It replaces the old inventory "slip" template with a category-grouped, alphabetized list.
"""

import logging
from collections import defaultdict
from typing import List, Dict, Any, Optional

from docx import Document
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH


logger = logging.getLogger(__name__)


def _get_product_name(record: Dict[str, Any]) -> str:
    """Best-effort extraction of product name from a record."""
    name = (
        record.get("Product Name*")
        or record.get("ProductName")
        or record.get("Description")
        or ""
    )
    return str(name).strip()


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
    - Columns include: Product Name, Quantity, Barcode, Accepted Date, Room.
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

        # Title
        title = doc.add_heading("Current Inventory", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Sort categories alphabetically
        for category in sorted(grouped.keys(), key=lambda c: c.lower()):
            items = grouped[category]
            if not items:
                continue

            # Category heading
            heading = doc.add_heading(category, level=1)
            heading.alignment = WD_ALIGN_PARAGRAPH.LEFT

            # Table with 5 columns
            table = doc.add_table(rows=1, cols=5)
            table.style = "Light Grid Accent 1"
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            headers = ["Product Name", "Quantity", "Barcode", "Accepted Date", "Room"]
            header_cells = table.rows[0].cells
            for idx, text in enumerate(headers):
                header_cells[idx].text = text
                for paragraph in header_cells[idx].paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.size = Pt(11)

            # Sort items within category alphabetically by product name
            items_sorted = sorted(
                items,
                key=lambda r: _get_product_name(r).lower(),
            )

            for record in items_sorted:
                row_cells = table.add_row().cells
                row_cells[0].text = _get_product_name(record)
                row_cells[1].text = _get_quantity(record)
                row_cells[2].text = _get_barcode(record)
                row_cells[3].text = _get_accepted_date(record)
                row_cells[4].text = _get_room(record)

            # Add a blank paragraph after each category for spacing
            doc.add_paragraph("")

        logger.info(
            f"INVENTORY LIST: Generated inventory list with "
            f"{len(grouped)} categories and {total_rows} rows"
        )
        return doc
    except Exception as e:
        logger.warning(f"INVENTORY LIST: Failed to create inventory list document: {e}")
        return None


