import sys
import json
import os
import re
import time


def generateIndex(corpus):
    # TODO: add functionality for document index (format: {docID: text from all zones}) (sorted by docID)
    """
    This function takes the corpus as a collection of JSON objects, generates a list of tokens from each zone, and creates
    an inverted index and a document index from the tokens.

    Parameters:
        corpus (list): a list of JSON objects representing the corpus, where each object is separated into it's doc_id and zones
    
    Returns:
        indexes (list): 2 dictionaries for the inverted index and the document index
    """

    print("generating index dictionaries...")
    docIDs = []
    index = {}
    docIndex = {}

    # iterate through each document in the corpus
    for doc in corpus:
        docId = None
        docString = ""

        # check if the document contains less than 2 zones (incl. the doc_id zone) and if so, print an error message and exit the program
        if len(doc.keys()) <= 1:
            print("Error: document must contain a docID and at least one zone")
            sys.exit()
            
        # iterate through each zone in the document
        for key in doc.keys():
            # if the zone content is empty, continue to the next zone
            if doc[key] == None or doc[key] == "":
                print("Error: zone content cannot be empty")
                sys.exit()
            # if the current zone contains the doc_id, save the doc_id and continue to the next zone
            if key == "doc_id":
                docId = int(doc[key])
                # check if the docID has already been found
                if docId in docIDs:
                    print("Error: duplicate docIDs found")
                    sys.exit()
                docIDs.append(docId)
                continue
            
            # iterate through each word in the zone, tokenize it, and add it to the index
            for token in doc[key].split():
                token = re.sub(r'[^\w\s]', '', token).lower()
                if token != "":
                    # append the token to the docString
                    docString += token + " "
                    # if the token already exists in the index, add the doc_id to the postings list if it is not already there
                    if token in index:
                        if docId not in index[token]["postings"]:
                            index[token]["postings"].append(docId)
                            index[token]["postings"].sort()
                            index[token]["DF"] += 1
                    # if the token does not exist in the index, add it to the index along with it's frequency and postings list
                    else:
                        index[token] = {"DF": 1, "postings": [docId]}
        
        # check if docID was found and add the docString to the docIndex
        if docId == None:
            print("Error: no docID found")
            sys.exit()
        docIndex[docId] = docString
            
    # sort the index alphabetically and return the sorted index
    index = dict(sorted(index.items()))
    docIndex = dict(sorted(docIndex.items()))
    return [index, docIndex]


def generateIndexFiles(indexFileLoc, indexes):
    """
    This function creates an index folder and populates it with index files for each zone

    Parameters:
        indexFileLoc (str): the path where the user wants the index folder to be created
        indexes (list): dictionaries containing the generated inverted index and the document index
    """

    print("generating index files...")
    # create the index folder
    indexFileLoc = indexFileLoc + "\\index"
    try:
        os.mkdir(indexFileLoc)
    except FileExistsError:
        print("Error: index folder already exists")
        return

    # create the index file
    try:
        indexFile = open("{}\\index.tsv".format(indexFileLoc), "w", encoding="utf-8")
    except FileExistsError:
        print("Error: could not create the index files")
        return
    # create the document index file
    try:
        docIndexFile = open("{}\\docIndex.tsv".format(indexFileLoc), "w", encoding="utf-8")
    except FileExistsError:
        print("Error: could not create the index files")
        return

    # write the document index to the file
    for doc in indexes[1]:
        docIndexFile.write("{}\t{}\n".format(doc, indexes[1][doc]))
    docIndexFile.close()

    # write the index to the file
    for token in indexes[0]:
        indexFile.write("{}\t{}\t{}\n".format(token, str(indexes[0][token]["DF"]), str(indexes[0][token]["postings"])))
    indexFile.close()
        
    print("Index file generation complete.")


def buildIndex(corpusPath, indexPath):
    """
    This function gets the corpus file and passes it to the index generator before writing the completed index to the index file
    
    Parameters:
        corpusPath (str): the path to the corpus file as specified by the user
        indexPath (str): the path to the folder where the index folder will be created, as specified by the user
    """

    # open the corpus and index files
    try:
        corpusFile = open(corpusPath, "r", encoding="utf-8")
    except FileNotFoundError:
        print("Error: could not find the corpus file")
        return
    # generate a list of JSON objects from the corpus file
    corpus = json.load(corpusFile)
    corpusFile.close()

    # generate the index folder and files
    generateIndexFiles(indexPath, generateIndex(corpus))


def main(args):
    """
    The main function of the program

    Parameters:
        args (list): both the location of the corpus file and the location of where the index folder will be created
    """
    # check if the user wants to see the help message
    if "-h" in args or "--help" in args or len(args) == 0:
        print("Usage: python main.py [path to corpus] [path to index folder]")
        return

    # check if the user provided both the corpus and the index folder
    if len(args) != 2:
        print("Error: please provide both the corpus and the index folder")
        return

    # get the corpus and the index folder
    corpusPath = args[0]
    indexPath = args[1]
    buildIndex(corpusPath, indexPath)


if __name__ == "__main__":
    # call the main function with all provided cli arguments
    main(sys.argv[1:])
