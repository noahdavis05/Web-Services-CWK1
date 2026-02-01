# Datasets
## Information
- Datasets for train fares, coach fares, and bus fares are in their own directories.
- The actual data is ignored from the repo in the `.gitignore` as is veyr large.
- There are my scripts used to extract the data in each subdir.

## Train Fares Dataset
The dataset contains 24 files. the `.FFL` file contains the actual train journeys and their given prices. The data is in this format:

| Field Name | Chars | Example Value | Description |
|---|---|---|---|
| Record Identity | 1-2 | RF | Identifies this as a Flow Record. |
| Origin NLC | 3-6 | 0041 | The NLC code for the starting station. |
| Destination NLC | 7-10 | 0258 | The NLC code for the end station. |
| Route Code | 11-15 | 01000 | The specific route (e.g., "Any Permitted"). |
| Status Code | 16-18 | 000 | Usually 000 (standard). |
| Usage Indicator | 19-20 | AS | Applicable Single (or AR for Return). |
| End Date | 21-28 | 31122999 | When this fare expires (effectively "forever"). |
| Start Date | 29-36 | 02032025 | Valid from March 2, 2025. |
| TOC Code | 37-39 | ATO | The Train Company that owns this fare. |
| Cross-London | 40-41 | 00 | Indicates if it includes Tube travel (01 = Yes). |
| NS Flag | 42 | Y | Is it a "Non-Standard" fare? |
| Fare (Pence) | 43-50 | 0000218 | The Price. This fare is £2.18. |

**Note** - This table was generated through google Gemini. I gave Gemini an example snippet form the `.FFL` file, and told it to explain the format exactly.

To find a stations NLC Code we need to use the `.LOC` file. The data is in this format:

| Field Name | Chars | Value | Description |
|---|---|---|---|
| Record Identity | 1-2 | RL | Rail Location record. |
| Revision Number | 3-4 | 70 | Internal versioning for the record. |
| NLC Code | 5-8 | 2774 | This is the gold! Use 2774 to search the .FFL file. |
| End Date | 10-17 | 023092025 | Date this record expires (DDMMYYYY). |
| Start Date | 18-25 | 11072025 | Date this record becomes active. |
| Created Date | 26-33 | 07042017 | When the station was first added to the DB. |
| Station Name | 44-73 | WILMSLOW | The human-readable name (padded with spaces). |
| CRS Code | 82-84 | WML | The 3-letter code you see on departure boards. |
| NLC (Again) | 93-96 | 2774 | Repeated for data integrity checks. |
| Zone/Region | 100-101 | 06 | Regional code (06 is usually North West/Manchester area). |