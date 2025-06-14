

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env (for local testing)
load_dotenv()

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRF_TOKEN = os.getenv("CSRF_TOKEN")
HEADERS = {
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}",
    "x-csrftoken": CSRF_TOKEN,
    "referer": "https://leetcode.com",
    "origin": "https://leetcode.com",
    "Content-Type": "application/json",
}

LANGUAGE = "cpp"  # C++ for kamyu104
KAMYU_REPO_URL = "https://raw.githubusercontent.com/kamyu104/LeetCode-Solutions/master/C++/"

def send_telegram_message(msg):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("[!] Telegram credentials missing.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print(f"[!] Failed to send Telegram alert: {r.text}")
    except Exception as e:
        print(f"[!] Telegram error: {e}") 

# === STEP 1: Get today's POTD ===
def fetch_potd_slug():
    graphql_url = "https://leetcode.com/graphql"
    query = {
        "query": """
        query questionOfToday {
          activeDailyCodingChallengeQuestion {
            date
            question {
              titleSlug
              title
            }
          }
        }
        """
    }
    # Send the GraphQL request to LeetCodegraphql
    response = requests.post(graphql_url, json=query, headers=HEADERS)
    data = response.json()
    question = data["data"]["activeDailyCodingChallengeQuestion"]["question"]
    return question["titleSlug"], question["title"]

# === STEP 2: Convert to solution file name ===
def guess_cpp_filename(title):
    # Converts e.g. "Longest Increasing Path in a Matrix" → "longest-increasing-path-in-a-matrix.cpp"
    filename = title.lower().replace(" ", "-").replace("?", "").replace(",", "").replace("'", "")
    return filename + ".cpp"

# === STEP 3: Download C++ code from GitHub ===
def get_solution_code(filename):
    url = KAMYU_REPO_URL + filename
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        print(f"[!] Could not find file: {filename} in kamyu104 repo.")
        return None

# === STEP 4: Submit code to LeetCode ===
def submit_solution(title_slug, code):
    submit_url = f"https://leetcode.com/problems/{title_slug}/submit/"
    payload = {
        "lang": LANGUAGE,
        "question_id": fetch_question_id(title_slug),
        "typed_code": code
    }
    r = requests.post(submit_url, json=payload, headers=HEADERS)
    if r.status_code == 200:
        print(f"[✓] Submitted {title_slug} successfully.")
    elif r.status_code == 403:
        print(f"[!] Submission failed: {r.status_code} | {r.text}")
        send_telegram_message("⚠️ *LeetCode Session Expired*\nPlease update your `LEETCODE_SESSION` and `CSRF_TOKEN` in the `.env` file.")
    else:
        print(f"[!] Submission failed: {r.status_code} | {r.text}")
# === Utility: Get Question ID ===
def fetch_question_id(title_slug):
    query = {
        "query": """
        query questionData($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
          }
        }
        """,
        "variables": {
            "titleSlug": title_slug
        }
    }
    graphql_url = "https://leetcode.com/graphql"
    response = requests.post(graphql_url, json=query, headers=HEADERS)
    return response.json()["data"]["question"]["questionId"]

# === MAIN ===
def main():
    slug, title = fetch_potd_slug()
    filename = guess_cpp_filename(title)
    print(f"[•] POTD: {title} ({slug})")
    print(f"[•] Fetching file: {filename}")
    cpp_code = get_solution_code(filename)

    if cpp_code:
        submit_solution(slug, cpp_code)

if __name__ == "__main__":
    main()
