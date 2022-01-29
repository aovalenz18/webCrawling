import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import urllib3
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from collections import OrderedDict

subDomains = OrderedDict()
from collections import Counter

# dict containing text of each URL
urlFullText = dict()

# Used to store the number of tokens for each URL
numOfTokenPerURL = {}

urls = set()   # set that stores all urls

def removeFragment(url):
    url = url.split('#')
    return url[0]

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

# Gets the 50 most common words in the entire set of pages crawled,
# ignoring stop words
def addFreqDist(urlTextDict):
    allPages = ""

    # Parse all of the urls and their associated text and add it 
    # to a single string
    for text in urlTextDict.values():
        allPages += text + " "
    
    # Create a list of all of the tokens encountered
    splitPages = allPages.split()

    # Pass the list of tokens into a counter object
    pagesCounter = Counter(splitPages)

    # Call the most_common() function from the Counter
    # library that gets the most common words in the
    # counter object
    freqList = pagesCounter.most_common(50)

    return freqList


def isSubdomain(url):
    isMatch = re.match('(https?:\/\/[a-z]+.ics.uci.edu)',url)
    return isMatch


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
    if resp.status == 200:
        htmlContent = resp.raw_response.content

        # creates the soup object to extract all the text
        soup = BeautifulSoup(htmlContent,'html.parser')


        # get all text from the document in one string
        fullText = soup.get_text().lower()

        # tokenizer that only tokenizes lower case words including apostrophes
        # and hyphenated words


        # TODO: might have to change it to og tokenizer

        tokenizer = RegexpTokenizer('[a-z]+?-?[a-z]+')
        tokens = tokenizer.tokenize(fullText)

        # filter out the stop words according to nltk
        filteredTokens = [word for word in tokens if word not in stopwords.words('english')]


        # add words to frequency dictionary
        urlFullText[url] = " ".join(filteredTokens)

        
        # Adding in the url with number of words to numOfTokenPerURL
        # numOfTokenPerURL used later to find the longest URL by word count
        # within addUniquePage function - Ayako
        numOfTokenPerURL[resp.url] = len(filteredTokens)


        # Check if the page has high textual information content
        if len(filteredTokens) <= 20 or len(htmlContent) > 10000000:
            pass
        else:
            # extract all the links in the document
            for link in soup.find_all('a'):

                if isSubdomain(url):
                    if url not in subDomains:
                        subDomains[url] = 1
                    else:
                        subDomains[url] += 1
                if is_valid(link.get('href')) and isUniquePage(link.get('href')):
                    links.append(link.get('href'))
                    urls.add(link.get('href'))

    else:
        print("An error occurred while attempting to access the page.\n")

    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    # TODO: check if valid domain and that we haven't crawled it before (look at fragment of URl)
    try:
        blockedList = ["evoke","wics","ngs","chen-li"]
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if not re.match(r".+\.ics\.uci\.edu", parsed.hostname):
            if not re.match(r".+\.cs\.uci\.edu", parsed.hostname):
                if not re.match(r".+\.informatics\.uci\.edu", parsed.hostname):
                    if not re.match(r".+\.stat\.uci\.edu", parsed.hostname):  
                        if not re.match(r".+today\.uci\.edu", parsed.hostname) and not re.match(r".+department\/information\_computer\_sciences.*", parsed.path.lower()):
                            return False

        for blocked in blockedList:
            match = url.find(blocked)
            if match > -1:
                return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|ppsx"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
       # print ("TypeError")
        return False
