import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# ==============================
# CONFIG
# ==============================
CLOUD_URL = "https://college-rank-list-with-sgpa.onrender.com/submit_result"
VTU_URL = "https://results.vtu.ac.in/MJ26cbcs/index.php"  # 6th Sem, May/June-2026 exam


# ==============================
# PARSER
# ==============================
def parse_result(html, usn):
    soup = BeautifulSoup(html, "html.parser")

    data = {
        "usn": usn,
        "name": "Unknown",
        "total_marks": 0
    }

    # Student name
    texts = list(soup.stripped_strings)
    for i, t in enumerate(texts):
        if "Student Name" in t and i + 2 < len(texts):
            data["name"] = texts[i + 2].strip()
            break

    # Total marks
    total = 0
    rows = soup.find_all("div", class_="divTableRow")
    for r in rows:
        cells = r.find_all("div", class_="divTableCell")
        if len(cells) >= 6:
            try:
                total += int(cells[4].text.strip())
            except:
                pass

    data["total_marks"] = total
    return data


# ==============================
# MAIN
# ==============================
def main():
    print("\n🔵 Starting browser...")

    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.get(VTU_URL)

    usn = input("Enter USN: ").strip().upper()
    captcha = input("Enter CAPTCHA shown in browser: ").strip()

    print("🔵 Submitting form...")

    driver.find_element(By.NAME, "lns").send_keys(usn)
    driver.find_element(By.NAME, "captchacode").send_keys(captcha)
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    time.sleep(3)

    html = driver.page_source
    result = parse_result(html, usn)

    print("\n📦 Parsed Data:")
    print(result)

    print("\n🌐 Uploading to cloud server...")

    try:
        resp = requests.post(
            CLOUD_URL,
            json=result,
            headers={"Content-Type": "application/json"},
            timeout=20
        )

        print("✅ HTTP Status:", resp.status_code)
        print("✅ Server Response:", resp.text)

        if resp.status_code == 200:
            print("\n🎉 SUCCESS: Data stored in MongoDB Atlas")
        else:
            print("\n❌ Upload failed")

    except Exception as e:
        print("\n❌ Network error:", e)

    driver.quit()


if __name__ == "__main__":
    main()
