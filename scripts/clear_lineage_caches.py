#!/usr/bin/env python3
"""Maintenance script to clear lineage-related caches.

Usage: python scripts/clear_lineage_caches.py
"""
import os
import logging
import shutil

logging.basicConfig(level=logging.INFO)

def main():
    # Import application to get cache and paths
    try:
        # Ensure project root is on sys.path so `import app` works when run as script
        import sys
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        import app as main_app
    except Exception as e:
        logging.error(f"Could not import app: {e}")
        return 1

    # 1) Clear product_database lineage TTL cache
    try:
        from src.core.data.product_database import clear_lineage_cache
        clear_lineage_cache(None)
        logging.info("Cleared product_database lineage cache")
    except Exception as e:
        logging.warning(f"Could not clear product_database lineage cache: {e}")

    # 2) Clear fast_generation caches if available
    try:
        from src.core.generation.fast_generation import clear_all_caches
        clear_all_caches()
        logging.info("Cleared fast_generation caches")
    except Exception as e:
        logging.warning(f"Could not clear fast_generation caches: {e}")

    # 3) Clear Flask app cache (file system cache)
    try:
        if hasattr(main_app, 'cache') and main_app.cache:
            try:
                main_app.cache.clear()
                logging.info("Called app.cache.clear()")
            except Exception:
                logging.warning("app.cache.clear() not supported, falling back to cache dir prune")

        # Attempt to remove cache files matching known prefixes in CACHE_DIR
        cache_dir = getattr(main_app, 'CACHE_DIR', None) or getattr(main_app, 'UPLOADS_DIR', None)
        if cache_dir and os.path.isdir(cache_dir):
            # Flask-Caching FileSystemCache writes files under CACHE_DIR; remove pattern matches
            for root, dirs, files in os.walk(cache_dir):
                for fname in files:
                    if 'preroll_group' in fname or 'preroll' in fname or 'template' in fname:
                        path = os.path.join(root, fname)
                        try:
                            os.remove(path)
                            logging.info(f"Removed cache file: {path}")
                        except Exception as e:
                            logging.warning(f"Could not remove cache file {path}: {e}")
        else:
            logging.info("No CACHE_DIR found to prune file cache")
    except Exception as e:
        logging.warning(f"Error while pruning file cache: {e}")

    logging.info("Cache clearing complete")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
