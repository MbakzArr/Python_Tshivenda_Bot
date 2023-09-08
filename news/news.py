import random
import requests
from bs4 import BeautifulSoup


# Function to get news or article from the internet
def get_random_news():
    # URL of the website you want to scrape
    url = 'https://www.limpopomirror.co.za/articles/venda'

    print("Bot may take time to respond...")

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the elements
        articles = soup.find_all('div', class_='art')

        # Random article
        index = random.randint(0, len(articles) - 1)

        # noinspection PyBroadException
        try:
            title = articles[index].find('h3').text.strip()
            date = articles[index].find('span', class_="date").text.strip()
            author = "Unknown"
            content = articles[index].find('div', class_="syn").find('p').text.strip()

            if title is None:
                return get_random_news()
            else:
                return f"""
                        Date: {date}
                        Author: {author}
                        Title: {title}
                        Content: {content}
                        """
        except:
            return get_random_news()
