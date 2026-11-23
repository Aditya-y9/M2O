"""
Simple dashboard regeneration script that works around torch dependency issues.
Uses the tagged core_banking_deposit_data.json file directly.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modernizeiq.ui.enhanced_dashboard import render_enhanced_dashboard

def main():
    # Load the tagged sample data
    data_path = Path(__file__).parent / "output" / "core_banking_deposit_data.json"
    
    print(f"Loading data from: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    print("Generating dashboard HTML...")
    html_content = render_enhanced_dashboard(report_data)
    
    # Save to output
    output_path = Path(__file__).parent / "output" / "core_banking_deposit_dashboard_desloped.html"
    print(f"Writing to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Dashboard regenerated successfully!")
    print(f"Open in browser: {output_path}")

if __name__ == "__main__":
    main()
