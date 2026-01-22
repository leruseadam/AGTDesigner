import sys
sys.path.insert(0, '/Users/adamcordova/Desktop/labelMaker_ QR copy final')
from src.core.generation.preroll_tag_generator import generate_preroll_tags

class SimpleCache:
    def __init__(self):
        self.d={}
    def set(self,k,v,timeout=None):
        self.d[k]=v
    def get(self,k):
        return self.d.get(k)

cache=SimpleCache()
records=[
    {'Product Name*':'PR1 by BrandA - 1g','Description':'Pre-Roll 1g','Product Brand':'BrandA','Vendor':'Vendor1','ProductName':'PR1 by BrandA - 1g'},
    {'Product Name*':'PR2 by BrandB - 1g','Description':'Pre-Roll 1g','Product Brand':'BrandB','Vendor':'Vendor2','ProductName':'PR2 by BrandB - 1g'},
    {'Product Name*':'PR3 by BrandA - 1g','Description':'Pre-Roll 1g','Product Brand':'BrandA','Vendor':'Vendor1','ProductName':'PR3 by BrandA - 1g'},
    {'Product Name*':'Regular Flower','Description':'Flower','Product Brand':'BrandA','Vendor':'Vendor1','ProductName':'Regular Flower'},
]

out = generate_preroll_tags(records, cache)
print('Generated groups:', len(out))
for r in out:
    print('Group:', r.get('Product Name*'), 'Vendor:', r.get('Vendor'), 'Brand:', r.get('Product Brand'))
