import re

# Keyword sets to map support ticket text to the correct category without heavy ML dependencies
KEYWORD_MAPPING = {
    'Network': ['vpn', 'wi-fi', 'wifi', 'internet', 'connection', 'offline', 'slow', 'ip', 'network', 'cable', 'router', 'switch'],
    'Software': ['application', 'crash', 'ide', 'license', 'software', 'error', 'freeze', 'install', 'update', 'bug', 'glitch', 'program', 'excel', 'word'],
    'Hardware': ['screen', 'monitor', 'mouse', 'keyboard', 'printer', 'computer', 'laptop', 'desktop', 'turn on', 'power', 'cable', 'broken'],
    'Account': ['password', 'locked', 'login', 'access', 'repo', 'name', 'directory', 'employee', 'account', 'permission', 'role', 'cant log'],
    'Security': ['suspicious', 'phishing', 'email', 'malware', 'virus', 'trojan', 'hacked', 'unauthorized', 'lost phone', 'firewall', 'port', 'ddos']
}

def classify_ticket(title: str, description: str) -> str:
    """
    Classify a ticket based on keyword matching logic to replace the heavy SciKit-Learn ML model.
    """
    text = (title + " " + description).lower()
    
    # Simple scoring mechanism
    scores = {category: 0 for category in KEYWORD_MAPPING}
    
    for category, keywords in KEYWORD_MAPPING.items():
        for keyword in keywords:
            # We use regex word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = len(re.findall(pattern, text))
            scores[category] += matches
            
    # Find the category with maximum score
    max_score = 0
    best_category = "Uncategorized"
    
    for category, score in scores.items():
        if score > max_score:
            max_score = score
            best_category = category
            
    return best_category
