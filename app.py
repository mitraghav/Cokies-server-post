from flask import Flask, request, render_template_string
import requests
import time
import threading
import random

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment - Anti-Ban</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment - Anti-Ban</h1>
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

def keep_alive():
    """हर 5 मिनट में Server को जिंदा रखने के लिए एक Dummy Request भेजें"""
    while True:
        time.sleep(300)  # 5 मिनट Wait
        try:
            requests.get("https://your-deployed-url.onrender.com")
            print("🔄 Keeping Server Alive!")
        except:
            print("🚨 Keep Alive Failed!")

threading.Thread(target=keep_alive, daemon=True).start()

def anti_ban_commenting(tokens, comments, post_id, interval):
    url = f"https://graph.facebook.com/{post_id}/comments"
    blocked_tokens = set()
    retry_tokens = {}

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

    while True:
        for token in tokens:
            if token in blocked_tokens:
                if time.time() - retry_tokens[token] > 1800:  # 30 मिनट बाद फिर Try करेगा
                    blocked_tokens.remove(token)
                    print(f"🔄 Retrying Blocked Token: {token}")
                else:
                    continue

            comment = random.choice(comments)
            response = post_with_token(token, comment)

            if response and response.status_code == 200:
                print(f"✅ Comment Sent Successfully!")
            else:
                print(f"❌ Token Blocked! Will Retry in 30 Minutes...")
                blocked_tokens.add(token)
                retry_tokens[token] = time.time()

            safe_delay = interval + random.randint(500, 900)  # Random Delay 8-15 मिनट (Safe Anti-Ban)
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

    threading.Thread(target=anti_ban_commenting, args=(tokens, comments, post_id, interval), daemon=True).start()

    return render_template_string(HTML_FORM, message="✅ Anti-Ban Commenting Started in Background!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False, threaded=True)
