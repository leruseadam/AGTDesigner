import json
from src.core.data.json_matcher import extract_products_from_manifest

# Example manifest JSON (truncated for brevity, add more items as needed)
manifest_json = {
  "document_name": "WCIA Transfer Schema",
  "document_schema_version": "2.1.0",
  "document_origin": "https://files.cultivera.com/435553542D57533130383235/Interop/25/16/3EGQ3216P7YSVJCF/Cultivera_ORD-5430_422044.json",
  "from_license_number": "412627",
  "from_license_name": "JSM LLC",
  "to_license_number": "422044",
  "to_license_name": "A GREENER TODAY BOTHELL",
  "to_license_type": None,
  "transporter_name": "TERPENE TRANSIT                              ",
  "transporter_license": "426061",
  "manifest_type": "transporter",
  "created_at": "2025-04-24T15:07:14+00:00",
  "updated_at": "2025-04-24T15:07:14+00:00",
  "transferred_at": "2025-04-24T15:00:00+00:00",
  "external_id": "0000005466",
  "transfer_id": "18800589441865253",
  "est_departed_at": "2025-04-24T15:00:00+00:00",
  "est_arrival_at": "2025-04-25T15:39:23+00:00",
  "route": "Head north toward 59th Ave NE\nTurn left toward 59th Ave NE\nTurn right toward 59th Ave NE\nTurn left onto 59th Ave NE\nTurn right onto 172nd St NE/Edgecomb Rd\nAt the traffic circle, take the 2nd exit onto WA-531 W/172nd St NE/Edgecomb RdContinue to follow WA-531 W/172nd St NE\nTake the Interstate 5 S ramp to Seattle\nMerge onto I-5 S\nTake exit 186 for WA-96 E\nTurn left onto WA-96 E/128th St SW\nTurn right onto Dumas Rd\nTurn right onto WA-527 S\nTurn leftDestination will be on the right",
  "inventory_transfer_items": [
    {
      "created_at": "2025-04-21T21:43:51+00:00",
      "updated_at": "2025-04-21T21:43:51+00:00",
      "integrator_data": "C108251V1S185680000246914",
      "is_sample": "0",
      "sample_type": None,
      "product_name": "Medically Compliant - Dank Czar Rosin All-In-One - GMO - 1g",
      "qty": 10,
      "serving_weight": None,
      "unit_weight": 1,
      "line_price": 200,
      "uom": "ea",
      "unit_weight_uom": "g",
      "inventory_id": "18800565902471256",
      "sample_source_id": "18800160227924755",
      "is_medical": "1",
      "is_for_extraction": "0",
      "lab_result_passed": "passed",
      "lab_result_link": "https://files.cultivera.com/https://files.cultivera.com/435553542D57533130383235/Interop/25/11/WZFAKCWMRVMDKKG8/C10825_qaSJR9HH3E.json",
      "lab_result_data": {
        "lab_result_id": "1176566",
        "lab_result_status": "passed",
        "lab_result_detail": "https://files.cultivera.com/https://files.cultivera.com/435553542D57533130383235/Interop/25/11/WZFAKCWMRVMDKKG8/C10825_qaSJR9HH3E.json",
        "coa": "https://files.cultivera.com/435553542D57533130383235/Coas/25/03/19/NQQ2D1WHXWSG8Z25/18800160227924755.pdf",
        "potency": [
          {"type": "cbd", "value": 0, "unit": "pct"},
          {"type": "thc", "value": 5.5, "unit": "pct"},
          {"type": "thca", "value": 78, "unit": "pct"},
          {"type": "cbda", "value": 0, "unit": "pct"},
          {"type": "total-cannabinoids", "value": 86, "unit": "pct"}
        ],
        "lab_result_list": [
          {
            "coa": "https://files.cultivera.com/435553542D57533130383235/Coas/25/03/19/NQQ2D1WHXWSG8Z25/18800160227924755.pdf",
            "lab_result_id": "1176566",
            "lab_result_status": "passed",
            "lab_result_link": "https://files.cultivera.com/https://files.cultivera.com/435553542D57533130383235/Interop/25/11/WZFAKCWMRVMDKKG8/C10825_qaSJR9HH3E.json",
            "coa_release_date": None,
            "coa_amended_date": None,
            "coa_expire_date": None
          }
        ]
      },
      "inventory_category": "IntermediateProduct",
      "inventory_type": "Concentrate for Inhalation",
      "strain_name": "GMO",
      "product_sku": None
    },
    {
      "created_at": "2025-04-21T21:43:51+00:00",
      "updated_at": "2025-04-21T21:43:51+00:00",
      "integrator_data": "C108251Z1T193210000246915",
      "is_sample": "0",
      "sample_type": None,
      "product_name": "Medically Compliant - Dank Czar Rosin All-In-One - Grape Gas - 1g",
      "qty": 10,
      "serving_weight": None,
      "unit_weight": 1,
      "line_price": 200,
      "uom": "ea",
      "unit_weight_uom": "g",
      "inventory_id": "18800565902471345",
      "sample_source_id": "18800227120782398",
      "is_medical": "1",
      "is_for_extraction": "0",
      "lab_result_passed": "passed",
      "lab_result_link": "https://files.cultivera.com/https://files.cultivera.com/435553542D57533130383235/Interop/25/12/ANYMMT8C9EMENBT3/C10825_qa21VGX2V6.json",
      "lab_result_data": {
        "lab_result_id": "1177081",
        "lab_result_status": "passed",
        "lab_result_detail": "https://files.cultivera.com/https://files.cultivera.com/435553542D57533130383235/Interop/25/12/ANYMMT8C9EMENBT3/C10825_qa21VGX2V6.json",
        "coa": "https://files.cultivera.com/435553542D57533130383235/Coas/25/04/16/4PGF2XJZ2C7FQE7S/18800227120782398.pdf",
        "potency": [
          {"type": "cbd", "value": 0, "unit": "pct"},
          {"type": "thc", "value": 2.6, "unit": "pct"},
          {"type": "thca", "value": 80, "unit": "pct"},
          {"type": "cbda", "value": 0, "unit": "pct"},
          {"type": "total-cannabinoids", "value": 82.6, "unit": "pct"}
        ],
        "lab_result_list": [
          {
            "coa": "https://files.cultivera.com/435553542D57533130383235/Coas/25/04/16/4PGF2XJZ2C7FQE7S/18800227120782398.pdf",
            "lab_result_id": "1177081",
            "lab_result_status": "passed",
            "lab_result_link": "https://files.cultivera.com/https://files.cultivera.com/435553542D57533130383235/Interop/25/12/ANYMMT8C9EMENBT3/C10825_qa21VGX2V6.json",
            "coa_release_date": None,
            "coa_amended_date": None,
            "coa_expire_date": None
          }
        ]
      },
      "inventory_category": "IntermediateProduct",
      "inventory_type": "Concentrate for Inhalation",
      "strain_name": "Grape Gasoline",
      "product_sku": None
    }
  ]
}

if __name__ == "__main__":
    products = extract_products_from_manifest(manifest_json)
    print("Extracted Products:")
    for i, product in enumerate(products, 1):
        print(f"\nProduct {i}:")
        for k, v in product.items():
            print(f"  {k}: {v}") 