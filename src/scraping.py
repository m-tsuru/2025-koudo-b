import requests
import os
import re
from matplotlib import pyplot as plt
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv()
token = os.getenv('GITHUB_API_TOKEN')

def fetch_data(url: str) -> dict:
    """
    Fetch data from a given URL.

    :param url: The URL to fetch data from.
    :return: JSON response from the URL.
    """
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    return response.json()

def fetch_data_from_github(url: str, github_token: str | None = token) -> tuple[dict, dict]:
    """
    Fetch data from a GitHub API endpoint using a personal access token.

    :param url: The GitHub API endpoint URL.
    :param github_token: Personal access token for GitHub API authentication.
    :return: JSON response from the GitHub API.
    """

    if github_token is not None:
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    else:
        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error fetching data from GitHub: {response.status_code} - {response.text}")

    return dict(response.headers), response.json()

def get_top_repositories(language: str, sort: str = 'stars', order: str = 'desc', per_page: int = 100) -> list:
    """
    Get top repositories for a given programming language from GitHub.

    :param language: The programming language to filter repositories by.
    :param sort: The sorting criteria (default is 'stars').
    :param order: The order of sorting (default is 'desc').
    :param per_page: Number of repositories to return per page (default is 100).
    :return: List of top repositories.
    """
    url = f"https://api.github.com/search/repositories?q=language:{language}&sort={sort}&order={order}&per_page={per_page}"
    headers, data = fetch_data_from_github(url)

    if not data or 'items' not in data:
        raise Exception("No items found in the response.")

    return data['items']

def count_from_link(url: str) -> int:
    """
    Count the number of items with the 'Link' header.
    GitHub API returns paginated results, but not counts items of the all pages.
    This function uses the pagination information in the 'Link' header to count the total number of items.

    :param url: The GitHub API endpoint URL to count items from.
    :return: Number of items in the 'Link' header.
    """

    headers, data = fetch_data_from_github(url)
    if not data:
        raise Exception("No data found in the response.")

    count_per_page = len(data)

    if 'Link' not in headers:
        raise Exception("No 'Link' header found in the response.")

    link_header = headers['Link']
    match = re.search(r'<([^>]+)>;\s*rel="last"', link_header)
    if match:
        last_url = match.group(1)
        print("last_url:", last_url)
    else:
        raise Exception("No 'last' link found in the 'Link' header.")
    last_url_parse = urlparse(last_url)
    last_page_num = parse_qs(last_url_parse.query).get('page', [None])[0]
    print("last_page_num:", last_page_num)

    if last_page_num is None:
        raise Exception("Could not determine the last page number from the 'Link' header.")

    _, last_page_rawdata = fetch_data_from_github(url=last_url)
    last_page_count = len(last_page_rawdata)

    count = count_per_page * (int(last_page_num) - 1) + last_page_count

    return count

if __name__ == "__main__":
    mode = 0 # Change this to run different modes

    if mode == 0:
        langs = ['python', 'TypeScript', 'javascript', 'java', 'c++']
        colors = ['blue', 'orange', 'green', 'red', 'purple']

        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(1,1,1)

        for lang in langs:
            tops = get_top_repositories(lang)
            x = []
            y = []
            for i in tops:
                x.append(i['id'])
                y.append(i['stargazers_count'])
            ax.scatter(x, y, label=lang, color=colors[langs.index(lang)])

        print("x: ", x)
        print("y: ", y)

        # ax.set_xlim(0, 400000000)
        # ax.set_ylim(0, 200000)
        ax.set_xlabel('Repository ID')
        ax.set_ylabel('Stars')
        ax.set_title('Top Repository by Language')
        ax.legend(loc='upper right')

        fig.show()
        fig.savefig("result_1-1.png")
