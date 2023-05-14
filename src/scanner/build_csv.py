import re
import shutil
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import spacy
from collections import Counter
from tabulate import tabulate
from spacy.language import Language
import os
import csv
import openai

CSV_OUTPUT = True
USE_STATS = False

class normalizer():
    def __init__(self):
        self.emoj_ptrn = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u'\U00010000-\U0010ffff'
            u"\u200d"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\u3030"
            u"\ufe0f"
            "]+", re.UNICODE)
        
        self.url_ptrn = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.facebook_ptrn = re.compile(r'\BFacebook\B|\BFacebook\b|\bFacebook\B')
        self.more_ptrn = re.compile(r'\BMore\B|\BMore\b|\bMore\B')
        self.numeric_date_ptrn = re.compile(r'\b(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4})\b')
        self.textual_date_ptrn = re.compile(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b|\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', re.IGNORECASE)
        self.monthes_ptrn = re.compile(r'\b(December|January|August|September|June|July|October|November|February|March|May|April)\b',
                                                 re.IGNORECASE)
        
    def parse(self, cnt):
        soup = BeautifulSoup(cnt, 'html.parser')
        
        for tag in soup(["script", "style", "meta", "code", "svg", "path", "button", "img", "option", "select"]): 
            tag.decompose()
        
        elems_remove = soup.find_all(attrs={'aria-hidden': 'true'})
        elems_remove += soup.find_all('span', attrs={'aria-hidden': 'true'})
        elems_remove += soup.find_all('div', attrs={'aria-hidden': 'true'})
        elems_remove += soup.find_all('div', attrs={'role': 'Button'})
        elems_remove += soup.find_all('svg')
        elems_remove += soup.find_all('code')
        elems_remove += soup.find_all('img')
        elems_remove += soup.find_all(attrs={'role': 'status'})
        elems_remove += soup.find_all(attrs={'class': ['presence-entity__indicator',
                                                       'profile-creator-shared-feed-update__anchor']})
        elems_remove += soup.find_all('h2', attrs={'class': 'visually-hidden'})
        elems_remove += soup.find_all('label', attrs={'for': 'globalfooter-select_language'})
        elems_remove += soup.find_all('p', attrs={'class': 'global-footer__label'})
        elems_remove += soup.find_all('section', attrs={'id': 'ember895'})
        elems_remove += soup.find_all('footer')
        elems_remove += soup.find_all('a', attrs={'class': 'app-aware-link'})
        
        for div in elems_remove:
            div.decompose()
            
        # delete any irrelevant content
        specific_elems = soup.find_all(string="To learn more about")
        specific_elems += soup.find_all(string="FacebookFacebook")
        for elem in specific_elems:
            elem.parent.decompose()
            
        rawtext = soup.get_text()
        lines = (line.strip() for line in rawtext.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        text = re.sub(self.emoj_ptrn, '', text)
        text = re.sub(self.url_ptrn, '', text)
        text = re.sub(self.facebook_ptrn, '', text)
        text = re.sub(self.more_ptrn, '', text)
        text = re.sub(self.numeric_date_ptrn, '', text)
        text = re.sub(self.textual_date_ptrn, '', text)
        text = re.sub(self.monthes_ptrn, '', text)
        text = text.replace("\n", " ").replace("\r", " ")
        return text.strip()


class tokenizer():
    def __init__(self):
        self.nlp = spacy.load('en_core_web_lg')
        
        self.removable_tags = ['_SP', 'NFP', '.', ',', 'SYM', ':', 'HYPH', 'DT',
                               'TO', 'PRP$', 'PRP', 'IN', '$', 'CD', ' ', '-RRB-', '-LRB-',
                               'XX']
        self.removable_tokens = ['&', '-', '.', ':)', '#', '`', '’', '*']

    def analyze(self, cnt):
        doc = self.nlp(cnt)
        table = []
        for word in doc:
            if not word.is_stop \
                    and word.is_alpha \
                    and word.tag_ not in self.removable_tags \
                    and word.text not in self.removable_tokens \
                    and len(word.text) <= 30:
                table.append([word.text.strip(), word.tag_, spacy.explain(word.tag_), word.sentiment,
                              word.cluster, word.is_stop])
        return table
    
    def print(self, table):
        print(tabulate(table, headers=['Text', 'Tag', 'Explain', 'Setiment', 'Cluster', 'IsStop']))
         
    
def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    datadir = os.path.join(current_dir, 'data')
    outputdir = os.path.join(current_dir, 'output')
    if os.path.exists(outputdir):
        print("remove old output dir")
        shutil.rmtree(outputdir)
    os.mkdir(outputdir)
    print(outputdir, "created")
        
    normalizer_ = normalizer()
    tokenizer_ = tokenizer()
    
    for root, dirs, files in os.walk(datadir):
        if root == datadir:
            continue
        
        csv_data=[]
        for file in files:
            filepath = os.path.join(root, file)
            print("processing set", filepath)
            tag, file_extension = os.path.splitext(os.path.basename(filepath))
            with open(filepath, mode='r', encoding="utf8") as f:
                content = f.read()
                norm_text = normalizer_.parse(content)
                csv_data.append([tag, norm_text])
                if USE_STATS:
                    token_table = tokenizer_.analyze(norm_text)
                    tokenizer_.print(token_table)
        if CSV_OUTPUT:
            csv_file_path = os.path.join(outputdir, os.path.basename(os.path.normpath(root)) + ".csv")
            print("csv_file_path", csv_file_path)
            with open(csv_file_path, 'w', encoding="utf8", newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(csv_data)
                
                



if __name__ == "__main__":
    main()
