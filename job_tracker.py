import requests, sqlite3, openai
from bs4 import BeautifulSoup

openai.api_key = "sk-..."  # replace with your API key

def scrape_jobs(keyword, location="remote", limit=5):
    url = f"https://remoteok.io/remote-{keyword}-jobs"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    jobs = soup.find_all('tr', class_='job')
    out = []
    for job in jobs[:limit]:
        title = job.find('h2').text.strip()
        desc = job.find('td', class_='company_and_position').text.strip()
        out.append({'title': title, 'desc': desc})
    return out

def score_match(job_text, resume_text):
    prompt = f"Does this job description match this resume? Score from 0-10.\n\nJob: {job_text}\n\nResume: {resume_text}"
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    score_line = res.choices[0].message.content.strip()
    return score_line

def save_to_db(jobs):
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS matched_jobs (title TEXT, desc TEXT, score TEXT)''')
    c.executemany('INSERT INTO matched_jobs VALUES (?, ?, ?)', jobs)
    conn.commit()
    conn.close()

def main():
    resume = open("my_resume.txt").read()
    jobs = scrape_jobs("python")
    scored = []
    for job in jobs:
        score = score_match(job["desc"], resume)
        scored.append((job["title"], job["desc"], score))
    save_to_db(scored)
    for title, _, score in scored:
        print(f"{title} — Match Score: {score}")

if __name__ == "__main__":
    main()
