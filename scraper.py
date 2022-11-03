import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urldefrag, urljoin


def scraper(url, resp, counter):
    links = extract_next_links(url, resp, counter)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp, counter):
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

    if resp.status == 200 and resp.raw_response:  # process the page only on 200 success
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        # pass soup content to the counter
        low_info = counter.process_soup(soup, urlparse(resp.url))

        if low_info:
            return links

        # get urls from the 'href' attribute within <a> tags e.g., <a href='...'>
        for a_tag in soup.find_all('a'):
            # get absolute url by joining the two if necessary
            link = urljoin(url, a_tag.get('href'))
            # remove the fragment from the url and append to the list
            links.append(urldefrag(link).url)

    return links


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        query = parsed.query.lower()

        if parsed.scheme not in set(["http", "https"]):
            return False

        # Check for valid domain
        domains = re.compile(r"""
            .*\.(
            ics.uci.edu|
            cs.uci.edu|
            informatics.uci.edu|
            stat.uci.edu)$
            """, re.VERBOSE)
        if not domains.match(domain):
            return False

        # Check domain & traps
        if domain == "flamingo.ics.uci.edu" and ("/src" in path or "/.svn" in path):
            return False
        if domain in ["swiki.ics.uci.edu", "wiki.ics.uci.edu"] and "do" in query:
            return False
        if domain in ["archive.ics.uci.edu", "cbcl.ics.uci.edu"] and query != '':
            return False
        if domain == "wics.ics.uci.edu" and ("event" in path):
            return False

        # Check path
        if any(i in path for i in ["login", "img", "pdf"]):
            return False
        # Check repetitive path
        if re.search(r'\b([/\w]+)(\1){2,}\b', path):
            return False

        # Check file extension
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|odc"
            + r"|png|tiff?|mid|mp2|mp3|mp4|mat|z|cpp|ipynb"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|py|bam|m|r"
            + r"|thmx|mso|arff|rtf|jar|csv|db|txt"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz|odp|mpg|bib|ppsx|war|java|xml|h|cc?|apk|sql)$", path):
            return False

        # Check query
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|odc"
            + r"|png|tiff?|mid|mp2|mp3|mp4|mat|z|cpp|ipynb"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|py|bam|m|r"
            + r"|thmx|mso|arff|rtf|jar|csv|db|txt"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz|odp|mpg|bib|ppsx|war|java|xml|h|cc?|apk|sql)$", query):
            return False
        if query and any(i in query for i in ["version=", "format=txt", "share=", "login"]):
            return False

        return True

    except:
        return False
