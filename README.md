# LC Daily Submit 🚀

Automate your daily LeetCode challenge submissions using GitHub Actions!  
This tool fetches the **LeetCode Daily Problem**, checks for a local solution in your repository (e.g., `githubSoln/`), and auto-submits it to LeetCode.

---

## 📌 Features

- 🔁 Automatically fetches the daily LeetCode problem
- 🧠 Detects if a solution exists in your repo
- 🚀 Automatically submits the solution to LeetCode
- ⏰ Runs daily (customizable via cron)

---

## 📂 Folder Structure

```
githubSoln/
├── 2025/
│   └── 06/
│       └── 08_DailyProblem.py
│
└── utils/
    └── leetcode_submitter.py

.github/
└── workflows/
    └── daily-submit.yml
```

---

## ⚙️ Setup Instructions

### 1. Organize Your Solutions

Create a `githubSoln/` folder and store your solutions in a structure like:

```
githubSoln/YYYY/MM/DD_ProblemTitle.py
```

Make sure filenames include either the date or exact title so the script can match them.

---

### 2. Configure Secrets

Go to your GitHub repository > `Settings` > `Secrets and variables` > `Actions` and add:

- `LEETCODE_USERNAME`: Your LeetCode username
- `LEETCODE_PASSWORD`: Your LeetCode password (or App Password if 2FA is enabled)

---

### 3. GitHub Actions Workflow

Create a workflow file at `.github/workflows/daily-submit.yml`:

```yaml
name: LeetCode Daily Submit

on:
  schedule:
    - cron: '30 0 * * *'  # Runs at 6:00 AM IST daily
  workflow_dispatch:

jobs:
  daily-leetcode-submit:
    runs-on: ubuntu-latest

    steps:
      - name: ⬇️ Checkout Repository
        uses: actions/checkout@v3

      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: 📦 Install Dependencies
        run: pip install -r requirements.txt

      - name: 🚀 Run Daily Submit Script
        env:
          LEETCODE_USERNAME: ${{ secrets.LEETCODE_USERNAME }}
          LEETCODE_PASSWORD: ${{ secrets.LEETCODE_PASSWORD }}
        run: python githubSoln/utils/leetcode_submitter.py
```

---

### 4. `leetcode_submitter.py` Logic (High-Level)

The script should:

1. Fetch the Daily Problem from LeetCode (via GraphQL or web scraping).
2. Parse the title/date and look for a matching `.py` file inside `githubSoln/YYYY/MM/`.
3. Read the file and submit the code to LeetCode using credentials from environment variables.

---

### 5. Example `requirements.txt`

```
requests
beautifulsoup4
leetcode-api-wrapper  # or your own script
```

---

## 🧪 Testing

You can manually trigger the workflow via the "Run workflow" button in the GitHub Actions tab. This is useful for testing before letting it run on schedule.

---

## 📌 Notes

- Ensure your filenames are predictable based on the daily problem.
- You may implement fuzzy matching for problem titles if exact matches are difficult.
- Logs will appear in the Actions tab — monitor them for issues.

---

## 📬 Contributions

Pull requests are welcome for:
- Adding support for other languages (e.g., C++, Java)
- Improving problem matching
- Enhancing security or error handling

---

## 📄 License

MIT License

---

Happy Coding! 💻✨
