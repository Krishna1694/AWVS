# Advanced Web Vulnerability Scanner (AWVS Project)

This is a minimal, educational web vulnerability scanner with a **Tkinter GUI**, designed for learning and research purposes.  
**Important:** Only run scans against targets you own or have explicit permission to test. Unauthorized scanning is illegal.

**Role:** Backend Developer & Team Lead  
**Project Context:** Developed during my **Supraja Technologies internship** to understand automated vulnerability scanning, analyze scanner limitations, and implement a lightweight educational tool.

---

## Features

- Lightweight crawling and passive security checks
    
- Non-destructive heuristic checks for a subset of **OWASP Top 10 vulnerabilities**:
    
    - SQL Injection (heuristic detection)
        
    - Cross-Site Scripting (XSS) reflections
        
    - Security headers verification and more...
        
- Optional integrations for deeper scanning:
    
    - **sqlmap (CLI)**: confirm SQL injections
        
    - **ZAP (via zap-cli)**: advanced vulnerability scanning
        

---

## Installation

1. Clone the repository:
    
    ```bash
    git clone https://github.com/yourusername/awvs-project.git 
    cd awvs-project
    ```
    
2. Create and activate a virtual environment:
    
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
    ```
    
3. Install dependencies:
    
    ```bash
    pip install -r requirements.txt
    ```
    
4. Optional tools:
    
    - **sqlmap**: install via package manager or [GitHub](https://github.com/sqlmapproject/sqlmap)
        
    - **ZAP**: install ZAP and [zap-cli](https://github.com/Grunny/zap-cli)
        

---

## Running the Application

`python3 app.py`

- The **Tkinter UI** allows selecting scan targets, enabling optional integrations, and viewing scan progress.
    
- Default mode is **non-destructive**. Deep scans (sqlmap/ZAP/SSRF active tests) require explicit toggles in the UI.
    

---

## Safety & Ethical Guidelines

- Only scan targets you own or have **written authorization** to test.
    
- Default scans are non-destructive.
    
- Deep scans can be destructive or trigger alerts—use with caution.
    

---

## Project Workflow & Learnings

1. **Planning & Setup:** Defined scanning scope, selected targets, and designed Tkinter UI.
    
2. **Scanner Implementation:** Integrated lightweight crawling, heuristic checks, and optional tools.
    
3. **Analysis:** Evaluated scan results, false positives, and scanner limitations.
    
4. **Documentation:** Compiled findings, insights, and recommendations for further improvement.
    

**Learnings:**

- In-depth understanding of **automated vulnerability scanners**
    
- Advantages: fast scanning, structured reports, broad coverage
    
- Limitations: false positives, inability to detect business logic flaws, dependency on tool updates
    
- Improved skills in **Python, backend integration, API usage, and security testing workflows**
    

---

## Future Enhancements

- Dashboard for visualizing scan results
    
- CI/CD integration for automated security testing
    
- Advanced filtering to reduce false positives
    

---

## References

- OWASP Top 10
    
- [sqlmap](https://github.com/sqlmapproject/sqlmap)
    
- ZAP Proxy