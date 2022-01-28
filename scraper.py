import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords


# Used to store the number of tokens for each URL
numOfTokenPerURL = {}

urls = set()   # set that stores all urls

# boolean function that returns if the url is stored in urls or not
def isUniquePage(url):
    str = ""
    for c in url:
        if c != "#":
            str += c
        else:
            break

    if str in urls:
        return False
    return True

# returns number of unique urls from url set
def numOfUniqueUrls(url_set):
    return len(urls)

# void function that adds url if it's unique
def addUniquePage(url):
    if isUniquePage(url):
        urls.add(url)

# Returns the URL with the most words/tokens in that page
def longestPage():
    return max(numOfTokenPerURL, key=numOfTokenPerURL.get)

def addFreqDist(text):
    pass

def addSubdomains(url):
    pass



def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    links = []

    if not resp.error:
        htmlContent = resp.raw_response.content

        # creates the soup object to extract all the text
        soup = BeautifulSoup(htmlContent,'html.parser')

        # extract all the links in the document
        for link in soup.find_all('a'):
            if is_valid(link):
                links.append(link.get('href'))

        # get all text from the document in one string
        fullText = soup.get_text().lower()

        # tokenizer that only tokenizes lower case words including apostrophes
        # and hyphenated words
        tokenizer = RegexpTokenizer('[a-z]+?-?[a-z]+')
        tokens = tokenizer.tokenize(fullText)

        # filter out the stop words according to nltk
        filteredTokens = [word for word in tokens if word not in stopwords]

        # add words top frequency dictionary

        
        # Adding in the url with number of words to numOfTokenPerURL
        # numOfTokenPerURL used later to find the longest URL by word count
        # within addUniquePage function - Ayako
        numOfTokenPerURL[resp.url] = filteredTokens.len()


    else:
        print("An error occurred while attempting to access the page.\n")

    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # TODO: check if valid domain and that we haven't crawled it before (look at fragment of URl)
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
