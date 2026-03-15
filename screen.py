import requests
import random
import time 

REQUEST_TIMEOUT = 30

def get_with_backoff_jitter(
    url,
    params=None,
    headers=None,
    max_retries=5,
    base_delay=1,
    timeout=REQUEST_TIMEOUT,
):
    for attempt in range(max_retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)

            if r.status_code in [429, 500, 502, 503, 504]:
                raise requests.exceptions.HTTPError(f"{r.status_code}")

            r.raise_for_status()
            return r.json()

        except Exception as e:
            wait = random.uniform(0, base_delay * (2 ** attempt))
            print(f"Retrying in {wait:.2f}s due to {e}")
            time.sleep(wait)

    raise RuntimeError("Failed after retries")