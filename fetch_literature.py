import requests
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import sys
from deep_translator import GoogleTranslator

# Europe PMC API endpoint
EPMC_API_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# Categories and their specific queries
CATEGORIES = {
    "Glutathione & GSH (Production & Strain Improvement)": '("Saccharomyces cerevisiae" OR "baker\'s yeast" OR "S. cerevisiae") AND ("glutathione" OR "GSH") AND ("production" OR "biosynthesis" OR "metabolic engineering" OR "strain improvement" OR "overproduction" OR "fermentation" OR "yield")',
    "NAD+ & Precursors (Production & Strain Improvement)": '("Saccharomyces cerevisiae" OR "baker\'s yeast" OR "S. cerevisiae") AND ("NMN" OR "Nicotinamide mononucleotide" OR "NR" OR "Nicotinamide riboside" OR "NAD" OR "NAD+" OR "NADH" OR "Nicotinamide adenine dinucleotide" OR "NAM" OR "Nicotinamide") AND ("production" OR "biosynthesis" OR "metabolic engineering" OR "strain improvement" OR "overproduction" OR "fermentation" OR "yield")',
    "Gene Editing (Novel Tools & Methods)": '("Saccharomyces cerevisiae" OR "baker\'s yeast" OR "S. cerevisiae") AND ("gene editing" OR "CRISPR" OR "CRISPR/Cas9" OR "Cas9" OR "TALEN" OR "ZFN") AND ("novel" OR "new" OR "development" OR "toolkit" OR "platform" OR "improved" OR "efficient")'
}

def fetch_recent_papers(query, days=30):
    """
    Fetch papers from Europe PMC for a given query over the past `days` days.
    Europe PMC includes PubMed, PMC, bioRxiv, medRxiv, etc.
    """
    today = datetime.datetime.now()
    past_date = today - datetime.timedelta(days=days)
    
    date_str = f"[{past_date.strftime('%Y-%m-%d')} TO {today.strftime('%Y-%m-%d')}]"
    full_query = f"{query} AND (FIRST_PDATE:{date_str})"
    
    params = {
        "query": full_query,
        "format": "json",
        "resultType": "core", # core includes abstract
        "pageSize": 20
    }
    
    try:
        response = requests.get(EPMC_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("resultList", {}).get("result", [])
    except Exception as e:
        print(f"Error fetching data for query '{query}': {e}")
        return []

def format_html_email(results_by_category):
    """
    Format the results into a clean HTML email.
    """
    html = """
    <html>
    <head>
        <style>
            body { font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { color: #2980b9; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            th { background-color: #f4f6f7; color: #2c3e50; text-align: left; padding: 12px; border: 1px solid #ddd; font-weight: bold; }
            td { padding: 12px; border: 1px solid #ddd; vertical-align: top; }
            .title { font-size: 15px; font-weight: bold; color: #2c3e50; }
            .authors { font-size: 13px; color: #7f8c8d; margin-top: 5px; }
            .abstract { font-size: 14px; text-align: justify; line-height: 1.5; }
            .date { font-size: 13px; color: #e67e22; font-weight: bold; white-space: nowrap; }
            .link-btn { display: inline-block; background: #3498db; color: #fff; text-decoration: none; padding: 6px 10px; border-radius: 3px; font-size: 12px; margin-top: 10px; }
            .link-btn:hover { background: #2980b9; }
            .no-papers { color: #7f8c8d; font-style: italic; }
        </style>
    </head>
    <body>
        <h1>🧬 S. cerevisiae Monthly Literature Update</h1>
        <p>지난 한 달(30일) 동안 새롭게 등록된 효모 관련 논문들을 요약한 리포트입니다.</p>
    """
    
    total_papers = 0
    for category, papers in results_by_category.items():
        html += f"<h2>📌 {category}</h2>"
        if not papers:
            html += "<p class='no-papers'>이번 기간에는 해당 카테고리에 새로운 논문이 없습니다.</p>"
            continue
            
        html += """
        <table border="1" cellpadding="10" style="width: 100%; border-collapse: collapse; margin-top: 15px; border-color: #ccc; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background-color: #f4f6f7;">
                    <th style="width: 25%; color: #2c3e50; text-align: left; padding: 12px; font-weight: bold; border: 1px solid #ccc;">논문제목 (영어)</th>
                    <th style="width: 60%; color: #2c3e50; text-align: left; padding: 12px; font-weight: bold; border: 1px solid #ccc;">Abstract (핵심 요약)</th>
                    <th style="width: 15%; color: #2c3e50; text-align: left; padding: 12px; font-weight: bold; border: 1px solid #ccc;">발행년도</th>
                </tr>
            </thead>
            <tbody>
        """
            
        for paper in papers:
            total_papers += 1
            title = paper.get('title', 'No Title Available')
            authors = paper.get('authorString', 'Authors not listed')
            abstract_eng = paper.get('abstractText', 'No abstract available.')
            doi = paper.get('doi')
            pmid = paper.get('pmid')
            pub_date = paper.get('firstPublicationDate', paper.get('pubYear', '알 수 없음'))
            
            # Format date (e.g., 2024-05-15 -> 2024년 5월 15일)
            formatted_date = pub_date
            if '-' in pub_date and len(pub_date.split('-')) == 3:
                y, m, d = pub_date.split('-')
                formatted_date = f"{y}년 {int(m)}월 {int(d)}일"
            elif '-' in pub_date and len(pub_date.split('-')) == 2:
                y, m = pub_date.split('-')
                formatted_date = f"{y}년 {int(m)}월"
            elif len(pub_date) == 4 and pub_date.isdigit():
                formatted_date = f"{pub_date}년"
                
            # Summarize and Translate abstract
            abstract_kor = "요약 정보가 없습니다."
            if abstract_eng != 'No abstract available.':
                # Keep first 800 chars and last 600 chars to ensure background and conclusion are included
                if len(abstract_eng) > 1500:
                    abstract_eng_summary = abstract_eng[:800] + " [...중략...] " + abstract_eng[-600:]
                else:
                    abstract_eng_summary = abstract_eng
                    
                try:
                    abstract_kor = GoogleTranslator(source='auto', target='ko').translate(abstract_eng_summary)
                    abstract_kor = abstract_kor.replace('[...중략...]', '<br><br><span style="color:#7f8c8d; font-size:12px;">[...중간 내용 생략...]</span><br>')
                except Exception as e:
                    abstract_kor = f"(번역 오류) {abstract_eng_summary}"
            
            link = f"https://doi.org/{doi}" if doi else (f"https://pubmed.ncbi.nlm.nih.gov/{pmid}" if pmid else "#")
            
            html += f"""
                <tr>
                    <td style="padding: 12px; vertical-align: top; border: 1px solid #ccc;">
                        <div class="title">{title}</div>
                        <div class="authors">{authors}</div>
                        <a href="{link}" class="link-btn" target="_blank">원문 보기</a>
                    </td>
                    <td style="padding: 12px; vertical-align: top; border: 1px solid #ccc;">
                        <div class="abstract">{abstract_kor}</div>
                    </td>
                    <td style="padding: 12px; vertical-align: top; border: 1px solid #ccc;">
                        <div class="date">{formatted_date}</div>
                    </td>
                </tr>
            """
            
        html += "</tbody></table>"
            
    html += """
        <br><hr>
        <p style="font-size: 12px; color: #95a5a6; text-align: center;">Automatically generated by S. cerevisiae Literature Updater using Europe PMC API.</p>
    </body>
    </html>
    """
    return html, total_papers

def send_email(html_content, total_papers):
    sender_email = os.environ.get("EMAIL_SENDER")
    sender_password = os.environ.get("EMAIL_PASSWORD")
    receiver_email = os.environ.get("EMAIL_RECEIVER")
    
    if not all([sender_email, sender_password, receiver_email]):
        print("Email credentials are not set in environment variables.")
        return
        
    msg = MIMEMultipart("alternative")
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    msg["Subject"] = f"[{today_str}] S. cerevisiae Monthly Literature Update ({total_papers} new)"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    
    part = MIMEText(html_content, "html")
    msg.attach(part)
    
    try:
        # Using Naver SMTP
        server = smtplib.SMTP_SSL("smtp.naver.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    print("Starting S. cerevisiae literature update process...")
    results_by_category = {}
    
    for category, query in CATEGORIES.items():
        print(f"Fetching data for: {category}")
        papers = fetch_recent_papers(query)
        results_by_category[category] = papers
        print(f"Found {len(papers)} papers for {category}.")
        
    html_content, total_papers = format_html_email(results_by_category)
    
    if total_papers > 0:
        send_email(html_content, total_papers)
    else:
        print("No new papers found across all categories. Not sending email to avoid spam.")

if __name__ == "__main__":
    main()
