import json
from src.core.constants import CLASSIC_TYPES


def enforce(tags):
    for tag in tags:
        product_type = (tag.get('Product Type*') or tag.get('ProductType') or '').lower().strip()
        if not product_type:
            continue
        is_classic = product_type in [ct.lower() for ct in CLASSIC_TYPES] or any(ct.lower() in product_type for ct in CLASSIC_TYPES)
        if is_classic:
            continue
        product_strain = (tag.get('Product Strain','') or tag.get('ProductStrain','') or tag.get('Product Strain*','')).strip()
        if product_strain:
            has_cbd = any(ind in product_strain.upper() for ind in ['CBD','HIGH CBD','CBG','CBN','CBC'])
            correct_lineage='CBD' if has_cbd else 'MIXED'
        else:
            correct_lineage='MIXED'
        current_lineage = tag.get('Lineage') or tag.get('currentLineage') or tag.get('canonical_lineage') or ''
        cur=current_lineage.strip().upper()
        valid=['MIXED','CBD','CBD_BLEND','THC']
        if cur not in valid:
            tag['Lineage']=correct_lineage
            tag['Lineage*']=correct_lineage
            tag['currentLineage']=correct_lineage
            tag['canonical_lineage']=correct_lineage
            tag['lineage']=correct_lineage.lower()
            product_brand_candidate = (tag.get('Product Brand') or tag.get('ProductBrand') or tag.get('productBrand') or tag.get('Brand') or tag.get('brand') or '').strip()
            if product_brand_candidate:
                brand_upper = product_brand_candidate.upper()
                tag['ProductBrand']=brand_upper
                tag['Product Brand']=brand_upper
                tag['productBrand']=brand_upper
                tag['ProductBrand_Center']=brand_upper
    print(json.dumps(tags,indent=2))


# Test cases
tags=[
 {'Product Name*':'Choco','Product Type*':'Edible','Product Brand':'Ceres','Lineage':'SATIVA'},
 {'Product Name*':'Gummy','Product Type*':'Edible','Vendor':'Acme','Lineage':'INDICA'},
 {'Product Name*':'Bud1','Product Type*':'Flower','Product Brand':'GrowCo','Lineage':'SATIVA'}
]
print('--- BEFORE ---')
print(json.dumps(tags,indent=2))
print('\n--- AFTER ENFORCEMENT ---')
enforce(tags)
