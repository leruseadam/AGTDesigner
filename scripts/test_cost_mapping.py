from src.core.data.json_matcher import JSONMatcher
import pandas as pd

class FakeExcelProcessor:
    def __init__(self):
        # Simulate an Excel upload with a Cost column already present
        self.df = pd.DataFrame(columns=['Product Name*', 'Price', 'Weight*', 'Cost'])

# Create fake matched products with cost fields
matched_products = [
    {
        'Product Name*': 'Blueberry Mini Buds',
        'Price': '$70',
        'Weight*': '14 g',
        'cost': '$15'
    },
    {
        'Product Name*': 'Gelato 33',
        'Price': '$75',
        'Weight*': '14 g',
        'cost': '$16.50'
    }
]

# Instantiate matcher with a None excel_processor (we'll pass the fake one to integrate)
matcher = JSONMatcher(None)
excel = FakeExcelProcessor()

success = matcher.integrate_with_excel_system(excel, matched_products)
print('Integration success:', success)
print(excel.df.to_dict(orient='records'))
