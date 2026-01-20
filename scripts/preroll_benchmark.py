import time
import requests

BASE = 'http://127.0.0.1:5000'

def main():
    s = requests.Session()
    print('Fetching available tags...')
    r = s.get(BASE + '/api/available-tags', params={'nocache':'1','prefer_db':'1'})
    if r.status_code != 200:
        print('Failed to fetch available tags:', r.status_code, r.text)
        return
    data = r.json()
    tags = data.get('tags', [])
    print(f'Got {len(tags)} tags from server (source: {data.get("source")})')
    if not tags:
        print('No tags to test with')
        return

    # Choose a preroll-heavy sample: take first 60 tags (adjustable)
    sample = tags[:60]

    payload = {
        'template_type': 'preroll',
        'selected_tags': sample,
        'scale_factor': 1.0
    }

    print(f'Posting generate request with {len(sample)} tags...')
    start = time.time()
    gr = s.post(BASE + '/api/generate', json=payload, timeout=120)
    elapsed = time.time() - start
    print(f'Generate status: {gr.status_code} in {elapsed:.2f}s')
    try:
        print('Response JSON keys:', list(gr.json().keys()))
    except Exception:
        print('Response text length:', len(gr.text))

if __name__ == '__main__':
    main()
