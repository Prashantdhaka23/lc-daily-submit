import os
import requests

LEETCODE_SESSION = os.environ.get("LEETCODE_SESSION")
CSRF_TOKEN = os.environ.get("CSRF_TOKEN")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

HEADERS = {
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}",
    "x-csrftoken": CSRF_TOKEN,
    "referer": "https://leetcode.com",
    "origin": "https://leetcode.com",
    "Content-Type": "application/json",
}

LANGUAGE = "cpp"
GITHUB_URL = "https://raw.githubusercontent.com/kamyu104/LeetCode-Solutions/master/C++/"

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] Missing Telegram credentials.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"[!] Telegram alert failed: {response.text}")
    except Exception as e:
        print(f"[!] Telegram error: {e}")

def fetch_potd_slug():
    query = {
        "query": """
        query {
          activeDailyCodingChallengeQuestion {
            question {
              titleSlug
              title
            }
          }
        }
        """
    }
    response = requests.post("https://leetcode.com/graphql", json=query, headers=HEADERS)
    data = response.json()
    question = data["data"]["activeDailyCodingChallengeQuestion"]["question"]
    return question["titleSlug"], question["title"]

def guess_cpp_filename(title):
    filename = title.lower().replace(" ", "-").replace("?", "").replace(",", "").replace("'", "")
    return filename + ".cpp"

def get_solution_code(filename):
    url = GITHUB_URL + filename
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    print(f"[!] File not found in repo: {filename}")
    return None

def fetch_question_id(title_slug):
    query = {
        "query": """
        query($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
          }
        }
        """,
        "variables": {"titleSlug": title_slug}
    }
    response = requests.post("https://leetcode.com/graphql", json=query, headers=HEADERS)
    return response.json()["data"]["question"]["questionId"]

def submit_solution(title_slug, code):
    payload = {
        "lang": LANGUAGE,
        "question_id": fetch_question_id(title_slug),
        "typed_code": code
    }
    url = f"https://leetcode.com/problems/{title_slug}/submit/"
    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print(f"[✓] Submitted {title_slug} successfully.")
    elif response.status_code == 403:
        print(f"[!] Submission failed: {response.status_code} | {response.text}")
        send_telegram_message(
            "⚠️ *LeetCode Session Expired*\nPlease update your `LEETCODE_SESSION` and `CSRF_TOKEN` in GitHub Secrets."
        )
    else:
        print(f"[!] Submission failed: {response.status_code} | {response.text}")

def main():
    slug, title = fetch_potd_slug()
    print(f"[•] POTD: {title} ({slug})")
    filename = guess_cpp_filename(title)
    print(f"[•] Fetching solution file: {filename}")
    code = get_solution_code(filename)
    if code:
        submit_solution(slug, code)

if __name__ == "__main__":
    main()
