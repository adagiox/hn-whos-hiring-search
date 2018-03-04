import urllib.request
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup

# @TODO():  Better scoring algorithm, i.e. multiple matches increase score
# @TODO():  Sort output by most matches/best score
# @TODO():  User input of search terms

search_dict = {
    '1': ['San Francisco', 'Python', 'Intern'],
    '2': ['Seattle', 'Python', 'Intern'],
    '3': ['Blockchain'],
    '4': ['SQL']
}


def score_all(comment_text, search_all_dict):
    score_dict = {}
    for search_key, search_list in search_all_dict.items():
        score_dict[search_key] = score_from_search_list(comment_text, search_list)
    return score_dict


def score_from_search_list(comment_text, search_list):
    score = 0.0
    for search_term in search_list:
        search_score = fuzz.partial_ratio(comment_text, search_term)
        if search_score > 50:
            score += (search_score / len(search_list))
    return score


def search_comments(search_query):
    url = 'https://news.ycombinator.com/item?id=16492994'
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    for comment in soup.find_all('span', attrs={'class': 'c00'}):
        comment_text_stripped = comment.get_text(' ')
        comment_text_stripped = comment_text_stripped.encode('utf-8')
        comment_text_stripped = comment_text_stripped.decode('latin-1')
        scored_dict = score_all(comment_text_stripped, search_query)
        p = ""
        for key, value in scored_dict.items():
            if scored_dict[key] > 0:
                p += f"{scored_dict[key]:<.{4}}\t {search_dict[key]}\n"
        if p:
            print(f"{comment_text_stripped}{p}===============\n")


if __name__ == '__main__':
    search_comments(search_dict)

