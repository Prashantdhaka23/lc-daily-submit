#experiment to fully automate leetcode potd submission

import os
import time
import requests
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

KAMYU_REPO_URL = "https://raw.githubusercontent.com/kamyu104/LeetCode-Solutions/master/C++/"
LANGUAGE = "cpp"
from selenium_stealth import stealth



def update_env_cookie(key, value):
    # Replace or append cookie value in .env
    updated_lines = []
    found = False
    if not os.path.exists(".env"):
        open(".env", "w").close()
    with open(".env", "r") as file:
        for line in file:
            if line.startswith(key + "="):
                updated_lines.append(f"{key}={value}\n")
                found = True
            else:
                updated_lines.append(line)
    if not found:
        updated_lines.append(f"{key}={value}\n")
    with open(".env", "w") as file:
        file.writelines(updated_lines)



def refresh_leetcode_tokens():
    load_dotenv()
    USERNAME = os.getenv("LEETCODE_USERNAME")
    PASSWORD = os.getenv("LEETCODE_PASSWORD")

    if not USERNAME or not PASSWORD:
        print("❌ Username or password not found in .env")
        exit(1)

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--headless=new")  # Optional: Enable for full automation

    driver = uc.Chrome(options=options, version_main=137)

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    # ✅ Enable cookie tracking to access HttpOnly cookies like LEETCODE_SESSION
    driver.execute_cdp_cmd("Network.enable", {})

    try:
        print("🔐 Opening LeetCode login page...")
        driver.get("https://leetcode.com/accounts/login/")
        wait = WebDriverWait(driver, 30)

        username_input = wait.until(EC.presence_of_element_located((By.ID, "id_login")))
        password_input = driver.find_element(By.ID, "id_password")

        time.sleep(1)
        username_input.send_keys(USERNAME)
        time.sleep(1)
        password_input.send_keys(PASSWORD)
        time.sleep(1)
        password_input.send_keys(Keys.RETURN)

        print("🛑 Waiting for manual login if needed (2 min)...")
        WebDriverWait(driver, 120).until(lambda d: "https://leetcode.com" in d.current_url)

        # ✅ Navigate to a protected page to trigger LEETCODE_SESSION creation
        driver.get("https://leetcode.com/problemset/all/")
        time.sleep(5)

        # ✅ Fetch all cookies including HttpOnly using Chrome DevTools Protocol
        all_cookies = driver.execute_cdp_cmd("Network.getAllCookies", {})["cookies"]
        cookies = {cookie["name"]: cookie["value"] for cookie in all_cookies}

        for name, value in cookies.items():
            print(name, value)

        driver.quit()

        if "LEETCODE_SESSION" in cookies and "csrftoken" in cookies:
            update_env_cookie("LEETCODE_SESSION", cookies["LEETCODE_SESSION"])
            update_env_cookie("CSRF_TOKEN", cookies["csrftoken"])
            print("✅ Login successful. Tokens refreshed.")
            return cookies["LEETCODE_SESSION"], cookies["csrftoken"]
        else:
            print("❌ Missing LEETCODE_SESSION or csrftoken cookie.")
            exit(1)

    except Exception as e:
        print("❌ Login failed:", e)
        try:
            with open("leetcode_login_debug.html", "w") as f:
                f.write(driver.page_source)
            print("📄 Page dumped to leetcode_login_debug.html")
        except:
            pass
        driver.quit()
        exit(1)
def get_headers():
    load_dotenv()
    LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
    CSRF_TOKEN = os.getenv("CSRF_TOKEN")
    if not LEETCODE_SESSION or not CSRF_TOKEN:
        print("❌ Missing session or CSRF token.")
        exit(1)
    return {
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}",
        "x-csrftoken": CSRF_TOKEN,
        "referer": "https://leetcode.com",
        "origin": "https://leetcode.com",
        "Content-Type": "application/json",
    }

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
    response = requests.post(graphql_url, json=query, headers=get_headers())
    question = response.json()["data"]["activeDailyCodingChallengeQuestion"]["question"]
    return question["titleSlug"], question["title"]

def guess_cpp_filename(title):
    return title.lower().replace(" ", "-").replace("?", "").replace(",", "").replace("'", "") + ".cpp"

def get_solution_code(filename):
    url = KAMYU_REPO_URL + filename
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        print(f"[!] File not found in repo: {filename}")
        return None

def fetch_question_id(title_slug):
    query = {
        "query": """
        query questionData($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
          }
        }
        """,
        "variables": { "titleSlug": title_slug }
    }
    graphql_url = "https://leetcode.com/graphql"
    r = requests.post(graphql_url, json=query, headers=get_headers())
    return r.json()["data"]["question"]["questionId"]

def submit_solution(title_slug, code):
    payload = {
        "lang": LANGUAGE,
        "question_id": fetch_question_id(title_slug),
        "typed_code": code
    }
    submit_url = f"https://leetcode.com/problems/{title_slug}/submit/"
    r = requests.post(submit_url, json=payload, headers=get_headers())
    if r.status_code == 200:
        print(f"[✓] Submitted {title_slug} successfully.")
    else:
        print(f"[!] Submission failed: {r.status_code} | {r.text}")

def main():
    refresh_leetcode_tokens()
    slug, title = fetch_potd_slug()
    filename = guess_cpp_filename(title)
    print(f"[•] POTD: {title} ({slug})")
    print(f"[•] Fetching file: {filename}")
    cpp_code = get_solution_code(filename)
    if cpp_code:
        submit_solution(slug, cpp_code)

if __name__ == "__main__":
    main()
