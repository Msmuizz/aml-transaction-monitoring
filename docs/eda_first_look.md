# EDA: First Look at HI-Small

**Date:** 2026-10-19
**Data:** AMLworld HI-Small (`HI-Small_Trans.csv`, `HI-Small_Patterns.txt`, `HI-Small_accounts.csv`)
**Method:** Command-line inspection (`head`, `wc -l`, `awk`) of the raw files. No cleaning applied yet.

---

### Finding 1: The file has 5,078,345 transactions
- **Evidence:** `wc -l HI-Small_Trans.csv` returns 5,078,346 lines; the first line is the header.
- **Implication:** Any row-count check must subtract the header, or reconciliation will be off by one.
- **Action:** Use 5,078,345 as the expected row count when validating the bronze table.

### Finding 2: Laundering is extremely rare (0.10%)
- **Evidence:** `awk -F, 'NR>1 && $11==1' HI-Small_Trans.csv | wc -l` returns 5,177, which is 0.10% of all transactions (about 1 in 981).
- **Implication (measuring):** A model that predicts "not laundering" for every transaction scores 99.90% accuracy while catching zero laundering, so accuracy cannot tell a useful model from a useless one.
- **Implication (learning):** With only 5,177 positive examples, the model has few laundering cases to learn from, which makes learning their patterns harder.
- **Action:** Evaluate with recall at a fixed alert budget and PR-AUC (Phase 2). Handle imbalance with class weights and threshold tuning (Phase 3).

### Finding 3: Bank codes contain leading zeros
- **Evidence:** `head -5` shows bank codes like `010`, `03208`, `001`.
- **Implication:** If read as numbers, `010` becomes `10` and `001` becomes `1`, silently corrupting the identifiers. Bank codes are labels, not quantities.
- **Action:** Read `From Bank` and `To Bank` as strings in an explicit bronze schema (no `inferSchema`).

### Finding 4: Two columns are both named `Account`
- **Evidence:** The header contains `Account` twice: once after `From Bank`, once after `To Bank`.
- **Implication:** Spark and pandas can't handle two columns with the same name cleanly. The first `Account` is the sender's account and the second is the receiver's, so their meaning would be lost.
- **Action:** Rename them to `from_account` and `to_account` in the bronze step.

### Finding 5: Self-transfers are common (11.7%)
- **Evidence:** `awk -F, 'NR>1 && $3==$5' HI-Small_Trans.csv | wc -l` returns 595,391 (11.7%). Sample rows show these are mostly `Reinvestment`.
- **Implication:** In 11.7% of transactions the sender and receiver account have the same value (money moving within one account). In the other 88% they differ, so the two Account columns are different fields, not duplicates.
- **Action:** Keep both columns. Consider an `is_self_transfer` flag as a feature in Phase 3.

### Finding 6: Cross-currency transactions exist (1.4%)
- **Evidence:** `awk -F, 'NR>1 && $7!=$9' HI-Small_Trans.csv | wc -l` returns 72,170 (1.4%).
- **Implication:** When the payment and receiving currencies differ, `Amount Paid` and `Amount Received` differ too, so the two amount columns are not duplicates. Amounts in different currencies also can't be compared directly (100 Yen is not 100 US Dollars).
- **Action:** Keep both amount and currency columns in bronze. Decide in silver how to compare amounts across currencies (e.g. convert to one currency), and record it as a decision record.

### Finding 7: Timestamps are unsorted and have no seconds
- **Evidence:** In `head -5`, row 1 is `2022/09/01 00:20` but row 3 is `2022/09/01 00:00`. The format is `yyyy/MM/dd HH:mm`.
- **Implication:** If I assume the file is in time order, a time-based split ("first 80% of rows = train") would mix future transactions into training, which is data leakage. Without seconds, several transactions can share the exact same timestamp.
- **Action:** Parse timestamps with the exact format `yyyy/MM/dd HH:mm`. Never rely on file order; split and sort by the parsed timestamp explicitly.

### Finding 8: The Patterns file groups laundering by typology
- **Evidence:** Blocks start with `BEGIN LAUNDERING ATTEMPT - <TYPE>` and end with `END LAUNDERING ATTEMPT - <TYPE>`. The first block is a FAN-OUT where account `800737690` sends to 16 different accounts over 4 days.
- **Implication:** A fan-out is when one account quickly sends money out to many different accounts, spreading the funds to make them harder to trace. The typology labels let me measure which laundering types my model catches and misses.
- **Action:** Use the Patterns file for per-typology error analysis in Phase 3.

## Open questions (to investigate later)
- What other typologies appear in the Patterns file besides FAN-OUT and CYCLE?
- Are there transactions with very small amounts (e.g. `0.01`)? Are they meaningful or noise?