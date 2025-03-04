from flask import Flask, request, render_template_string
import requests
import time
import random
import threading
import os

app = Flask(__name__)

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
        <input type="number" name="interval" placeholder="Set Time Interval (Seconds)" required><br>
        <button type="submit">Start Safe Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

def auto_restart():
    """हर 10 मिनट में स्क्रिप्ट खुद को Restart करेगी।"""
    while True:
        time.sleep(600)  # 10 मिनट Wait
        print("🔄 Auto Restarting Script to Prevent Sleep Mode...")
        os.system("kill -9 $(pgrep -f 'python') && python3 main.py")  # खुद को Restart करें

def safe_commenting(tokens, comments, post_id, interval):
    url = f"https://graph.facebook.com/{post_id}/comments"
    blocked_tokens = set()
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)",
        "Mozilla/5.0 (Linux; Android 11; SM-G991B)"
    ]
    
    def modify_comment(comment):
        emojis = ["🔥", "✅", "💯", "👏", "😊", "👍", "🙌", "🎉", "😉", "💪"]
        variations = ["!!", "!!!", "✔️", "...", "🤩", "💥"]
        return f"{random.choice(variations)} {comment} {random.choice(emojis)}"

    def post_with_token(token, comment):
        headers = {"User-Agent": random.choice(user_agents)}
        payload = {'message': modify_comment(comment), 'access_token': token}
        try:
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            return response
        except requests.exceptions.RequestException:
            return None

    token_index = 0

    while True:
        token = tokens[token_index % len(tokens)]
        if token in blocked_tokens:
            print(f"⚠️ Blocked Token Skipped: {token}")
            token_index += 1
            time.sleep(600)
            continue

        comment = comments[token_index % len(comments)]
        response = post_with_token(token, comment)

        if response and response.status_code == 200:
            print(f"✅ Comment Sent Successfully!")
        else:
            print(f"❌ Token Blocked! Adding to Retry Queue...")
            blocked_tokens.add(token)

        token_index += 1
        safe_delay = interval + random.randint(300, 540)
        print(f"⏳ Waiting {safe_delay} seconds before next comment...")
        time.sleep(safe_delay)

@app.route('/submit', methods=['POST'])
def submit():
    token_file = request.files['token_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    tokens = token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    threading.Thread(target=safe_commenting, args=(tokens, comments, post_id, interval), daemon=True).start()

    return render_template_string(HTML_FORM, message="✅ Commenting Process Started in Background!")

if __name__ == '__main__':
    threading.Thread(target=auto_restart, daemon=True).start()
    app.run(host='0.0.0.0', port=10000, debug=False)
