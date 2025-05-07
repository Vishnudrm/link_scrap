import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import seaborn as sns
import matplotlib.pyplot as plt

# Widened skill list (add more if you want)
skills_list = [
    'Python', 'SQL', 'Excel', 'Power BI', 'Tableau', 'R', 'Machine Learning', 
    'Communication', 'AWS', 'Azure', 'Data Analysis', 'Deep Learning', 
    'Data Visualization', 'Java', 'C++', 'JavaScript', 'Django', 'Flask', 
    'Leadership', 'Problem Solving', 'NoSQL', 'Hadoop', 'Spark', 'Linux', 
    'Docker', 'Kubernetes', 'Cloud', 'Git', 'HTML', 'CSS'
]

# Function to extract skills from text
def extract_skills(description_text):
    found_skills = []
    for skill in skills_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', description_text, re.IGNORECASE):
            found_skills.append(skill)
    return found_skills

# Scrape function
def scrape_linkedin_jobs(query, location, pages=2):
    jobs_data = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for page in range(pages):
        print(f"Scraping page {page+1}...")
        start = page * 25
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={location}&start={start}"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        jobs = soup.find_all('li')

        for job in jobs:
            try:
                title = job.find('h3').text.strip()
                company = job.find('h4').text.strip()
                job_location = job.find('span', class_='job-search-card__location').text.strip()
                job_link = job.find('a')['href']

                # Visit job link to get description
                job_response = requests.get(job_link, headers=headers)
                job_soup = BeautifulSoup(job_response.text, "html.parser")
                desc = job_soup.get_text()

                # Extract skills
                found_skills = extract_skills(desc)

                jobs_data.append({
                    'Title': title,
                    'Company': company,
                    'Location': job_location,
                    'Skills': ', '.join(found_skills),
                    # Removed 'Link'
                })

                time.sleep(1)  # Sleep between job fetches
            except Exception as e:
                print(f"Error fetching job: {e}")
                continue

        time.sleep(2)  # Sleep between page fetches
    return jobs_data

# MAIN
if __name__ == "__main__":
    query = ""  # Empty query for all jobs or set 'developer', 'analyst', 'engineer' etc.
    location = "India"
    pages_to_scrape = 2  # Increase pages if needed

    scraped_data = scrape_linkedin_jobs(query, location, pages=pages_to_scrape)

    # Save to CSV without Link
    df = pd.DataFrame(scraped_data)
    df.to_csv('linkedin_jobs_cleaned.csv', index=False)
    print("\n✅ Scraping Completed and Cleaned Data Saved as 'linkedin_jobs_cleaned.csv'.")

    # --------- Data Analysis Part ----------

    # Expand rows by Skills
    skills_expanded = df.assign(Skill=df['Skills'].str.split(', ')).explode('Skill')
    skills_expanded = skills_expanded.dropna(subset=['Skill'])

    # Top 10 Skills Overall
    top_skills = skills_expanded['Skill'].value_counts().head(10).index.tolist()

    # Create pivot table for heatmap
    heatmap_data = skills_expanded[skills_expanded['Skill'].isin(top_skills)]
    pivot = heatmap_data.pivot_table(index='Location', columns='Skill', aggfunc='size', fill_value=0)

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, annot=True, fmt='d', cmap="YlGnBu")
    plt.title('Top 10 Skills Demand by City')
    plt.xlabel('Skills')
    plt.ylabel('City')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

    # Skill vs Role Matrix
    role_skill_matrix = skills_expanded.pivot_table(index='Skill', columns='Title', aggfunc='size', fill_value=0)
    role_skill_matrix.to_excel('skill_vs_role_matrix_cleaned.xlsx')
    print("\n✅ Skill vs Role Matrix saved as 'skill_vs_role_matrix_cleaned.xlsx'.")
