import sys
from pathlib import Path

# Allow running from project root without installing as a package
sys.path.insert(0, str(Path(__file__).parent))

from etl.extract  import load_data
from etl.transform import transform
from etl.validate  import validate
from etl.load      import save_output
from config        import EXTRACTION_FILE, CUSTOMER_FILE, OUTPUT_FILE


def run(
    extraction_path=EXTRACTION_FILE,
    customer_path=CUSTOMER_FILE,
    output_path=OUTPUT_FILE,
    include_validation: bool = False,
):
    print("── Extract ─────────────────────────────────────────")
    raw_extraction_data, customer_rm_list = load_data(extraction_path, customer_path)
    print(f"  Extraction rows : {len(raw_extraction_data)}")
    print(f"  Customer rows   : {len(customer_rm_list)}")

    print("── Transform ───────────────────────────────────────")
    df = transform(raw_extraction_data, customer_rm_list)
    print(f"  Output rows     : {len(df)}")

    print("── Validate ────────────────────────────────────────")
    df, issues = validate(df)
    ok_count    = (df["Validation"] == "OK").sum()
    issue_count = (df["Validation"] == "ISSUE").sum()
    print(f"  OK              : {ok_count}")
    print(f"  Issues          : {issue_count}")

    if issues:
        print("\n  First 10 issues:")
        for issue in issues[:10]:
            print(f"    Row {issue['row']:>5} | {issue['column']:<45} | {issue['detail']}")

    print("── Load ────────────────────────────────────────────")
    saved = save_output(df, output_path, include_validation=include_validation)
    print(f"  Saved to: {saved}")
    print("────────────────────────────────────────────────────")


if __name__ == "__main__":
    run()
