


# Automated Credit Risk Report Generator

This project is a web-based platform that automates the generation of credit risk reports for companies based on uploaded financial documents. Built using **Django (backend)** and **HTML/CSS (frontend)**, the system parses PDF financial statements, extracts relevant financial metrics using `pdfplumber` and `re`, computes credit risk scores using a weighted scoring model, and generates a downloadable report.



## 🚀 Features

- Upload company information and financial documents (PDFs)
- Automated parsing of:
  - **Balance Sheet**
  - **Income Statement**
  - **Cash Flow Statement**
- Extraction of key and derived financial metrics using `pdfplumber` (for reading) and `re` (for pattern matching)
- Credit risk scoring using custom logic with weights and thresholds
- Preview of credit score before download
- Generate and download a detailed DOCX report of the analysis



## 🧰 Tech Stack

| Layer            | Technology / Library             |
|------------------|----------------------------------|
| Backend          | Django (Python)                  |
| Frontend         | HTML, CSS                        |
| PDF Parsing      | pdfplumber |
| Pattern Matching | Regular Expressions              |
| Report Generation| python-docx              |

## 🧾 API Endpoints

| URL Path              | View Function       | Description                                      |
|-----------------------|---------------------|--------------------------------------------------|
| `/upload/`            | `company_info`      | Displays the form to enter company information   |
| `/upload/upload/`     | `document_upload`   | Uploads financial documents (PDFs)               |
| `/upload/success/`    | `upload_success`    | Confirms successful upload                       |
| `/download_report/`   | `download_report`   | Generates and downloads the credit risk report   |



## 📸 Sample Output

Below are screenshots of the website interface and a sample generated credit risk report.

### 🔹 Website UI Screenshots
![Credit Score Preview](https://github.com/user-attachments/assets/c400fe74-83e5-46d9-bf73-33e40aa5f3a6)

*Company Information Upload Page*

![Document Upload Page](https://github.com/user-attachments/assets/9dde3476-783c-4cb2-a747-cad9b22739ae)
*PDF Document Upload (Balance Sheet, Income Statement, etc.)*

![Company Info Page](https://github.com/user-attachments/assets/df3b5a64-70d6-46b1-9ce5-1e1d781a9d51)
*Credit Score Preview and Download Button*

---

### 📄 Sample Credit Risk Report

📥 [Download credit_report.docx](https://github.com/user-attachments/files/20908419/credit_report_14.docx)

This downloadable `.docx` file contains:
- Company Information
- Parsed Financial Metrics
- Computed Risk Scores
- Risk Level Interpretation
- Summary Notes




