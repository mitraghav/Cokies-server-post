from flask import Flask, request, render_template_string
import requests
import time
import random
import threading

app = Flask(__name__)

# Simple Web Interface
HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment - Carter by Rocky Roy</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment - Carter by Rocky Roy</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <button type="submit">Start Commenting</button>
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

def load_tokens(token_file):
    """ Load tokens and track blocked ones """
    tokens = token_file.read().decode('utf-8').splitlines()
    return {token: True for token in tokens}  # True = Active, False = Blocked

def load_comments(comment_file):
    """ Load comments """
    return comment_file.read().decode('utf-8').splitlines()

def extract_post_id(post_url):
    """ Extract Post ID from URL """
    try:
        return post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return None

def get_random_user_agent():
    """ Generate a random user-agent to avoid detection """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.98 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:91.0) Gecko/20100101 Firefox/91.0"
    ]
    return random.choice(user_agents)

def modify_comment(comment):
    """ Add random variation to comments to avoid spam detection """
    emojis = ["🔥", "✅", "💯", "👏", "😊", "👍", "🙌", "🎉", "😉", "💪"]
    return f"{random.choice(emojis)} {comment} {random.choice(emojis)}"

def post_comment(post_id, token, comment):
    """ Post a comment on Facebook """
    url = f"https://graph.facebook.com/{post_id}/comments"
    payload = {'message': modify_comment(comment), 'access_token': token}
    headers = {'User-Agent': get_random_user_agent()}  # Random User-Agent

    response = requests.post(url, data=payload, headers=headers)
    return response

def auto_commenting(tokens, comments, post_id):
    """ Main commenting loop with random delay & token rotation """
    token_list = list(tokens.keys())
    token_index = 0

    while True:
        active_tokens = [t for t in tokens if tokens[t]]  # Get active tokens

        if not active_tokens:
            print("🚨 No active tokens available. Retrying in 5 minutes...")
            time.sleep(300)
            continue

        token = active_tokens[token_index % len(active_tokens)]
        comment = comments[token_index % len(comments)]

        response = post_comment(post_id, token, comment)

        if response.status_code == 200:
            print(f"✅ Success! Comment posted with Token {token_index+1}")
        else:
            print(f"❌ Token {token_index+1} blocked! Skipping it...")
            tokens[token] = False  # Mark token as blocked

        token_index += 1
        
        # Random Delay (5-9 Minutes)
        delay = random.randint(300, 540)
        print(f"⏳ Waiting {delay} seconds before next comment...")
        time.sleep(delay)

        # **Check & Reactivate Blocked Tokens**
        for t in tokens:
            if not tokens[t]:  # If token is blocked, check its status
                check_url = f"https://graph.facebook.com/me?access_token={t}"
                check_response = requests.get(check_url)
                if check_response.status_code == 200:
                    print(f"🔓 Token Reactivated: {t}")
                    tokens[t] = True  # Mark as active again

@app.route('/submit', methods=['POST'])
def submit():
    token_file = request.files['token_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']

    tokens = load_tokens(token_file)
    comments = load_comments(comment_file)
    post_id = extract_post_id(post_url)

    if not post_id:
        return "❌ Invalid Post URL!"

    thread = threading.Thread(target=auto_commenting, args=(tokens, comments, post_id))
    thread.start()

    return "✅ Auto commenting started successfully!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
