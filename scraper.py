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

    if resp.status == 200 and resp.raw_response:
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')

        if not soup:
            pass
        ps = soup.find_all('p') + soup.find_all('pre')
        if not ps:
            pass
        max_word = 0
        if len(ps) < 20 and len(soup.find_all('a')) < 20:
            for p in ps:
                word = len(p.get_text().strip().split())
                if word > max_word:
                    max_word = word
                if word > 25:
                    print(url, "  satisfied with ", word)
                    break
            else:
                print(url, " not satisfied with ", max_word)
                pass

        counter.process_soup(soup, urlparse(resp.url))  # pass soup content to the counter
        # get urls from the 'href' attribute within <a> tags e.g., <a href='...'>
        for a_tag in soup.find_all('a'):
            # get absolute url by joining the two if necessary
            link = urljoin(url, a_tag.get('href'))

            # remove the fragment from the url and append to the list
            links.append(urldefrag(link).url)

    else:
        pass  # todo when the status is not 200

    return links


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False


        domains = re.compile(r"""
            .*\.(
            ics.uci.edu|
            cs.uci.edu|
            informatics.uci.edu|
            stat.uci.edu|
            today.uci.edu/department/information_computer_sciences)$
            """, re.VERBOSE)

        # Check domain
        if not domains.match(parsed.netloc):
            return False

        # Check file extension 
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|odp|mpg|bib|ppsx|war|java|xml|h|cc)$", parsed.path.lower()):
            return False
        q = urlparse(url).query
        p = urlparse(url).path
        l = urlparse(url).netloc
        if q:
            if any(i in q for i in ("limit", "order", "sort", "filter", "&format=txt")):
                return False
        if any(i in p for i in ("stayconnected","personal/personal", "/seminar/Nanda/", "eppstein/pix", "/pdf", "asterix")):
            return False
        if l == "archive.ics.uci.edu":
            return False
        if l == "flamingo.ics.uci.edu" and "/src" in p:
            return False
        if (l == "swiki.ics.uci.edu" or "wiki.ics.uci.edu") and "do" in q:
            return False

        #print_url(url, True)

        return True

    except TypeError:
        print("TypeError for ", parsed)
        raise


def print_url(url, valid):
    """For debugging the url."""
    if valid:
        print("Valid: ", url)
    else:
        print("  Bad: ", url)

