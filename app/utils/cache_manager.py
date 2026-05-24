import os
import json
from datetime import datetime, timedelta
from typing import List, Optional

class CacheManager:
    def __init__(self, cache_file="storage/downloaded_papers_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def cleanup_old_cache(self, days_old: int = 30):
        """Remove cache entries older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        removed = 0
        
        for paper_id, info in list(self.cache.items()):
            downloaded_at = datetime.fromisoformat(info['downloaded_at'])
            if downloaded_at < cutoff_date:
                # Delete the file
                if os.path.exists(info['local_path']):
                    os.remove(info['local_path'])
                del self.cache[paper_id]
                removed += 1
        
        self._save_cache()
        return removed
    
    def get_cache_summary(self) -> dict:
        """Get detailed cache summary"""
        total_size = 0
        for info in self.cache.values():
            if os.path.exists(info['local_path']):
                total_size += os.path.getsize(info['local_path'])
        
        return {
            'total_papers': len(self.cache),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'oldest_paper': min([info['downloaded_at'] for info in self.cache.values()]) if self.cache else None,
            'newest_paper': max([info['downloaded_at'] for info in self.cache.values()]) if self.cache else None
        }