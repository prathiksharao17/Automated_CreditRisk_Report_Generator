


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




