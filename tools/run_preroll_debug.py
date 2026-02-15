#!/usr/bin/env python3
"""Debug runner for preroll tag generation."""
from pprint import pprint

from src.core.generation import preroll_tag_generator as ptg


class DummyCache:
    def __init__(self):
        self._d = {}

    def set(self, key, val, timeout=None):
        self._d[key] = val

    def get(self, key, default=None):
        return self._d.get(key, default)


def run():
    # Replace module session with a simple dict to avoid Flask context requirements
    ptg.session = {}

    cache = DummyCache()

    records = [
        {
            'Product Name*': 'Acme Pre-Roll 0.5g x 7 Pack by Acme - Variety',
            'Description': 'Acme Pre-Roll 0.5g x 7 Pack',
            'Product Brand': 'Acme',
            'Vendor': 'Acme Vendor LLC',
            'Price': '12.00',
            'CombinedWeight': '0.5g'
        },
        {
            'Product Name*': 'Acme Pre-Roll 0.5g x 7 Pack by Acme - Variety 2',
            'Description': 'Acme Pre-Roll 0.5g x 7 Pack',
            'Product Brand': 'Acme',
            'Vendor': 'Acme Vendor LLC',
            'Price': '12.00',
            'CombinedWeight': '0.5g'
        },
        {
            'Product Name*': 'Other Brand Infused Pre Roll 1g by OtherCo',
            'Description': 'Infused Pre-Roll 1g',
            'Product Brand': 'OtherCo',
            'Vendor': 'OtherCo',
            'Price': '$20',
            'CombinedWeight': '1g'
        }
    ]

    grouped = ptg.generate_preroll_tags(records, cache)
    print('\n--- GROUPED REPRESENTATIVES ---')
    pprint(grouped)
    print('\n--- SESSION KEYS ---')
    pprint(ptg.session)
    print('\n--- CACHE KEYS ---')
    pprint(cache._d)


if __name__ == '__main__':
    run()
