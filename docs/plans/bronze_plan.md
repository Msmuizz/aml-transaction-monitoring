# Bronze Step Plan

## 1. Purpose 
Convert the raw transactions CSV into Parquet with clear column names and correct types, without changing the content. Cleaning is left for silver.

## 2. Input. What’s the path of the transactions file inside the project?
- File: `data/raw/HI-Small_Trans.csv`
- Size: 5,078,345 transactions, 11 columns
- Only the transactions file for now. Patterns and accounts files are handled later.

## 3. Output
- Folder: `data/bronze/transactions/`
- Format: Parquet
- Why Parquet instead of CSV:
  1. Saves column types inside the file, so `010` stays a string in every later step (protects Finding 3).
  2. Faster for Spark to read, because it can read only the columns it needs.
  3. Smaller on disk, because it compresses data automatically.

## 4. Schema
| Original column | New name | Type | Why this type |
|---|---|---|---|
| Timestamp | timestamp | string | Kept as original text in bronze; parsed in silver (Finding 7) |
| From Bank | from_bank | string | Identifier with leading zeros (Finding 3) |
| Account (1st) | from_account | string | Sender's account ID; contains letters (Finding 4) |
| To Bank | to_bank | string | Identifier with leading zeros (Finding 3) |
| Account (2nd) | to_account | string | Receiver's account ID (Finding 4) |
| Amount Received | amount_received | double | Quantity with decimals |
| Receiving Currency | receiving_currency | string | Category label |
| Amount Paid | amount_paid | double | Quantity with decimals |
| Payment Currency | payment_currency | string | Category label |
| Payment Format | payment_format | string | Category label |
| Is Laundering | is_laundering | integer | 0/1 target; sum = count, mean = rate |

## 5. What bronze does NOT do
Bronze changes names and storage only. It does NOT change values or remove rows. Left for silver:
- Parsing `timestamp` text into a real date-time (Finding 7, DR-002)
- Removing duplicate transactions
- Converting amounts into one currency (Finding 6)
- Removing or fixing rows that look wrong

## 6. Checks (how I know it worked)

### Check A: Row count
Raw: 5,078,345 rows (5,078,346 lines minus 1 header). Bronze must have exactly 5,078,345 rows.

### Check B: Laundering count
Raw: 5,177 rows with is_laundering = 1 (0.102%). Bronze must have exactly 5,177.
This matters most because laundering is only 0.10% of rows, so every missing positive row reduces the model's recall.

### Check C: Column count
Raw: 11 columns. Bronze must have exactly 11 columns.

### Check D: Leading zeros
Bank code 010 must still be 010 in bronze. If the schema failed, it would become 10.

## 7. Open questions
- A. How do I write the Spark code that applies the schema from section 4?
- B. How do I run Checks A–D automatically after bronze runs, instead of by hand?
- C. When and how should I make bronze versions of the patterns and accounts files?
- D. How do I confirm that Parquet really saved the column types (e.g. `from_bank` is a string)?
