from flask import Flask, request, render_template_string
import requests
import time
import random
import threading
import undetected_chromedriver as uc

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

def safe_commenting(tokens, comments, post_id, interval):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)",
        "Mozilla/5.0 (Linux; Android 11; SM-G991B)"
    ]
    
    blocked_tokens = set()
    
    def modify_comment(comment):
        emojis = ["🔥", "✅", "💯", "👏", "😊", "👍", "🙌", "🎉", "😉", "💪"]
        variations = ["!!", "!!!", "✔️", "...", "🤩", "💥"]
        return f"{random.choice(variations)} {comment} {random.choice(emojis)}"

    def post_with_selenium(token, comment):
        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        driver = uc.Chrome(options=options)
        driver.get(f"https://graph.facebook.com/{post_id}/comments?access_token={token}")
        
        try:
            driver.find_element("name", "message").send_keys(modify_comment(comment))
            driver.find_element("name", "submit").click()
            print(f"✅ Token से Comment Success!")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            driver.quit()

    token_index = 0
    success_count = 0

    while True:
        token = tokens[token_index % len(tokens)]
        
        if token in blocked_tokens:
            print(f"⚠️ Token Skipped (Blocked) → Retrying after 10 min: {token}")
            token_index += 1
            time.sleep(600)  # 10 मिनट का Wait
            continue

        comment = comments[token_index % len(comments)]
        post_with_selenium(token, comment)

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
    app.run(host='0.0.0.0', port=10000, debug=False)
