import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])

    #print(f"{transition_model(corpus, "3.html", DAMPING)}")
    #sys.exit()

    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages



def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    probability_distribution = {}

    for p in corpus:
        probability_distribution[p] = (1 - damping_factor) * (1 / len(corpus))

    pages_linked = corpus.get(page)
    if len(pages_linked) == 0:
        for v in probability_distribution.values():
            v = v + (damping_factor * (1 / len(probability_distribution)))
    else:
        for p in pages_linked:
            probability_p = probability_distribution.get(p)
            probability_distribution.update({p: probability_p + (damping_factor * (1 / len(pages_linked)))})

    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    sample_set = {}
    for k in corpus.keys():
        sample_set[k] = 0

    sample_index = 0
    page = random.choice(list(corpus.keys()))
    while sample_index < n:

        page_rank = sample_set.get(page)
        sample_set.update({page: page_rank + 1})

        probability_distribution = transition_model(corpus, page, damping_factor)
        page = random.choices(list(probability_distribution.keys()), weights=list(probability_distribution.values()), k=1)[0]

        sample_index = sample_index + 1

    pageranks = {}
    for k, v in sample_set.items():
        pageranks[k] = v / n

    return pageranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    pageranks = {}
    for k in corpus.keys():
        pageranks[k] = 1 / len(corpus)

    while 1:

        pageranks_new = {}
        for p in pageranks.keys():

            pagerank_new = (1 - damping_factor) / len(corpus)
            for k, v in corpus.items():
                if p in v:
                    pagerank_new = pagerank_new + (damping_factor * pageranks.get(k) / len(corpus.get(k)))
                elif len(v) == 0:
                    pagerank_new = pagerank_new + (damping_factor * pageranks.get(k) / len(corpus))

            pageranks_new[p] = pagerank_new

        should_break = True
        for k, v in pageranks.items():
            new_v = pageranks_new.get(k)
            if abs(v - new_v) > 0.001:
                should_break = False

        if should_break:
            break

        pageranks = pageranks_new

    return pageranks


if __name__ == "__main__":
    main()
