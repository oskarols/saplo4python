from saploapi import SaploJSONClient, SaploError
import sys

def main():
    """
    In this example we send in an article to the API, and then extract the tags from it.
    To do this first of all we need to create a corpus - which is a collection of texts.
    In the Saplo API, an article or document always exists inside of a corpus.
    
    Secondly we create the article itself, putting it inside of the corpus that we first created.
    
    Finally, we request the tags themselves. Depending on text length this might take a while.
    
    Instructions:
    1. Insert your api key and secret key in the variables named just that.
    2. Run the script. (one method would be to write 'python examples_tag.py' in the commandline when in the same directory as the file) 
    3. Change the value of the article_body variable to change the text that the tags are extracted from. 
    """
    
    # Firstly we need to authenticate to the API using the API-key and the Secret-key you received by mail.
    api_key = ""
    secret_key = ""
    
    if (api_key and secret_key):
        # Below creates the API-object that we use to send and recieve things from the Saplo API
        api = SaploJSONClient(api_key, secret_key)
    else:
        print "Welcome to the tags example!"
        print "You need to set your api_key and secret_key in the code for the example file to work."
        sys.exit(0)
        
    # This is the text that is sent to the API (using the addArticle-method a couple of rows below).
    # If you want to get the tags from another text, just change the value of article_body.
    article_body = "When the original television series was canceled in 1969, Star Trek creator Gene Roddenberry lobbied Paramount to continue the franchise through a film. The success of the series in syndication convinced the studio to begin work on a feature film in 1975. A series of writers attempted to craft a suitably epic script, but the attempts did not satisfy Paramount, so the studio scrapped the project in 1977. Paramount instead planned on returning the franchise to its roots with a new television series, Star Trek: Phase II. The box office success of Close Encounters of the Third Kind convinced Paramount that science fiction films other than Star Wars could do well at the box office, so the studio canceled production of Phase II and resumed its attempts at making a Star Trek film. In 1978, Paramount assembled the largest press conference held at the studio since the 1950s to announce that double Academy winning director Robert Wise would helm a $15 million film adaptation of the television series."
    
    
    # This creates a new corpus in the API. Note how we used 'en' to note that it's for english texts.
    response = api.createCorpus('Example Corpus', 'This is an example corpus.', 'en')
    corpusID = response['result']['corpusId']
    
    # This adds an article to the API
    response = api.addArticle(corpusID, '', '', article_body, '', '', '', 'en')
    articleID = response['result']['articleId']
    
    # Extracts the tags from the inserted article, with a maximum wait time of 50 seconds.
    response = api.getEntityTags(corpusID, articleID, 50)
    tags = response['result']
    
    # After the example is run, we remove the corpus. Note that this also deletes the articles.
    # In normal usage you wouldn't want to remove your corpuses, instead you'd want to save the ID
    # in your own local database so you can use them later.
    # We only remove it in the example since there's a maximum limit of corpuses for each user.
    api.deleteCorpus(corpusID)
    
    delimiter = ("#" * 50) + "\n"
    
    print delimiter
    print "This is the article we're using: \n\n", article_body
    print delimiter
    
    print "These are the extracted tags: \n"
    for tag in tags:
        print tag['tagWord']


if __name__ == "__main__":
    main()