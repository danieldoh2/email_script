import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
INPUT_FILE = "your_file.xlsx"            # <- path to your workbook
OUTPUT_FILE = "your_file_updated.xlsx"   # saved as a new file so the original is untouched
EMAILS_SHEET = "SFA Emails"
LIBRARY_SHEET = "Library"


def norm(value):
    """Normalize text for matching: strip whitespace, lowercase, treat NaN as ''."""
    if pd.isna(value):
        return ""
    return str(value).strip().casefold()


def main():
    # -----------------------------------------------------------------------
    # 1. Open the workbook. Read ALL sheets so the others are preserved on save.
    # -----------------------------------------------------------------------
    all_sheets = pd.read_excel(INPUT_FILE, sheet_name=None)
    emails = all_sheets[EMAILS_SHEET]
    library = all_sheets[LIBRARY_SHEET]

    # -----------------------------------------------------------------------
    # 2. Subset: Status == 'Match' AND yes_flag includes 'y'
    # -----------------------------------------------------------------------
    status_ok = emails["Status"].astype(str).str.strip().str.casefold() == "match"
    flag_ok = emails["yes_flag"].astype(str).str.contains("y", case=False, na=False)
    filtered_emails = emails[status_ok & flag_ok].copy()
    print(f"{len(filtered_emails)} of {len(emails)} email records passed the filter.")

    # -----------------------------------------------------------------------
    # 3. Prepare the Library for matching
    #    - normalized helper columns (dropped again before saving)
    #    - a dict of institution -> row labels, so we only scan a small slice
    # -----------------------------------------------------------------------
    library["_inst"] = library["InstitutionName"].map(norm)
    library["_first"] = library["StandardInvestigatorFirstName"].map(norm)
    library["_last"] = library["StandardInvestigatorLastName"].map(norm)

    # Make sure the target column exists and can hold text
    if "Email Match from TF" not in library.columns:
        library["Email Match from TF"] = pd.NA
    library["Email Match from TF"] = library["Email Match from TF"].astype(object)

    inst_groups = library.groupby("_inst").groups  # {institution: Index of row labels}

    # -----------------------------------------------------------------------
    # 4. Loop through filtered_emails and fill in matches
    # -----------------------------------------------------------------------
    matched_records = 0
    unmatched_records = 0
    library_rows_filled = 0

    for _, row in filtered_emails.iterrows():
        email_address = row["Email Address"]
        first_name = norm(row["First Name"])
        last_name = norm(row["Last Name"])
        institution = norm(row["match_institution"])

        # Step A: narrow the Library down to the same institution
        if institution not in inst_groups:
            unmatched_records += 1
            continue
        same_institution = library.loc[inst_groups[institution]]

        # Step B: within that institution, match first AND last name
        hits = same_institution[
            (same_institution["_first"] == first_name)
            & (same_institution["_last"] == last_name)
        ]

        if hits.empty:
            unmatched_records += 1
            continue

        # Step C: write the email into every matching Library record
        library.loc[hits.index, "Email Match from TF"] = email_address
        matched_records += 1
        library_rows_filled += len(hits)

    print(f"Emails matched:   {matched_records}")
    print(f"Emails unmatched: {unmatched_records}")
    print(f"Library rows filled: {library_rows_filled}")

    # -----------------------------------------------------------------------
    # 5. Save results (drop helper columns first)
    # -----------------------------------------------------------------------
    library = library.drop(columns=["_inst", "_first", "_last"])
    all_sheets[LIBRARY_SHEET] = library

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
