import pandas as pd


def normalize(s):
    """Lowercase + strip a string, safely handling NaN/None."""
    if pd.isna(s):
        return ""
    return str(s).strip().lower()


def match_emails_to_library(Emails: pd.DataFrame, Library: pd.DataFrame) -> pd.DataFrame:
    """
    Loops through every record in Emails, checks whether the
    (First Name, Last Name) pair has a match in Library's
    (StandardInvestigatorFirstName, StandardInvestigatorLastName).

    For efficiency, Library is pre-indexed by normalized last name
    into a dict of sets of normalized first names. This means for
    each Emails record we:
      1. Normalize the last name and do an O(1) dict lookup to see
         if that last name exists in Library at all.
      2. Only if it does, check whether the normalized first name
         is in the set of first names associated with that last name.

    This avoids re-scanning the entire Library dataframe for every
    single row in Emails, while preserving the "check last name
    first, then first name" logic you described.

    Returns a new dataframe (Modded_Emails) — a copy of Emails with
    statuscheck set to "Match" wherever a match was found.
    """

    # --- Build lookup index from Library: last_name -> set(first_names) ---
    last_to_firsts = {}
    for last, first in zip(
        Library["StandardInvestigatorLastName"],
        Library["StandardInvestigatorFirstName"],
    ):
        norm_last = normalize(last)
        norm_first = normalize(first)
        if norm_last == "":
            continue
        last_to_firsts.setdefault(norm_last, set()).add(norm_first)

    # --- Work on a copy so we don't mutate the original Emails df ---
    Modded_Emails = Emails.copy()

    # --- Loop through every record in Emails ---
    for idx, row in Modded_Emails.iterrows():
        last_name = normalize(row["Last Name"])
        first_name = normalize(row["First Name"])

        # Step 1: check if last name exists in Library at all
        if last_name in last_to_firsts:
            # Step 2: only then check first name
            if first_name in last_to_firsts[last_name]:
                Modded_Emails.at[idx, "statuscheck"] = "Match"

    return Modded_Emails


# --- Example usage ---
# Modded_Emails = match_emails_to_library(Emails, Library)
