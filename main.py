from src.extractor import extract_text
from src.parser import extract_data
from src.audit import run_audit

pdf_path = "data/sample.pdf"

text = extract_text(pdf_path)

print("\n--- RAW TEXT START ---\n")
print(text[:1000])   # print first 1000 chars
print("\n--- RAW TEXT END ---\n")

data = extract_data(text)
print("\nExtracted Data:", data)

issues = run_audit(data)

print("\n=== AUDIT RESULT ===\n")

if not issues:
    print("PASS")
else:
    for i in issues:
        print(i)