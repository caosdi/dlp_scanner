# dlp_scanner

## Prerequisites

1. **Install Python 3**
   - From Microsoft Store: [Python 3 on Microsoft Store](https://apps.microsoft.com/detail/9PNRBTZXMB4Z?hl=en-us&gl=GB&ocid=pdpshare)
   - And from the official website: [python.org/downloads](https://www.python.org/downloads/)
   - **Important:** Add Python to PATH during installation.

2. **Prepare your workspace**
   - Create a folder on your Desktop (e.g., `dlp_scanner`).
   - Save the script (`dlp_email_scanner.py`) and the Excel file (`SmartIDDictionaryTerms.xlsx`) .
   - Create a subfolder named `attachments` and save `.eml` files or other attachments you want to scan in it.
   - This one-liner should create the folders in Desktop
      ```bash
      New-Item -Path "C:\Users\$env:USERNAME\Desktop\DLP\attachments" -ItemType Directory
      ```
3. **Install dependencies**
   - Open PowerShell in your project folder and run:

     ```powershell
     python.exe -m pip install pandas openpyxl python-docx PyPDF2 beautifulsoup4
     ```
4. Download the dictionary from Wiki

## Usage

To scan an email or attachment, run:

```powershell
py.exe ./dlp_email_scanner.py dlp_dict.json input_path [--scan [{ssn,cc,dl,dict} ...]]
```

- You can provide a folder containing `.eml` files or a single attachment (e.g., PDF, DOCX, XLSX) as the `input_path`.

You can also scan all files in the `attachments` folder at once:

```powershell
py.exe .\dlp_email_scanner.py .\dlp_dict.json .\attachments --scan ssn cc dl dict
```

For help and a full list of options, run:

```powershell
py.exe .\dlp_email_scanner.py -h
```

If you disable all, the script will default to running all checks.

When you run the script, the output will look similar to:

```powershell
PS C:\Users\Diego\Desktop\ubuntushared\PE\DLP> py.exe .\dlp_email_scanner.py .\attachments\ --scan ssn

email.eml
  [EMAIL_BODY]: 489-36-8350  [category: SSN]
  testingDLP.docx: 489-36-8350  [category: SSN]
  testingDLP.pdf: 489-36-8350  [category: SSN]
```

## Notes

- **Do not provide the output to the customer.** The output is for internal use only.

- To convert `.msg` files to `.eml`, use:

  ```bash
  msgconvert --mbox email.eml email.msg
  ```
  - You may need to install `msgconvert` in WSL:
    ```bash
    sudo apt install libemail-outlook-message-perl
    ```

- Make sure to use the correct Python version (3.x) to run the script. If you have multiple versions installed, use `py.exe` or specify the full path to the Python 3 executable.
- The script scans for sensitive information based on the terms defined in `SmartIDDictionaryTerms.xlsx`. It will output matches found in the email body or attachments. So please verify the rule and the terms that are triggering in the email.
- The script can handle various file types, including `.eml`, `.pdf`, `.docx`, and `.xlsx`. Ensure that the attachments are in the `attachments` folder.
- **Validate SSNs:** [ssnregistry.org/validate](https://www.ssnregistry.org/validate/)
- **Validate Credit Cards:** [validcreditcardnumber.com](https://www.validcreditcardnumber.com/)
- **Validate NDC:** [dps.fda.gov/ndc](https://dps.fda.gov/ndc/)

