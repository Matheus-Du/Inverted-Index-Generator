import sys


def cosineScore(index, docIndex, keywords, docs, numResults):
    """
    Calculates the fast-cosine score of each document in the list of documents that contain at least one of the search phrases.
    Uses the algorithm described in Figure 7.1 of the textbook.

    Parameters:
        index (dict): the inverted index
        docIndex (dict): the document index
        keywords (list): the list of search keywords
        docs (list): the list of docIDs that contain at least one of the search phrases
        numResults (int): the number of results to return
    
    Returns:
        scores (dict): the dictionary of docIDs and their corresponding cosine scores
        docCount (int): the number of documents with non-zero cosine scores
    """
    
    scores = {}
    lengths = {}

    for doc in docs:
        scores[doc] = 0
        # set the length of the document to the number of terms in the document
        lengths[doc] = float(len(docIndex[doc].split()))

    for term in keywords:
        termWeight = 1/len(keywords)
        try:
            # get the postings list for the current term
            postings = index[term]["postings"]
        except KeyError:
            # if the term does not exist in the index, skip it
            continue
        # get the intersection of the postings list for the current term and the list of possible matching docs
        intersect = list(set(postings) & set(docs))
        for doc in intersect:
            try:
                scores[doc] += termWeight
            except KeyError:
                scores[doc] = termWeight

    cosineScores = {}
    for doc in lengths.keys():
        # calculate the cosine score for each document
        cosineScores[doc] = scores[doc]/lengths[doc]
    # sort the scores in descending order
    cosineScores = {k: v for k, v in sorted(cosineScores.items(), key=lambda item: item[1], reverse=True) if v > 0}

    # return the top numResults results and the number of documents with non-zero scores
    return [dict(list(cosineScores.items())[0:numResults]), len(cosineScores)]


def getPhraseResults(index, docIndex, phrases):
    """
    Collects a postings list of all docs that contain at least one of the provided search phrases.

    Parameters:
        index (dict): the inverted index
        docIndex (dict): the document index
        phrases (list): the list of search phrases

    Returns:
        phraseResults (list): the list of docIDs that contain at least one of the search phrases
        consideredDocs (int): the number of documents considered when searching for the search phrases
    """
    phraseResults = []
    consideredDocs = []

    # if the list of phrases is empty, return a list of all docIDs
    if len(phrases) == 0:
        return [sorted(list(docIndex.keys())), len(docIndex.keys())]

    for phrase in phrases:
        docs = docIndex.keys()
        # split the phrase into individual terms
        terms = phrase.split()
        # get the postings list for the first term in the phrase
        for term in terms:
            try:
                postings = index[term]["postings"]
            except KeyError:
                # if the term does not exist in the index discard the phrase
                break    
            # intersect the postings list with the list of possible matching docs
            docs = list(set(docs) & set(postings))

        for doc in docs:
            # iterate through each doc and check if it contains the entire phrase
            if phrase.strip() in docIndex[doc] and doc not in phraseResults:
                # if the doc contains the entire phrase, add it to the list of phrase results
                phraseResults.append(doc)
            if doc not in consideredDocs:
                # if the doc hasn't been considered yet, add it to the list of considered docs
                consideredDocs.append(doc)
        
    return [sorted(phraseResults), len(consideredDocs)]


def buildIndexes(indexPath):
    """
    Takes the path to the index folder and builds the inverted index and the document index using the .tsv files in the index folder

    Parameters:
        indexPath (str): the path to the index folder

    Returns:
        index (dict): the inverted index
        docIndex (dict): the document index
    """

    # create the index and document index dictionaries
    index = {}
    docIndex = {}

    # open the index and document index files
    try:
        indexFile = open("{}\\index.tsv".format(indexPath), "r", encoding="utf-8")
    except FileNotFoundError:
        print("Index file not found. Please run the indexer before running the query engine or make sure the path to the index folder is correct.")
        sys.exit()
    try:
        docIndexFile = open("{}\\docIndex.tsv".format(indexPath), "r", encoding="utf-8")
    except FileNotFoundError:
        print("Document index file not found. Please run the indexer before running the query engine or make sure the path to the index folder is correct.")
        sys.exit()

    # read the index file line by line
    for line in indexFile:
        [token, DF, postings] = line.split("\t")
        # remove the brackets and delimiters from the postings list
        postings = postings[1:len(postings) - 2].split(", ")
        # iterate through each posting, convert it to an integer, and create a token entry in the index
        postingsInt = []
        for docId in postings:
            postingsInt.append(int(docId))
        index[token] = {"DF": int(DF), "postings": postingsInt}

    # read the document index file line by line
    for line in docIndexFile:
        [docId, docString] = line.split("\t")
        # remove the newline character from the document string and add the document ID and document string to the document index
        docIndex[int(docId)] = docString[:len(docString) - 2]

    return [index, docIndex]


def parseQuery(query):
    """
    Takes the raw list of all the query terms and parses them into search keywords and phrases

    Parameters:
        query (list): the list of all the query terms
    
    Returns:
        keywords (list): the list of all the search keywords
        phrases (list): the list of all the search phrases
    """

    keywords = []
    phrases = []
    phrase = ""
    isPhrase = False

    # iterate through each query term
    for term in query:
        # if the current term is a phrase delimiter, toggle the phrase flag
        if term[0] == ':':
            isPhrase = not isPhrase
            if not isPhrase:
                # if the current term is the end-phrase delimiter, add the phrase to the list of phrases
                phrases.append(phrase.strip())
                phrase = ""
            if len(term) == 1:
                # if the current term is just a phrase delimiter, continue to the next term
                print("Invalid use of phrase delimiter. Make sure there is no space between the phrase delimiter and the first/last term in the phrase.")
                sys.exit()
        if isPhrase:
            # if the phrase flag is true, add the term to the current phrase
            if term[0] == ":":
                # if the current term contains the start-phrase delimiter, check if it is the only term in the phrase
                if term[len(term) - 1] == ":":
                    # if the current term is the only term in the phrase, add it to the list of phrases; otherwise, append it to the current phrase
                    phrase = term[1:len(term) - 1]
                    phrases.append(phrase.strip())
                    phrase = ""
                else: phrase += term[1:] + " "
            elif term[len(term) - 1] == ":":
                # if the current term contains the end-phrase delimiter, append it to the current phrase and add the phrase to the list of phrases
                phrase += term[:len(term) - 1] + " "
                phrases.append(phrase.strip())
                phrase = ""
                isPhrase = False
            else:
                # if the current term is in the middle of the phrase, append it to the current phrase
                phrase += term + " "
        else:
            # if the phrase flag is false, add the term to the list of keywords
            keywords.append(term)

    # return the lists of keywords and phrases
    return [keywords, phrases]


def main(args):
    """
    The main function of the program

    Parameters:
        args (list): the path to the index folder, the number of results to return, and the terms of the search query
    """
    # check if the user wants to see the help message
    if "-h" in args or "--help" in args or len(args) == 0:
        print("Usage: python main.py [path to index folder] [number of documents to return] [query]")
        sys.exit()

    # check if the user provided both the corpus and the index folder
    if len(args) < 3:
        print("Error: please provide a path to the index folder, the number of results to return, and the query")
        sys.exit()

        # ensure the number of documents to return is greater than 0
    try:
        if int(args[1]) <= 0:
            print("Error: please provide a number of results greater than 0")
            sys.exit()
    except ValueError:
        print("Error: make sure the number of results to return (2nd argument provided) is an integer")
        sys.exit()

    # get the corpus, index folder, and search query
    indexPath = args[0]
    numResults = int(args[1])
    query = args[2:]
    # generate the lists of keywords and phrases as well as the inverted index and document index
    [keywords, phrases] = parseQuery(query)
    [index, docIndex] = buildIndexes(indexPath)

    # append all the phrase terms to the list of keywords
    for phrase in phrases:
        keywords += phrase.split()
    
    # Get a list of documents that contain any of the search phrases
    [docs, numDocsConsidered] = getPhraseResults(index, docIndex, phrases)
    # calculate the fast-cosine score of each document
    [scores, nonZeroScoreDocs] = cosineScore(index, docIndex, keywords, docs, numResults)
    
    # print the results as per the assignment specifications
    print("Number of documents considered: " + str(numDocsConsidered))
    print("Number of documents with non-zero cosine scores: " + str(nonZeroScoreDocs))
    for doc in scores.keys():
        print("{}\t{}".format(doc, scores[doc]))


if __name__ == "__main__":
    # call the main function with all provided cli arguments
    main(sys.argv[1:])
