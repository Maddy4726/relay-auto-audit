import os
import glob
from src.extractor import extract_text
from src.parser import extract_data
from src.audit import run_audit

# Find all PDF files in the data folder
pdf_files = glob.glob("data/*.pdf")

if not pdf_files:
    print("No PDF files found in data folder")
else:
    for pdf_path in sorted(pdf_files):
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(pdf_path)}")
        print("=" * 60)

        try:
            text = extract_text(pdf_path)

            print("\n--- RAW TEXT START ---\n")
            print(text[:1000])  # print first 1000 chars
            print("\n--- RAW TEXT END ---\n")

            data = extract_data(text)
            print("\nExtracted Data:", data)

            issues = run_audit(data)

            print("\n=== AUDIT RESULT ===\n")

            if not issues:
                print("✓ PASS")
            else:
                for i in issues:
                    print(f"✗ {i}")
        except Exception as e:
            print(f"ERROR processing {pdf_path}: {str(e)}")

        print()
