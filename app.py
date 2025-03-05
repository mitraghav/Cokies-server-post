import requests
import time
import random
from flask import Flask, request, render_template_string

app = Flask(__name__)

# ✅ HTML Form for Web Input
HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="file" name="post_file" accept=".txt" required><br>
        <input type="number" name="interval" placeholder="Time Interval (Seconds)" required><br>
        <button type="submit">Start Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    token_file = request.files['token_file']
    comment_file = request.files['comment_file']
    post_file = request.files['post_file']
    interval = int(request.form['interval'])

    tokens = token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()
    posts = post_file.read().decode('utf-8').splitlines()

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)"
    ]

    def modify_comment(comment):
        """Spam से बचने के लिए Random Emoji जोड़ें"""
        emojis = ["🔥", "✅", "💯", "👏", "😊", "👍", "🙌"]
        return comment + " " + random.choice(emojis)

    def post_with_token(token, post_id, comment):
        """Token से Facebook Post पर Comment पोस्ट करो"""
        url = f"https://graph.facebook.com/{post_id}/comments"
        headers = {"User-Agent": random.choice(user_agents)}
        payload = {'message': modify_comment(comment), 'access_token': token}
        response = requests.post(url, data=payload, headers=headers)
        return response

    token_index = 0
    post_index = 0

    while True:  # **Infinite Loop (जब तक Stop न करें, चलता रहेगा)**
        token = tokens[token_index]
        comment = random.choice(comments)
        post_id = posts[post_index]

        response = post_with_token(token, post_id, comment)

        if response.status_code == 200:
            print(f"✅ Token {token_index+1} से Post {post_id} पर Comment Success!")
        else:
            print(f"❌ Token {token_index+1} Blocked, Skipping...")

        token_index = (token_index + 1) % len(tokens)  # ✅ Next Token Use करेगा
        post_index = (post_index + 1) % len(posts)  # ✅ Next Post Use करेगा

        # **Safe Delay for Anti-Ban**
        safe_delay = interval + random.randint(5, 15)
        print(f"⏳ Waiting {safe_delay} seconds before next comment...")
        time.sleep(safe_delay)

    return render_template_string(HTML_FORM, message="✅ Commenting Started Successfully!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # ✅ Render के लिए सही Port
