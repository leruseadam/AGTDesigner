import time
import sys
sys.path.insert(0, '/Users/adamcordova/Desktop/labelMaker_ QR copy final')

from src.core.generation.fast_generation import FastGenerationEngine, optimize_records_for_generation

# Minimal stub TemplateProcessor with process_records returning a simple docx Document
class StubTemplateProcessor:
    def __init__(self, template_type='horizontal'):
        self.template_type = template_type
        from docx import Document
        self._doc_class = Document
    def process_records(self, records):
        """Create a trivial Document with one paragraph per record to simulate work."""
        doc = self._doc_class()
        for r in records:
            doc.add_paragraph(str(r.get('ProductName') or r.get('Product Name*', '')))
        return doc


def make_record(i):
    return {
        'Product Name*': f'Product {i}',
        'ProductName': f'Product {i}',
        'ProductType': 'pre-roll' if i % 3 == 0 else 'flower',
        'Lineage': 'HYBRID' if i % 2 == 0 else 'SATIVA',
        'ProductBrand': 'BrandX',
        'Price': '$10.00',
        'DOH': 'YES',
        'Weight*': '1',
        'Units': 'g',
        'Description': f'Description {i}',
    }


def run_benchmark(num_records=500, iterations=3):
    records = [make_record(i) for i in range(num_records)]
    processor = StubTemplateProcessor()
    engine = FastGenerationEngine(processor)
    optimized = optimize_records_for_generation(records)

    # Warmup
    start = time.time()
    _ = engine.generate_with_cache(optimized, 'horizontal', 1.0)
    warmup = time.time() - start
    print(f'Warmup generation time: {warmup:.3f}s')

    times = []
    for it in range(iterations):
        t0 = time.time()
        _ = engine.generate_with_cache(optimized, 'horizontal', 1.0)
        t = time.time() - t0
        print(f'Iteration {it+1}: {t:.3f}s')
        times.append(t)

    avg = sum(times) / len(times)
    print(f'Average generation time over {iterations} runs: {avg:.3f}s')

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--n', type=int, default=500)
    p.add_argument('--iters', type=int, default=3)
    args = p.parse_args()
    run_benchmark(args.n, args.iters)
