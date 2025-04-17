import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def cyberpaw_message(result_type):
    messages = {
        "safe": "Purr-fect! This link looks good to go. Just make sure it’s from a trusted source next time. 🐾",
        "suspicious": "Hmm... my whiskers are twitching. Something feels a little off. Be careful. Maybe double-check who sent this.",
        "dangerous": "Claws out! This link is dangerous. It’s trying to steal your personal info! 🚨 Please avoid clicking it.",
    }
    return messages.get(result_type, "I couldn't figure that one out. Be extra careful!")

def is_valid_url(link):
    try:
        result = urlparse(link)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_strange_domain(domain):
    return re.search(r"(login|secure|update|account|bank)[.-]", domain)

def check_link(link):
    if not is_valid_url(link):
        print("Hmm... that doesn't look like a proper link. Please enter a full URL like 'https://example.com'")
        return "suspicious"
    
    if not link.startswith("https://"):
        print("Warning: This site is not using HTTPS. It may not be secure.")

    try:
        headers = {'User-Agent': 'CyberPawLinkChecker/1.1'}
        response = requests.get(link, timeout=5, headers=headers)

        if response.status_code != 200:
            return "suspicious"

        domain = urlparse(link).netloc.lower()

        # Flag suspicious domain names
        if is_strange_domain(domain):
            return "dangerous"

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.lower() if soup.title else ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        desc_text = meta_desc["content"].lower() if meta_desc and "content" in meta_desc.attrs else ""

        scan_text = title + " " + desc_text

        if re.search(r"(enter your password|verify your identity|unauthorized|security alert)", scan_text):
            return "dangerous"
        elif re.search(r"(claim your prize|you won|limited offer|urgent action)", scan_text):
            return "suspicious"
        else:
            return "safe"

    except requests.exceptions.Timeout:
        print("Request timed out.")
        return "suspicious"
    except Exception as e:
        print(f"Error: {e}")
        return "dangerous"

def phishing_link_scanner():
    print("Welcome to CyberPaw's Phishing Link Scanner! 🐾")
    link = input("Enter the link you want to check: ").strip()

    result = check_link(link)

    print("\nScanner Result:")
    print(f"Link Status: {result.capitalize()}")

    print("\nCyberPaw says:")
    print(cyberpaw_message(result))

if __name__ == "__main__":
    phishing_link_scanner()


