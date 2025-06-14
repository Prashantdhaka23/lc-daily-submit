# LeetCode POTD Daily Submit 🚀

Automate your daily LeetCode challenge submissions using GitHub Actions!  
This tool fetches the **LeetCode Daily Problem of the Day (POTD)**, downloads the C++ solution from [kamyu104/LeetCode-Solutions](https://github.com/kamyu104/LeetCode-Solutions), and automatically submits it to LeetCode. Telegram alerts notify you of success or failures like expired sessions.

---

## 📌 Features

- 🔁 Fetches the Daily LeetCode problem automatically
- 📦 Downloads C++ solution from `kamyu104/LeetCode-Solutions`
- 🚀 Submits the solution to LeetCode via API
- 🔔 Sends Telegram alerts for success/failure
- ⏰ Runs daily via GitHub Actions (configurable with cron)

---

## 📂 Folder Structure

```
.
├── .github/
│   └── workflows/
│       └── main.yml
├── .env                   # For local testing only (not used in GitHub Actions)
├── .gitignore
├── requirements.txt
├── submit_potd.py         # Main script to fetch and submit POTD
├── README.md
```

---

## ⚙️ Setup Instructions

### 1. Save This Repo

Clone or fork this repository to your GitHub account.

```bash
git clone https://github.com/Prashantdhaka23/lc-daily-submit.git
cd lc-daily-submit
```
---
### 2. Get Your LeetCode Cookies

1. Log in to [leetcode.com](https://leetcode.com)

2. Open your browser’s DevTools:
   - Right-click anywhere on the page → **Inspect**
   - Go to the **Application** tab
   - In the sidebar, go to **Storage → Cookies → https://leetcode.com**

3. Find and copy the values of the following cookies:
   - `LEETCODE_SESSION`
   - `csrftoken`

> 🔒 These are required to authenticate API requests to LeetCode.
---
### 3. Set Up GitHub Secrets

Go to your repository → `Settings` → `Secrets and variables` → `Actions` → `New repository secret` and add the following:

| Name                  | Description                            |
|-----------------------|----------------------------------------|
| `LEETCODE_SESSION`    | Your `LEETCODE_SESSION` cookie value   |
| `CSRF_TOKEN`          | Your `csrftoken` cookie value          |
| `TELEGRAM_BOT_TOKEN`  | Telegram bot token (from @BotFather)   |
| `TELEGRAM_CHAT_ID`    | Your personal or group chat ID         |

🔒 **Note:** Never commit your `.env` file or secrets into the repository.

---

### 4. Configure GitHub Workflow

Create the following workflow file at `.github/workflows/main.yml`:

```yaml
name: LC POTD Auto Submit

on:
  schedule:
    - cron: '4 0 * * *'  # Runs every day at 9:30 AM IST

  workflow_dispatch:

jobs:
  submit-daily-potd:
    runs-on: ubuntu-latest

    steps:
      - name: ⬇️ Checkout Repository
        uses: actions/checkout@v3

      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: 📦 Install dependencies
        run: pip install -r requirements.txt

      - name: 🚀 Run Submit Script
        env:
          LEETCODE_SESSION: ${{ secrets.LEETCODE_SESSION }}
          CSRF_TOKEN: ${{ secrets.CSRF_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python submit_potd.py
```

---

### 5. `submit_potd.py` Logic Overview

The script performs the following steps:

1. Fetches the **POTD (Problem of the Day)** using LeetCode's GraphQL API.
2. Constructs the expected filename from kamyu104's C++ repo.
3. Downloads the corresponding `.cpp` file.
4. Submits the solution using your LeetCode session.
5. Sends a Telegram message on success or failure (e.g., if session is expired).

---

### 6. Example `requirements.txt`

```
requests
python-dotenv
```

> Use `pip install -r requirements.txt` locally for testing.

---


## 🧪 Testing It Locally

### ✅ Steps:

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** in the root directory with the following content:

   ```env
   LEETCODE_SESSION=your_session_cookie_here
   CSRF_TOKEN=your_csrf_token_here
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

3. **Run the script:**
   ```bash
   python submit_potd.py
   ```
   > 💬 You should receive a Telegram message on success or failure.

---

## 📬 Telegram Alert Example

If the session is expired or submission fails, you’ll get a message like:

```
⚠️ LeetCode Session Expired
Please update your LEETCODE_SESSION and CSRF_TOKEN in GitHub secrets.
```

---

## 🧼 Experimental Files

The `experiment.py` file has been archived. It was used only for initial Selenium-based login testing.

> 🧪 **Note:**  
> Selenium-based login was **tested but later discarded** due to LeetCode’s enhanced login security mechanisms (e.g., CAPTCHA, MFA), which made automation unreliable and inconsistent.

---

---

## 🙌 Contributing & Support

If you find this project helpful, please consider giving it a ⭐️ — it really motivates and helps others discover the tool!

Found a bug or have an improvement idea?  
We welcome contributions! Feel free to [open an issue](https://github.com/Prashantdhaka23/lc-daily-submit/issues) or [raise a pull request](https://github.com/Prashantdhaka23/lc-daily-submit/pulls).

---

> Made with 💻, ☕, and a bit of automation magic ✨

## 📄 License

This project is licensed under the MIT License.

---

Happy Coding! 💻✨  
– Built for automation lovers!
