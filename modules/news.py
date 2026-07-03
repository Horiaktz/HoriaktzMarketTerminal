import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import re

class NewsManager:
    def __init__(self):
        # Folosim feed-urile de Google News filtrate direct după publisheri pentru acuratețe max
        self.sources = {
            'Reuters': 'https://news.google.com/rss/search?q=when:1d+source:Reuters&hl=en-US&gl=US&ceid=US:en',
            'CNBC': 'https://news.google.com/rss/search?q=when:1d+source:CNBC&hl=en-US&gl=US&ceid=US:en',
            'Bloomberg': 'https://news.google.com/rss/search?q=when:1d+source:Bloomberg&hl=en-US&gl=US&ceid=US:en'
        }

    def _parse_rss_date(self, date_str):
        """Converteste formatul RSS (ex: Fri, 03 Jul 2026 09:30:00 GMT) in HH:MM"""
        try:
            # Tăiem fusul orar pentru parsing simplu
            clean_date = date_str.split(' GMT')[0].strip()
            # Format standard RSS: Sat, 04 Jul 2026 14:20:00
            dt = datetime.strptime(clean_date, "%a, %d %b %Y %H:%M:%S")
            return dt.strftime("%H:%M")
        except Exception:
            return datetime.now().strftime("%H:%M")

    def _clean_title(self, title, source_name):
        """Scoate numele publisher-ului de la finalul titlului generat de Google News"""
        return re.sub(rf'\s*-\s*{source_name}$', '', title, flags=re.IGNORECASE).strip()

    def get_latest_news(self):
        news_by_source = {}
        
        for source_name, url in self.sources.items():
            news_by_source[source_name] = []
            try:
                # Facem cererea cu un User-Agent ca să nu fim blocați de Google
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    xml_data = response.read()
                
                root = ET.fromstring(xml_data)
                # Luăm toate elementele <item> din XML (articolele)
                items = root.findall('.//item')
                
                for item in items[:3]: # Ne oprim la top 3 cele mai recente
                    title = item.find('title').text if item.find('title') is not None else ''
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    
                    if title:
                        clean_title = self._clean_title(title, source_name)
                        time_str = self._parse_rss_date(pub_date)
                        
                        news_by_source[source_name].append({
                            'title': clean_title,
                            'time': time_str
                        })
            except Exception:
                # Dacă pică un feed (ex: Bloomberg are momente când blochează request-urile), punem o știre de siguranță
                t_now = datetime.now().strftime('%H:%M')
                news_by_source[source_name].append({
                    'title': f"Failed to fetch live feed. Checking alternative financial pipelines...",
                    'time': t_now
                })

            # Dacă lista a rămas goală din orice alt motiv
            if not news_by_source[source_name]:
                t_now = datetime.now().strftime('%H:%M')
                news_by_source[source_name].append({
                    'title': "No new stories published in the last hour.",
                    'time': t_now
                })
                
        return news_by_source