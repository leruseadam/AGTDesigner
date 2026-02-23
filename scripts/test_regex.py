import re
s = 'Apple Mac Live Resin Disposable Vape by Dabstract - 1g'
print('string:', s)
print('lower:', s.lower())
print('disposable regex:', bool(re.search(r"\b(aio|all[- ]?in[- ]?one|disposable)\b", s.lower())))
print('cartridge regex:', bool(re.search(r"\b(cartridge|cart|510|vape cartridge|vape pen|pod)\b", s.lower())))
