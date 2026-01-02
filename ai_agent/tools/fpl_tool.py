import requests
from bs4 import BeautifulSoup
import sys
from datetime import datetime
import logging

class FPLTool:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def get_news(self) -> str:
        """
        Fetches and prioritizes FPL news from multiple sources.
        Returns a formatted string of the news.
        """
        self.logger.info("Fetching FPL news...")
        items = []
        items.extend(self._fetch_ffscout_news())
        items.extend(self._fetch_allaboutfpl_news())
        items.extend(self._fetch_reddit_fpl())
        items.extend(self._fetch_official_fpl_status())

        if not items:
            return "No news found. Please check your internet connection or the source websites."

        classified = self._prioritize_news(items)
        return self._format_news(classified)

    def _fetch_ffscout_news(self):
        url = "https://www.fantasyfootballscout.co.uk/"
        news_items = []

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            articles = soup.find_all('article')
            for article in articles:
                title_tag = article.find(['h2', 'h3', 'h4'])
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link_tag = article.find('a')
                    link = link_tag['href'] if link_tag else url
                    news_items.append({'source': 'Fantasy Football Scout', 'title': title, 'link': link})
        except Exception as e:
            self.logger.error(f"Error fetching FFScout: {e}")

        return news_items

    def _fetch_allaboutfpl_news(self):
        url = "https://allaboutfpl.com/"
        news_items = []

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            articles = soup.find_all('article')
            for article in articles:
                title_tag = article.find(['h2', 'h3'])
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link_tag = article.find('a')
                    link = link_tag['href'] if link_tag else url
                    news_items.append({'source': 'AllAboutFPL', 'title': title, 'link': link})
        except Exception as e:
            self.logger.error(f"Error fetching AllAboutFPL: {e}")

        return news_items

    def _fetch_reddit_fpl(self):
        url = "https://www.reddit.com/r/FantasyPL/hot.json?limit=10"
        news_items = []

        try:
            reddit_headers = self.headers.copy()
            response = requests.get(url, headers=reddit_headers, timeout=10)
            if response.status_code == 429 or response.status_code == 403:
                self.logger.warning(f"Reddit API blocked request ({response.status_code}). Skipping Reddit source.")
                return news_items

            response.raise_for_status()
            data = response.json()

            for post in data['data']['children']:
                p_data = post['data']
                if not p_data.get('stickied'):
                    news_items.append({
                        'source': 'Reddit r/FantasyPL',
                        'title': p_data['title'],
                        'link': f"https://www.reddit.com{p_data['permalink']}"
                    })
        except Exception as e:
            self.logger.error(f"Error fetching Reddit: {e}")

        return news_items

    def _fetch_official_fpl_status(self):
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        news_items = []

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Check for next deadline
            events = data.get('events', [])
            next_event = next((e for e in events if e['is_next']), None)
            if next_event:
                timestamp = next_event['deadline_time_epoch']
                deadline_dt = datetime.fromtimestamp(timestamp)
                deadline_str = deadline_dt.strftime('%Y-%m-%d %H:%M')

                news_items.append({
                    'source': 'Official FPL',
                    'title': f"Gameweek {next_event['id']} Deadline: {deadline_str}",
                    'link': 'https://fantasy.premierleague.com/'
                })

        except Exception as e:
            self.logger.error(f"Error fetching Official FPL: {e}")

        return news_items

    def _prioritize_news(self, news_items):
        breaking_keywords = ['injury', 'banned', 'suspended', 'confirmed', 'official', 'deadline', 'team news', 'press conference', 'breaking', 'ruled out']
        viral_keywords = ['wildcard', 'free hit', 'triple captain', 'chip', 'price change', 'riser', 'faller', 'hamstring', 'benched', 'rant', 'discussion']
        notable_keywords = ['captain', 'scout picks', 'differentials', 'gameweek', 'gw', 'transfer', 'fixtures', 'analysis', 'guide']
        surprising_keywords = ['shock', 'surprise', 'unexpected', 'record', 'insane', 'crazy', 'unbelievable']

        classified_news = {
            "1) Breaking news and major developments": [],
            "2) Viral stories getting significant attention": [],
            "3) Notable events affecting many people": [],
            "4) Surprising or unusual stories gaining traction": [],
            "Other News": []
        }

        seen_titles = set()

        for item in news_items:
            title = item['title']
            title_lower = title.lower()

            if title in seen_titles:
                continue
            seen_titles.add(title)

            item_str = f"- [{item['source']}] {title}"

            if any(k in title_lower for k in breaking_keywords):
                classified_news["1) Breaking news and major developments"].append(item_str)
            elif any(k in title_lower for k in viral_keywords):
                classified_news["2) Viral stories getting significant attention"].append(item_str)
            elif any(k in title_lower for k in surprising_keywords):
                classified_news["4) Surprising or unusual stories gaining traction"].append(item_str)
            elif any(k in title_lower for k in notable_keywords):
                classified_news["3) Notable events affecting many people"].append(item_str)
            else:
                classified_news["Other News"].append(item_str)

        return classified_news

    def _format_news(self, classified):
        output = ["=== FANTASY PREMIER LEAGUE NEWS ===\n"]

        for category, stories in classified.items():
            if category == "Other News":
                continue

            output.append(f"\n{category}:")
            if stories:
                for story in stories[:5]:
                    output.append(story)
            else:
                output.append("- No major stories found in this category today.")

        if classified["Other News"]:
            output.append(f"\nOther News:")
            for story in classified["Other News"][:3]:
                output.append(story)

        return "\n".join(output)
