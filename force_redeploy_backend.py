#!/usr/bin/env python3
"""Force redeploy backend by making a dummy change"""

import os
import subprocess
import time
from datetime import datetime

def force_redeploy():
    print("FORCING BACKEND REDEPLOY")
    print("=" * 30)
    
    # Change to backend directory
    os.chdir("inmuebles-backend")
    
    # Add a timestamp to force deployment
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Modify the main.py file to force a change
    main_py_path = "app/main.py"
    
    # Read current content
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add timestamp comment
    new_content = content.replace(
        "# Updated with classification_rules and rental_contracts endpoints - Aug 26",
        f"# Force deploy {timestamp} - classification_rules and rental_contracts ready"
    )
    
    # Write back
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Added timestamp: {timestamp}")
    
    # Git operations
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run([
        "git", "commit", "-m", 
        f"Force redeploy {timestamp}: Ensure classification_rules and rental_contracts work\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
    ], check=True)
    subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
    
    print("Force push completed!")
    print("Waiting 60 seconds for deployment...")
    time.sleep(60)
    
    # Test endpoints
    print("Testing endpoints after deployment...")
    os.chdir("..")  # Back to backend root
    subprocess.run(["python", "verify_production_state.py"])

if __name__ == "__main__":
    force_redeploy()