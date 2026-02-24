from flask import Flask, render_template, request, jsonify, make_response
from utils.logger import setup_logger
from middleware.limiter import setup_limiter, is_ip_blocked, block_ip, record_failed_attempt
import os

app = Flask(__name__)
# Secret key for session, though we're mainly using Redis for state
app.secret_key = os.urandom(24)

# Setup logging
logger = setup_logger()

# Setup rate limiting
limiter = setup_limiter(app)

DOMAIN = os.getenv('DOMAIN', 'raw.bruteforce-project.com')

@app.before_request
def check_blocked():
    # Allow CSS and static files to load even if blocked, otherwise the UI breaks
    if request.path.startswith('/static/'):
        return

    ip = request.remote_addr
    if is_ip_blocked(ip):
        logger.warning(f"Blocked IP attempted access: {ip}")
        return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('index.html', domain=DOMAIN)

@app.route('/login', methods=['POST'])
@limiter.limit("50 per minute", error_message="Rate Limit Exceeded. Too many requests within 1 minute.")
def login():
    ip = request.remote_addr
    username = request.form.get('username')
    password = request.form.get('password')
    
    logger.info(f"Login attempt - IP: {ip}, User: {username}")
    
    # Dummy authentication logic
    if username == 'admin' and password == 'supersecret123':
        logger.info(f"Successful login - IP: {ip}, User: {username}")
        return render_template('success.html', username=username, domain=DOMAIN)
    
    # Failed attempt logic
    logger.warning(f"Failed login attempt - IP: {ip}, User: {username}")
    
    # Record the failure and check if block threshold is reached
    failed_attempts = record_failed_attempt(ip)
    
    if failed_attempts >= 50:
        logger.error(f"BRUTE FORCE DETECTED: IP {ip} exceeded 50 failed attempts. Blocking.")
        return make_response(render_template('404.html'), 404)
    elif failed_attempts >= 5:
        logger.warning(f"RATE LIMIT DETECTED: IP {ip} exceeded 5 failed attempts.")
        return make_response(render_template('rate_limit.html', domain=DOMAIN), 429)
        
    return render_template('index.html', error="Invalid credentials", domain=DOMAIN)

@app.errorhandler(429)
def ratelimit_handler(e):
    ip = request.remote_addr
    logger.warning(f"Rate limit hit for IP: {ip}")
    # The IP gets 429s, but is NOT fully blocked (403) until 50 attempts
    return render_template('rate_limit.html', domain=DOMAIN), 429

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
