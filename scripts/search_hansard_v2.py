import os
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.ourcommons.ca"

KEYWORDS = [
    r"\bcharit(y|ies|able|ables)\b",
    r"\bvolunt(eer|eers|eers'|ary|eerism)\b",
    r"\bNGOs?'?\b",
    r"\bnon-?for-?profits?'?\b",
    r"\bnot-?for-?profits?'?\b",
    r"\bnon-?profits?'?\b",
    r"\bnon-?governmental\b",
    r"\bdonations?'?\b",
    r"\bnon-?profit sector\b",
    r"\bnot-for-profit sector\b",
    r"\bcharitable sector\b",
    r"\bvoluntary sector\b",
    r"\bcivil society\b",
    r"\bcommunity (organization|organizations|group|groups)\b",
    r"\blocal (organization|organizations)\b",
    r"\bfaith (group|groups)\b",
    r"\bservice providers?'?\b",
    r"\bfood banks?'?\b",
    r"\bsocial enterprises?'?\b",
    r"\bgrant recipients?'?\b",
    r"\bbeneficiar(y|ies)\b",
    r"\bsettlement services\b"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SPEAKER_PATTERN = re.compile(
    r"(?:Hon\.|Mr\.|Ms\.|Mrs\.|Dr\.|Senator)\s+[A-Z][a-zA-L\.\s'\-]+(?:\s*\(.*?\))?",
    re.IGNORECASE
)

def clean_text(text: str) -> str:
    return " ".join(text.split())

def extract_sitting_date(soup) -> str:
    header_text = soup.get_text()[:4000]
    date_match = re.search(
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
        header_text
    )
    if date_match:
        return date_match.group(0)
    return datetime.now().strftime("%B %d, %Y")

def extract_speaker_name(tag) -> str:
    speaker_node = tag.find(class_=re.compile(r"speaker|member-name|person", re.I))
    if speaker_node:
        name = clean_text(speaker_node.get_text())
        if name:
            return name

    match = SPEAKER_PATTERN.search(tag.get_text()[:200])
    if match:
        return match.group(0).strip()

    return "Unknown Speaker"

def get_recent_hansard_urls(session, max_issues=12):
    """Finds the current sitting number and generates consecutive target URLs."""
    urls = []
    latest_url = "https://www.ourcommons.ca/documentviewer/en/house/latest/hansard"
    
    try:
        resp = session.get(latest_url, headers=HEADERS, timeout=25, allow_redirects=True)
        final_url = resp.url
        
        # Check if the final URL resolved to a numbered sitting (e.g. sitting-156)
        match = re.search(r"/(\d+-\d+)/house/sitting-(\d+)/hansard", final_url, re.I)
        if match:
            session_id = match.group(1) # e.g. 45-1
            latest_num = int(match.group(2))
            
            # Generate the last N consecutive sitting URLs
            for num in range(latest_num, max(0, latest_num - max_issues), -1):
                urls.append(f"https://www.ourcommons.ca/documentviewer/en/{session_id}/house/sitting-{num}/hansard")
        else:
            urls.append(latest_url)
    except Exception as e:
        print(f"Notice determining current sitting: {e}")
        urls.append(latest_url)
        
    return urls

def generate_styled_html(df: pd.DataFrame, output_file: str):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Parliamentary Sector Monitoring Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; color: #333; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #0056b3; padding-bottom: 8px; }}
            .summary {{ margin-bottom: 15px; font-size: 15px; color: #555; }}
            table {{ border-collapse: collapse; width: 100%; background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-top: 15px; table-layout: fixed; }}
            th, td {{ border: 1px solid #dee2e6; padding: 10px 12px; text-align: left; vertical-align: top; font-size: 14px; word-wrap: break-word; }}
            th {{ background-color: #0056b3; color: white; font-weight: bold; position: sticky; top: 0; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            col:nth-child(1) {{ width: 150px; }}
            col:nth-child(2) {{ width: 150px; }}
            col:nth-child(3) {{ width: 220px; }}
            col:nth-child(4) {{ width: 130px; }}
            col:nth-child(5) {{ width: auto;  }}
            col:nth-child(6) {{ width: 90px;  }}
            td:nth-child(3) {{ font-weight: bold; color: #2c3e50; }}
            td:nth-child(4) {{ font-weight: bold; color: #d9534f; }}
            a {{ color: #0056b3; text-decoration: none; font-weight: bold; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h2>🇨🇦 Federal Parliamentary Sector Monitoring History</h2>
        <div class="summary">
            Total Accumulated Mentions: <strong>{len(df)}</strong> | Last Updated: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M')} EST</strong>
        </div>
        <table>
            <colgroup>
                <col><col><col><col><col><col>
            </colgroup>
            <thead>
                <tr>
                    <th>Sitting Date</th>
                    <th>Source</th>
                    <th>Speaker</th>
                    <th>Matched Term</th>
                    <th>Context Snippet</th>
                    <th>Direct Quote Link</th>
                </tr>
            </thead>
            <tbody>
    """
    for _, row in df.iterrows():
        url_display = row['quote_url']
        if not str(url_display).startswith('<a'):
            url_display = f'<a href="{url_display}" target="_blank">Jump to Quote</a>'

        html_content += f"""
                <tr>
                    <td>{row['sitting_date']}</td>
                    <td>{row['source']}</td>
                    <td>{row['speaker']}</td>
                    <td>{row['matched_term']}</td>
                    <td>{row['context_snippet']}</td>
                    <td>{url_display}</td>
                </tr>
        """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

def fetch_and_parse():
    results = []
    seen_matches = set()
    compiled_regexes = [(kw, re.compile(kw, re.IGNORECASE)) for kw in KEYWORDS]

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    hoc_urls = get_recent_hansard_urls(session, max_issues=12)
    target_list = [{"name": "House of Commons (Hansard)", "url": u} for u in hoc_urls]
    target_list.append({"name": "Senate Debates", "url": "https://sencanada.ca/en/in-the-chamber/debates/"})

    for source in target_list:
        print(f"\nFetching: {source['name']} -> {source['url']}")
        try:
            resp = session.get(source["url"], headers=HEADERS, timeout=25)
            if resp.status_code != 200:
                print(f"  [NOTICE] Skipped (status {resp.status_code}): {source['url']}")
                continue
        except Exception as e:
            print(f"  [NOTICE] Connection skipped for {source['url']}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        sitting_date = extract_sitting_date(soup)

        for tag in soup(["header", "footer", "nav", "script", "style", "form"]):
            tag.decompose()

        for div in soup.find_all("div", class_=re.compile(r"PublicationSelector|Header|Navigation", re.I)):
            div.decompose()

        interventions = soup.find_all("div", class_=re.compile(r"intervention", re.I))
        if not interventions:
            interventions = soup.find_all(['p', 'div'])

        current_speaker = "Unknown Speaker"

        for block in interventions:
            paragraphs = block.find_all('p')
            if not paragraphs:
                paragraphs = [block]

            anchor_id = block.get("id") or block.get("data-id")
            quote_url = f"{source['url']}#{anchor_id}" if anchor_id else source['url']

            detected_speaker = extract_speaker_name(block)
            if detected_speaker != "Unknown Speaker":
                current_speaker = detected_speaker

            for p in paragraphs:
                p_text = clean_text(p.get_text())
                if len(p_text) < 15 or len(p_text) > 50000:
                    continue

                if "Publication Selector by Date" in p_text or "Parliamentary Historical Resources" in p_text:
                    continue

                sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', p_text) if s.strip()]

                for idx, sentence in enumerate(sentences):
                    sentence_key = (source["name"], sitting_date, current_speaker, sentence)
                    if sentence_key in seen_matches:
                        continue

                    for raw_keyword, regex in compiled_regexes:
                        match = regex.search(sentence)
                        if match:
                            prev_s = sentences[idx - 1] if idx > 0 else ""
                            next_s = sentences[idx + 1] if idx < len(sentences) - 1 else ""
                            context_snippet = f"{prev_s} [{sentence}] {next_s}".strip()
                            matched_word = match.group(0)

                            seen_matches.add(sentence_key)

                            results.append({
                                "sitting_date": sitting_date,
                                "source": source["name"],
                                "speaker": current_speaker,
                                "matched_term": matched_word,
                                "context_snippet": context_snippet,
                                "quote_url": quote_url
                            })
                            break

    os.makedirs("data", exist_ok=True)
    csv_path = "data/hansard_mentions.csv"
    html_path = "index.html"

    df_new = pd.DataFrame(results) if results else pd.DataFrame(columns=["sitting_date", "source", "speaker", "matched_term", "context_snippet", "quote_url"])

    if os.path.exists(csv_path):
        try:
            existing_df = pd.read_csv(csv_path)
            combined_df = pd.concat([existing_df, df_new], ignore_index=True)
            combined_df.drop_duplicates(subset=["sitting_date", "source", "speaker", "context_snippet"], inplace=True)
            combined_df.to_csv(csv_path, index=False)
        except Exception:
            df_new.to_csv(csv_path, index=False)
    else:
        df_new.to_csv(csv_path, index=False)

    if os.path.exists(csv_path):
        full_df = pd.read_csv(csv_path)
        full_df = full_df.iloc[::-1].reset_index(drop=True)
        generate_styled_html(full_df, html_path)
        print(f"\nReport updated: {html_path} ({len(full_df)} total mentions across recent sitting issues)")

if __name__ == "__main__":
    fetch_and_parse()