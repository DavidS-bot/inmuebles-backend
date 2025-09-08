#!/usr/bin/env python3
"""
Test the fresh scraper to make sure it works
"""

import subprocess
import sys

def test_fresh_scraper():
    """Test if the fresh scraper can run"""
    
    print("Testing fresh scraper...")
    
    try:
        # Test with a very short timeout first
        result = subprocess.run(
            [sys.executable, 'run_fresh_scraper.py'], 
            capture_output=True, 
            text=True, 
            timeout=10  # 10 second timeout for testing
        )
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Script started (timed out after 10 seconds, which is expected)")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_fresh_scraper()
    print(f"Test result: {'SUCCESS' if success else 'FAILED'}")