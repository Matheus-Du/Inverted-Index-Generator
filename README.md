# Inverted-Index-Generator
Python application that contains 2 programs to build and query a custom inverted index. Index.py builds an inverted index from a given corpus of JSON objects and Query.py allows for a user to search using keywords and phrases before returning a list of results from the index ranked according to how well they match the query.

## Installation

- Make sure you have `Python 3.7+` installed on your machine
- navigate the `src/` directory to run the index and query programs

## Instructions

1. Before running either program, ensure you are in the `src/` directory.
2. To generate the inverted index, run the following command:
    - ```python index.py [complete path to corpus] [complete path to folder where the index folder will be created]```
        - i.e. ```python index.py C:/Users/user/Documents/CMPUT361/HW2/corpus C:/Users/user/Documents/CMPUT361/HW2/``` will generate the `index` file inside `HW2`
    - ensure the path to the index folder location already exists as the program will create the index folder inside the specified folder
    - ensure the paths provided are complete paths and not relative paths
    - ensure all documents in the corpus contain a valid, unique document ID, have 2+ zones (including the docID), and that each zone's content is not empty
3. The index folder will be generated in the specified folder and will be named `index` and will be a folder containing the following files:
    - `index.tsv` - contains the inverted index, sorted by term
    - `docIndex.tsv` - contains the document index, sorted by document ID
4. To run a search query against the generated index, run the following command from the `src/` directory:
    - ```python query.py [complete path to index folder] [number of results to return] [keyword and phrase queries]```
        - i.e. ```python query.py C:/Users/user/Documents/CMPUT361/HW2/index 10 :top gun: maverick goose``` will run the query in `:top gun: maverick goose` against the indexes in `HW2/index`
    - if you choose to include any search phrases, ensure that the entire phrase is enclosed by a pair of phrase delimiters 
        - i.e. `:top gun:`
    - ensure both the inverted index and document index files exist in the folder being pointed to by the command
    - ensure the path to the index folder is the complete, and not relative, path
    - ensure the delimiters for all search phrases (':') are at the start/end of the first/last term in the phrase query (not separated by whitespace)
       - i.e. `:top gun:` is a correct phrase query, but `: top gun :` is not
    - if you choose to include search phrases in the query, be aware that the program will return only documents containing the entire query
5. The query program will output the results of the query to the terminal in the following order:
    ```
    Number of documents considered when searching for matching phrases
    Number of documents that have a non-zero cosine similarity score
    The top [number of results to return] documents that have a non-zero cosine similarity score, sorted in descending order by similarity score
    ```

## Data Structures and Algorithms

### Index.py

- the creation of the inverted index and document index is done in unison, ensuring that we iterate through the list of documents in the corpus only once (O(n) complexity)
- the inverted index is a dictionary where the key is the term and the value is a dictionary containing the document frequency and the postings list
    - the postings list is represented as an array of docIDs since the entire list must be converted to a string before being written to the index file, so a more complex/efficient data structure is not useful
    - using a dictionary makes the code more readable and structures the data in a simple and efficient manner
    - the dictionary is also the most efficient data structure for the index since Python renders a dictionary as a hashmap, so the average lookup time is O(1), which is much more efficient than the lookup time for a list since we need to lookup each token in the index to see if it has already been generated
- the document index is a dictionary where the key is the docID and the value is a string containing all tokens found in the document
    - this data structure is no more efficient than storing these 2 values in a 2D array since we never need to lookup data in this dictionary, but using a dictionary makes the code more readable and allows us to use the same logic for both the inverted index and document index

### Query.py

- the creation of the index and document index is done by retrieving all the necessary data from the two generated index files, then converting the data into 2 dictionaries, one for the inverted index and one for the document index
    - the inverted index is a dictionary where the key is the term and the value is a dictionary containing the document frequency and the postings list
    - the document index is a dictionary where the key is the docID and the value is a string containing all tokens found in the document
    - this is done to ensure that we only need to read the index files once, and that we can use the same logic for both the inverted index and document index
        - we need to read the entirety of both files at once since there is no way to search .tsv files in Python without first reading the contents into a data structure
    - parsing both index files as dictionaries allows for fast lookup since Python renders dictionaries as hashmaps, so average lookup time is O(1), which is more efficient than any other data structure
- the score for each document is calculated using a version of the FastCosineScore function outlined in Figure 7.1 from the textbook
    - first, a dictionary of document IDs and the length of their corresponding vector is created for each document being considered
    - then, we iterate through each keyword provided by the user (including keywords in search phrases), assigning each keyword a weight of `1/n` (where `n = number of keywords provided by the user`)
    - for each keyword, we retrieve its postings list from the inverted index and calculate the intersection between the doc's postings list and all the documents to be considered
    - for each doc in the intersection, we add the weight of the keyword to the doc's score
    - after all keywords have been processed, we calculate the cosine similarity score for each document originally passed to the function
        - the cosine similarity score of a document is calculated using the formula `cosine_score = doc_score/doc_length`
            - where `doc_score = the score of the document as previously calculated` and `doc_length = the number of tokens in the document`
    - the documents are then sorted in descending order by their cosine similarity score and the top `n` documents are returned
        - where `n = number of results to return as specified by the user`

## Error Handling

### Index.py
- if the user does not provide the correct number of arguments, the program will exit with an error message
- if the corpus folder does not exist, the program will exit with an error message
- if the path to the index folder location does not exist, the program will exit with an error message
- if the index folder already exists, the program will exit with an error message
- if a document in the corpus does not contain a valid, unique document ID, the program will exit with an error message
- if a document in the corpus does not contain 2+ zones (including the docID field), the program will exit with an error message
- if a zone in a document does not contain any content, the program will exit with an error message

### Query.py
- if the user does not provide the correct number of arguments, the program will exit with an error message
- if the inverted index and document index files do not exist at the specified path, the program will exit with an error message
- if the search phrase delimiter is not at the start/end of the first/last term in the phrase query, the program will exit with an error message
