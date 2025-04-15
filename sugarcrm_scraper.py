import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Set up the app UI
st.title("SugarCRM Reseller Directory Scraper")
st.markdown("Scrapes partner data from the SugarCRM directory and exports to CSV.")

num_pages = st.number_input("How many pages do you want to scrape?", min_value=1, max_value=20, value=5)

if st.button("Scrape Now"):
    base_url = "https://www.sugarcrm.com/uk/partner-type/reseller/page/{}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    all_partners = []

    @st.cache_data(show_spinner=False)
    def get_partner_details(url):
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            location = soup.select_one(".partner-location")
            description = soup.select_one(".partner-detail__body p")
            return {
                "location": location.text.strip() if location else "N/A",
                "description": description.text.strip() if description else "N/A"
            }
        except:
            return {"location": "Error", "description": "Error"}

    with st.spinner("Scraping data..."):
        for page in range(1, num_pages + 1):
            url = base_url.format(page)
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select(".partner-card")

            for card in cards:
                name_tag = card.select_one(".partner-card__title")
                link_tag = card.find("a", href=True)
                name = name_tag.text.strip() if name_tag else "N/A"
                link = link_tag['href'] if link_tag else "N/A"
                details = get_partner_details(link)

                all_partners.append({
                    "name": name,
                    "link": link,
                    "location": details["location"],
                    "description": details["description"]
                })
                time.sleep(0.5)  # Be nice to the server

    df = pd.DataFrame(all_partners)
    st.success(f"Scraped {len(df)} partners.")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", data=csv, file_name="sugarcrm_reseller_partners.csv", mime="text/csv")
