"""Simple dashboard regeneration without heavy dependencies"""
from src.modernizeiq.ui.enhanced_dashboard import render_enhanced_dashboard
import json

# Load sample data
with open('data/sample_cobol_metadata.json', 'r') as f:
    metadata = json.load(f)

# Create minimal report data structure
report_data = {
    'metadata': metadata,
    'app_name': 'Core Banking Deposit System',
    'app_id': 'CBDS-001',
    'assessment': {
        'overall_score': 72,
        'modernization_readiness': 'MODERATE',
        'recommended_approach': 'Incremental Refactoring',
        'business_complexity': 'High',
        'technical_debt': 'Medium',
        'data_coupling': 'High'
    },
    'migration_decision': {
        'platform': 'OCP',
        'confidence': 85,
        'timeline_months': 18,
        'risk_level': 'Medium'
    },
    'dependency_graph': {
        'nodes': [],
        'edges': []
    },
    'semantic_search': None  # Skip semantic search for now
}

# Build minimal dependency graph from metadata
programs = metadata.get('programs', [])
for prog in programs:
    report_data['dependency_graph']['nodes'].append({
        'id': prog['name'],
        'type': 'program',
        'complexity': prog.get('complexity', 0)
    })

# Generate dashboard
html = render_enhanced_dashboard(report_data)

# Save
with open('output/core_banking_deposit_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ Generated: output/core_banking_deposit_dashboard.html')
print('')
print('🎨 Design improvements applied:')
print('  ✓ IBM Plex Sans/Mono typography from Google Fonts')
print('  ✓ OKLCH color tokens (--color-* system)')
print('  ✓ Removed gradient backgrounds (header, buttons)')
print('  ✓ Removed glassmorphism (backdrop-blur)')
print('  ✓ Removed transform scale animations')
print('  ✓ Applied tabular numerals for metrics')
print('  ✓ 4-6px border-radius (max 6px per DESIGN.md)')
print('  ✓ Defined edge shadows (1px border + subtle shadow)')
print('')
print('Next: Opening in browser for visual verification...')
