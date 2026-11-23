#!/usr/bin/env python3
"""
Generate hierarchical zoomable dashboard from existing data
"""
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from modernizeiq.ui.hierarchical_dashboard import render_hierarchical_dashboard

def main():
    # Load existing data
    data_file = Path('output/core_banking_deposit_data.json')
    if not data_file.exists():
        print(f"Error: {data_file} not found")
        return 1
    
    with open(data_file, 'r') as f:
        report_data = json.load(f)
    
    # Generate hierarchical dashboard
    print("Generating hierarchical zoomable dashboard...")
    html = render_hierarchical_dashboard(report_data)
    
    # Save to output
    output_file = Path('output/hierarchical_explorer.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated: {output_file}")
    print(f"   Open in browser: file:///{output_file.absolute()}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
