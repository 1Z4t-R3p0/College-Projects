import requests
from bs4 import BeautifulSoup
import urllib.parse
import ipaddress
import socket
import re

class WebScanner:
    def __init__(self, target_url):
        self.target_url = self.normalize_url(target_url)
        self.domain = urllib.parse.urlparse(self.target_url).netloc
        self.results = []
        self.scanned_urls = set()

    def normalize_url(self, url):
        if not url.startswith(('http://', 'https://')):
            return f'http://{url}'
        return url

    def is_safe_url(self, url):
        """Check if the URL points to a prohibited IP range."""
        try:
            hostname = urllib.parse.urlparse(url).hostname
            if not hostname:
                return False
            
            ip_address = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip_address)
            
            # Check for private ranges
            if ip_obj.is_private or ip_obj.is_loopback:
                return False
            return True
        except Exception:
            return False

    def check_security_headers(self, headers):
        """Check for missing security headers."""
        headers_to_check = {
            "X-Frame-Options": "Low",
            "Content-Security-Policy": "Low",
            "X-XSS-Protection": "Low"
        }
        
        for header, severity in headers_to_check.items():
            if header not in headers:
                self.results.append({
                    "type": "Missing Security Header",
                    "url": self.target_url,
                    "severity": severity,
                    "description": f"The security header '{header}' is missing, which could lead to common web attacks."
                })

    def test_sql_injection(self, url, forms):
        """Basic SQL Injection test using error-based detection."""
        sql_payload = "' OR 1=1 --"
        sql_errors = [
            "SQL syntax", "mysql_fetch", "ora-", "PostgreSQL query failed",
            "Microsoft OLE DB Provider for SQL Server", "Unclosed quotation mark"
        ]

        for form in forms:
            action = form.get('action')
            method = form.get('method', 'get').lower()
            inputs = form.find_all(['input', 'textarea'])
            
            target_form_url = urllib.parse.urljoin(url, action)
            data = {}
            for input_field in inputs:
                name = input_field.get('name')
                if name:
                    data[name] = sql_payload

            try:
                if method == 'post':
                    response = requests.post(target_form_url, data=data, timeout=5)
                else:
                    response = requests.get(target_form_url, params=data, timeout=5)

                for error in sql_errors:
                    if error.lower() in response.text.lower():
                        self.results.append({
                            "type": "SQL Injection",
                            "url": target_form_url,
                            "severity": "High",
                            "description": "Potential SQL Injection detected via error-based analysis. The application returned a database error after being injected with a payload."
                        })
                        break
            except Exception:
                continue

    def test_xss(self, url, forms):
        """Basic Reflected XSS test."""
        xss_payload = "<script>alert(1)</script>"
        
        for form in forms:
            action = form.get('action')
            method = form.get('method', 'get').lower()
            inputs = form.find_all(['input', 'textarea'])
            
            target_form_url = urllib.parse.urljoin(url, action)
            data = {}
            for input_field in inputs:
                name = input_field.get('name')
                if name:
                    data[name] = xss_payload

            try:
                if method == 'post':
                    response = requests.post(target_form_url, data=data, timeout=5)
                else:
                    response = requests.get(target_form_url, params=data, timeout=5)

                if xss_payload in response.text:
                    self.results.append({
                        "type": "Cross-Site Scripting (XSS)",
                        "url": target_form_url,
                        "severity": "Medium",
                        "description": "Reflected XSS detected. The application reflected a script payload without proper encoding."
                    })
            except Exception:
                continue

    def test_open_redirect(self, url):
        """Basic Open Redirect test on common parameters."""
        redirect_payload = "https://google.com"
        params = ['url', 'next', 'redirect', 'target', 'dest']
        
        for param in params:
            test_url = f"{url}{'&' if '?' in url else '?'}{param}={redirect_payload}"
            try:
                response = requests.get(test_url, timeout=5, allow_redirects=False)
                if response.status_code in [301, 302] and response.headers.get('Location') == redirect_payload:
                    self.results.append({
                        "type": "Open Redirect",
                        "url": test_url,
                        "severity": "Medium",
                        "description": f"The application is vulnerable to Open Redirect via the '{param}' parameter."
                    })
            except Exception:
                continue

    def run_scan(self):
        if not self.is_safe_url(self.target_url):
            return {"error": "Scanning internal or private IP addresses is prohibited."}

        try:
            response = requests.get(self.target_url, timeout=10)
            self.check_security_headers(response.headers)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')
            
            self.test_sql_injection(self.target_url, forms)
            self.test_xss(self.target_url, forms)
            self.test_open_redirect(self.target_url)

            summary = {
                "total": len(self.results),
                "high": len([r for r in self.results if r['severity'] == "High"]),
                "medium": len([r for r in self.results if r['severity'] == "Medium"]),
                "low": len([r for r in self.results if r['severity'] == "Low"]),
            }
            
            return {
                "target_url": self.target_url,
                "summary": summary,
                "vulnerabilities": self.results
            }
        except Exception as e:
            return {"error": f"Failed to connect to target: {str(e)}"}
