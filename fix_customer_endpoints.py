import os
import glob

def fix_customer_endpoints_safe():
    """Fix customer endpoint URLs in test files (handles encoding issues)"""
    test_files = glob.glob('tests/test_*.py')
    
    replacements = {
        # Customer endpoint fixes
        "'/customer/'": "'/customers/'",
        "'/customer/login'": "'/customers/login'",
        "'/customer/register'": "'/customers/'",
        "'/customer/profile'": "'/customers/profile'",
        "'/customer/1'": "'/customers/1'",
        "'/customer/my-tickets'": "'/customers/my-tickets'",
        
        # URL pattern fixes
        '"/customer/"': '"/customers/"',
        '"/customer/login"': '"/customers/login"',
        '"/customer/register"': '"/customers/"',
        '"/customer/profile"': '"/customers/profile"',
        '"/customer/1"': '"/customers/1"',
        '"/customer/my-tickets"': '"/customers/my-tickets"',
    }
    
    for test_file in test_files:
        print(f"Checking {test_file}...")
        
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(test_file, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"  - Could not read {test_file} with any encoding, skipping")
                continue
            
            changes_made = False
            for old, new in replacements.items():
                if old in content:
                    content = content.replace(old, new)
                    print(f"  - Fixed: {old} -> {new}")
                    changes_made = True
            
            if changes_made:
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except Exception as e:
            print(f"  - Error processing {test_file}: {e}")
            continue

if __name__ == '__main__':
    fix_customer_endpoints_safe()
    print("✓ Customer endpoints fixed!")