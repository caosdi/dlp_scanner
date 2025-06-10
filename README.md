# dlp_scanner

## Prerequisites

1. **Install Python 3**
   - From Microsoft Store: [Python 3 on Microsoft Store](https://apps.microsoft.com/detail/9PNRBTZXMB4Z?hl=en-us&gl=GB&ocid=pdpshare)
   - And from the official website: [python.org/downloads](https://www.python.org/downloads/)
   - **Important:** Add Python to PATH during installation.

2. **Prepare your workspace**
   - Create a folder on your Desktop (e.g., `dlp_scanner`).
   - Save the script (`dlp_email_scanner.py`) and the Excel file (`SmartIDDictionaryTerms.xlsx`) in this folder.
   - Create a subfolder named `attachments` and save `.eml` files or other attachments you want to scan in it.

3. **Install dependencies**
   - Open PowerShell in your project folder and run:

     ```powershell
     python.exe -m pip install pandas openpyxl python-docx PyPDF2 beautifulsoup4
     ```
4. Download the `SmartIDDictionaryTerms.xlsx` file from the Guide wiki.
   - Not going to add the URL to the wiki as this is not public information

## Usage

To scan an email or attachment, run:

```powershell
py.exe .\dlp_email_scanner.py .\SmartIDDictionaryTerms.xlsx .\attachments\email.eml
```

- You can also provide a folder containing `.eml` files or a single attachment (e.g., PDF, DOCX, XLSX) as the third argument.

## Notes

- To convert `.msg` files to `.eml`, use:

  ```bash
  msgconvert --mbox email.eml email.msg
  ```
  - You may need to install `msgconvert` in WSL:
    ```bash
    sudo apt install libemail-outlook-message-perl
    ```

- **Validate SSNs:** [ssnregistry.org/validate](https://www.ssnregistry.org/validate/)
- **Validate Credit Cards:** [validcreditcardnumber.com](https://www.validcreditcardnumber.com/)
- **Validate NDC:** [dps.fda.gov/ndc](https://dps.fda.gov/ndc/)
