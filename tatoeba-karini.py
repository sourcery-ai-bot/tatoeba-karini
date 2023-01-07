import webbrowser
import argparse
import os
import csv
import requests
import bs4
import tarfile


# --------------------------
# find and store real path

realPath = os.path.dirname(os.path.realpath(__file__))

# --------------------------
# Functions for the main LOCAL search

# The main search stuff

sentences = []
translationsList = []


def findTranslation(register, inLanguageS, toLanguageS, termInArgS):

    global translationID
    global toLanguage
    global translationsList
    global testUhuList
    global testCheckID

    with open(f'{realPath}/links.csv') as links:
        linksList = csv.reader(links, delimiter='\t')

        for line in linksList:
            if line[0] == register:
                testCheckID = line[1]
                checkTranslation(
                    testCheckID, inLanguageS, toLanguageS, termInArgS)
                continue


def checkTranslation(possibleID, inLanguageS, toLanguageS, termInArgS):
    global sentences
    global translationsList

    with open(f'{realPath}/sentences.csv') as sentencesListing:
        sentencesList = csv.reader(sentencesListing, delimiter='\t')
        for row in sentencesList:
            if row[0] == possibleID and toLanguageS == row[1]:
                translationsList.append(row)
                print(sentences[-1])
                print(translationsList[-1], '\n\n')
                continue


def findTermTranslatedtoLang(inLanguageS, toLanguageS, termInArgS):
    with open(f'{realPath}/sentences.csv') as sentencesListing:
        sentencesList = csv.reader(sentencesListing, delimiter='\t')
        global sentences
        global translationsList

        for row in sentencesList:
            if row[1] == inLanguageS and termInArgS in row[2]:
                sentences.append(row)
                findTranslation(row[0], inLanguageS, toLanguageS, termInArgS)
# Define argument function


def browserWrapper(fromLanguage, toLanguage, term):
    toReference = '&to='

    # Join everything to perform the search
    search = f'{term}&from={fromLanguage}{toReference}{toLanguage}'

    # Open the browser
    webbrowser.open(
        f'https://tatoeba.org/eng/sentences/search?query={search}', new=2
    )


def downloadWrapper(downloadFile):
    def downloadTool():
        with open(realPath + downloadFile + '.tar.bz2', 'wb') as theFile:
            print('Downloading the ',
                  downloadFile, 'file, in the \'.tar.bz2\' format.')
            print('Please wait.')
            res = requests.get('http://downloads.tatoeba.org/exports/' +
                               downloadFile + '.tar.bz2')
            res.raise_for_status()
            if not res.ok:
                print('Download failed.')
            for block in res.iter_content(1024):
                theFile.write(block)

            print('Download finished.\n\n')

    def uncompressTool():
        print('\n\nUncompressing the', downloadFile, 'file. Please wait.')
        untarFile = tarfile.open(realPath + downloadFile + '.tar.bz2', 'r:bz2')
        untarFile.extractall(realPath)
        untarFile.close()
        print('File uncompressed and ready to use.\n')

    if downloadFile in ['sentences', 'links']:
        pass
    elif downloadFile != 'sentences' or downloadFile != 'links':
        print(
            "Wrong file name. Please, choose between 'sentences' and 'links'.")
        print("Consult the README file to learn more about their usage.")
        return

    print("""
            \nYou will be downloading this file directly
            from https://tatoeba.org/eng/downloads.
            """)
    print('Keep in mind that this file is released under CC-BY.')
    print("""
            But if you would like more information about the file,
            check the link above.
            """)
    print('You should also keep in mind that this file can be around 100mb.')
    print('\nThe file will be downloaded and uncompressed.')
    print('\n\nWould you like to proceed? (y/n)')

    askForDownload = input('> ')

    if askForDownload.lower() in ['yes', 'y']:
        downloadTool()
        uncompressTool()

    else:
        print("""
                \n\nNo problems. You can always download and
                extract the files manually.
              """)
        print('Just head to https://tatoeba.org/eng/downloads.\n')


def idWrapper(sentenceId):
    """
    Open Tatoeba.org in a new tab searching by sentence's ID, just in case.
    Use it to get more information about the sentence.
    """
    webbrowser.open(f'https://tatoeba.org/eng/sentences/show/{sentenceId}', new=2)


def findWrapper(inLanguageF, termInArgF):

    # Make use of the 'sentences.csv' file to to find a sentence containing
    # a term in an language

    # findWrapper variables
    with open(f'{realPath}/sentences.csv') as listFile:
        readList = csv.reader(listFile, delimiter='\t')

        # function responsible for making the search AND looping the matches
        def findTermInLang():
            foundedTerm = [
                row
                for row in readList
                if row[1] == inLanguageF and termInArgF in row[2]
            ]

            for row in foundedTerm:
                print(row)

        findTermInLang()


def listAbbreviationWrapper(searchPattern):
    with open(f'{realPath}/abbreviationList.csv') as abbreviationList:
        abbList = csv.reader(abbreviationList, delimiter='\t')
        abbreviation = [row for row in abbList if searchPattern in row]
        print(abbreviation)


# Fetching
def requestGet(search):
    return requests.get(search)


def requestPaginationInput(value):
    userInput = input(value)
    if userInput == "y":
        return("y")
    elif userInput == "n":
        return("n")
    else:
        return(print('Invalid input.'))


def requestPagination(search):
    res = requestGet(search)
    return requestPrint(res)


def requestPrint(value):
    res = value
    res.raise_for_status()

    ttbksoup = bs4.BeautifulSoup(res.text, 'lxml')
    elements = ttbksoup.find_all('div', class_='sentence translations'.split())

    try:
        pagination = ttbksoup.find('md-icon', class_='next')
        if pagination is None:
            print("\n".join("{}".format(el.find(
                'div', class_='text').get_text()) for el in elements), '\n')
            return(False)
        else:
            print("\n".join("{}".format(el.find(
                'div', class_='text').get_text()) for el in elements), '\n')
            paginationHref = pagination.find('a', href=True)
            return(paginationHref.get('href'))

    except AttributeError:
            pass


def requestWrapper(fromLanguage, toLanguage, term):
    urlBase = 'https://tatoeba.org'
    searchBase = '/eng/sentences/search?'
    fromReference = 'from='
    toReference = '&to='
    query = '&query='

    # Join everything to perform the search

    search = urlBase + searchBase + fromReference + fromLanguage +\
        toReference + toLanguage + query + term
    res = requestGet(search)

    pagination = requestPrint(res)

    while pagination is not False:
        nextPage = requestPaginationInput('Next page? (y/n) ')
        if nextPage == "n":
            return(print('Ok, no pagination this time...'))
        elif nextPage == "y":
            search = urlBase + pagination
            pagination = requestPagination(search)
    return


def searchWrapper(inLanguageS, toLanguageS, termInArgS):
    findTermTranslatedtoLang(inLanguageS, toLanguageS, termInArgS)

# --------------------------
# Define command line menu function


def main():

    # Set commanline argments

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-b", help="Open a browser and show the result", nargs=3
    )

    parser.add_argument("-d", help="Download files from Tatoeba.org in order to \
            perform offline searchs", nargs=1)

    parser.add_argument("-f", help="Find sentence containing term in a specific \
            language", nargs=2)

    parser.add_argument("-i", help="Open Tatoeba on the browser searching by \
            sentence's ID", nargs=1)

    parser.add_argument("-l", help="List languages and their abbreviation used by \
            Tatoeba", nargs=1)

    parser.add_argument("-r", help="Request data from Tatoeba.org, works as the \
            main search on the homepage", nargs=3)

    parser.add_argument("-s", help="Search for sentences containing term in a \
            specific language and it the counterparts of the sentence \
            in another \
            language", nargs=3)

    args = parser.parse_args()

    if args.b:
        fromLanguage = args.b[0]
        toLanguage = args.b[1]
        term = args.b[2]
        browserWrapper(fromLanguage, toLanguage, term)

    elif args.f:
        inLanguageF = args.f[0]
        termInArgF = args.f[1]
        findWrapper(inLanguageF, termInArgF)

    elif args.d:
        downloadFile = args.d[0]
        downloadWrapper(downloadFile)

    elif args.i:
        sentenceId = args.i[0]
        idWrapper(sentenceId)

    elif args.l:
        searchPattern = args.l[0]
        listAbbreviationWrapper(searchPattern)

    elif args.r:
        fromLanguage = args.r[0]
        toLanguage = args.r[1]
        term = args.r[2]
        requestWrapper(fromLanguage, toLanguage, term)

    elif args.s:
        inLanguageS = args.s[0]
        toLanguageS = args.s[1]
        termInArgS = args.s[2]
        searchWrapper(inLanguageS, toLanguageS, termInArgS)

    else:
        print("Ooops!")


# ---------------------------
# call the main

if __name__ == '__main__':
    main()
