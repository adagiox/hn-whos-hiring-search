import urllib.request
import requests
import json
import sys
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup

search_dict = {
    '1': ['San Francisco', 'Python', 'Intern'],
    '2': ['Seattle', 'Python', 'Intern']
}

results = []

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

def get_latest_hiring_post():
    url = 'https://hacker-news.firebaseio.com/v0/user/whoishiring.json'
    r = requests.get(url)
    posts = json.loads(r.text)
    base_post = 'https://hacker-news.firebaseio.com/v0/item'
    for post in posts['submitted']:
        check = requests.get(f'{base_post}/{post}.json')
        check = json.loads(check.text)
        if 'Who is hiring?' in check['title']:
            return post

def search_comments(search_query):
    base_items = 'https://hacker-news.firebaseio.com/v0/item'
    whoishiring = get_latest_hiring_post()
    comments = requests.get(f'{base_items}/{whoishiring}.json')
    for comment in json.loads(comments.text)['kids']:
        comment_id = comment
        comment = requests.get(f'{base_items}/{comment}.json')
        comment = json.loads(comment.text)
        if not comment is None and not 'deleted' in comment:
            comment = comment['text']
            comment_text = BeautifulSoup(comment, 'html.parser').get_text(' ')
            scored_dict = score_all(comment_text, search_query)
            p = ""
            total_score = 0
            for key, value in scored_dict.items():
                total_score += scored_dict[key]
                p += f"{scored_dict[key]:<.{4}}\t {search_dict[key]}\n"
            if total_score > 0:
                res = f"{p}\n\n{comment_text}\n==============="
                results.append((total_score, res, comment_id))

if __name__ == '__main__':
    search_comments(search_dict)
    results.sort(key=lambda tup: tup[0], reverse=True)
    with open('out.txt', 'w+') as f:
        for r in results:
            f.write(f'https://news.ycombinator.com/item?id={r[2]}' + '\n' + 'Score: ' + str(r[0]) + '\n' + r[1] + '\n')