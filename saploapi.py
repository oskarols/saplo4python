import json
import urllib
import urllib2

class SaploError(Exception):
        """
        Is thrown when an request to the Saplo API for some reason fails

        All requests to the SaploJSOnClient should catch this exception, and handle it
        """
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)


class SaploJSONClient:
        """
         Saplo JSON Client.
         Handles authentication and json-requests to the saplo API Server.

         All requests to the SaploJSONClient should catch the SaploError that is thrown if a request fails

         Example of request usage: All these requests returns a dictionary that you can use to retrieve data
         try:
                client = SaploJSONClient()
                client.createCorpus("My new Corpus", "Some description text", "sv")
                client.addArticle(corpusId, TitleString, LeadString, BodyString, Date, "someurl.com", "some author")
                client.getEntityTags(corpusId, articleId, waittime)
                client.getSimilarArticles(corpusId, articleId, wait, numberOfResults, minThreshold, maxThreshold)
                client.getCorpusPermission()
        except SaploError, err:
                print err.__str__()
                
        """
        url         = "http://api.saplo.com/rpc/json;jsessionid={token}"
        apikey      = ''
        secretkey   = ''
        token       = ''
                        
        def __init__(self,apikey, secretkey, token=None):
                """
                Initiates the Saplo JSONClient using the secret & api keys
                @type String
                @param Saplo API key
                @type String
                @param Saplo Secret key
                """
                self.apikey     = apikey
                self.secretkey  = secretkey
                self.token      = token
                self.__createSession(self.apikey, self.secretkey)
                
        def getArticle(self,corpusId, articleId):
                """
                Gives information about the saved headline and publish url for a specific article.
                @type number
                @param corpusId - The unique id of the corpus where the article is stored
                @type number
                @param articleId - the id for the article you want information about
                @rtype dictionary
                @return
                        corpusId   Number - The id of the corpus that the article exists in
                        articleId  String - The id for the article you requested
                        headline   String - The headline for the article
                        publishUrl String - The url (if it exists) that are saved for the article
                       
                """
                params = (corpusId, articleId)
                response = self.__doRequest('corpus.getArticle', params)
                return self.__handleJSONResponse(response.read())
                
        def getEntityTags(self,corpusId, articleId, waiton):
                """
                Gives you the persons, organisations and geographical names (places) that are mentioned within an article/text.
                @type number
                @param corpusId  - The unique id for the corpus where the source article is stored.
                @param articleId - The id for the article to which you want to find similar articles.
                @param waitOn    - This param specifies how long you want to wait for a result to be calculated or if you want to just start a search
                        and come back later to fetch the result.
                        We RECOMMEND you to use waitOn = 0. On high load the calculation might not be able to process all requests and then its better
                        to add a search to the queue and fetch the result
                @rtype dictionary
                @return
                        tagId     Number - an id for the result based on your articleId and corpusId. (corpusId + articleId + tagId are a unique combination)
                        tagWord   String - a word that has been recognized as an entity and is represented in the article/text
                        tagTypeId Number - specifies which category a tag has been placed in. 3 = person, 4 = organisation, 5 = geoname (place)
                       
                """
                params = (corpusId, articleId,waiton)
                response = self.__doRequest('tags.getEntityTags', params)
                return self.__handleJSONResponse(response.read())
                
        def getSimilarArticles(self,corpusId, articleId, wait, numberOfResults, minThreshold, maxThreshold):
                """
                Searches the corpus you provide and looking for articles that has a similar semantic meaning as your source article.
                The request gives you a list with a maximum of 50 articles that are similar to the source article.
               
                @type Number
                @param corpusId   - The unique id for the corpus where the source article is stored.
                @type Number
                @param articleId  - The id for the article to which you want to find similar articles.
                @type Number
                @param wait           - This param specifies if you want to wait until a result has been calculated or
                if you want to just start a search and come back later to fetch the result. We RECOMMEND you to use wait = 0.
                On high load the calculation might not be able to process all requests and then its better to add a search to the queue and fetch the result later.
                @type Number
                @param numberOfResults - How many results that will be returned (default 10).
                @type Float
                @param minThreshold - If you only want similar articles that are 50 percent like your source article, provide 0.5 as param.
                @type Float
                @param maxThreshold - If you only want similar articles that are like your source article to a max of 90 %, provide 0.9 as param.

                
                @rtype dictionary
                @return
                        matchId            Number        an id for the result based on your sourceCorpusId and sourceArticleId.
                                (sourceCorpusId + sourceArticleId + matchId are a unique combination)
                        resultCorpusId     Number        id for the corpus where the similar article exists
                        resultArticleId    Number        id for the similar article
                        resultValue        Number    value of how similar the result article is.
                                The scale goes from 0.00 to 1.00. A result of 1 equals the exact same article.
                """

                params = [corpusId, articleId, wait, numberOfResults, minThreshold, maxThreshold]
                response = self.__doRequest('match.getSimilarArticles', params)
                return self.__handleJSONResponse(response.read())
                
        def createCorpus(self,corpusName, corpusDesc, lang):
                """
                Creates a new corpus (container to store articles and texts in) and returns an id to the created corpus.
                A corpus may only contain articles with the same language (i.e. only english texts in the corpus).

                @type String
                @param corpusName - Provide a name for your new corpus.
                @type String
                @param corpusDesc - Provide a description for your new corpus.
                        Use something that describes what the corpus contains (i.e. English blog posts from my personal blog)
                @type String
                @param lang - Specify what language the articles/texts that will be stored in the corpus are written in.
                        English and Swedish are supported and specified according to ISO 639-1 (http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).
                        Swedish = "sv", English = "en".
               
                @rtype dictionary
                @return
                        corpusId    Int        A unique id for your newly created corpus.
                """
                params = (corpusName,corpusDesc,lang)
                response = self.__doRequest('corpus.createCorpus', params)
                return self.__handleJSONResponse(response.read())
                
        def addArticle(self,corpusId, headline, lead, body, publishStart, publishUrl, authors, lang):
                '''
                Add a new article to a corpus.
                If you are adding an article that already exists (the combination of headline+body+publishUrl) then the id for that article will be returned.

                @type  Number
                @param corpusId (required) - The id to the corpus where you want to add your article.
                @type  String
                @param headline (required) - The article headline
                @type  String
                @param lead                - The article lead text
                @type  String
                @param body     (required) - The body text for the article
                @type  date
                @param publishDate         - The date when the article was published (YYYY-MM-DD HH:MM:SS, i.e. 2010-01-24 12:23:44)
                @type  String
                @param publishUrl          - The url for where the article can be found on internet
                @type  String
                @param authors             - The authors of the article or text
                @type  String
                @param lang     (required) - The language for the article.
                        English and Swedish are supported and specified according to ISO 639-1 (http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).
                        Swedish = "sv", English = "en".
                @rtype dictionary
                @return
                        corpusId    Number        A unique corpus id.
                        articleId   Number        The id for the new article.
                '''
                params = (corpusId, headline, lead, body, publishStart, publishUrl, authors,lang)
                response = self.__doRequest('corpus.addArticle', params)
                return self.__handleJSONResponse(response.read())
                
        def getCorpusPermission(self):
                """
                Gives you a list to all corpus ids that you have read or write permission to.


                @rtype Dictionary
                @return
                        corpusId    Int        A unique corpus id.
                        permission    String    The permission you have to the unique corpusId. This can have the values of "read" or "write"
                """
                response = self.__doRequest('corpus.getPermissions',() )
                return self.__handleJSONResponse(response.read())
                
        def getCorpusInfo(self,corpusId):
                """
                Gives you the name, description and the last article id for a specific corpus.

                @type  Number
                @param corpusId The unique id for the corpus you want information about.
                @rtype Dictionary
                @return
                        corpusId        Int        The unique id for the corpus you want information about.
                        corpusName      String    The current name for the corpus
                        corpusDesc      String    The current description for the corpus
                        lang            String    The language that are specified for this corpus
                        lastArticleId   Int    The id for the last article that has been added to the corpus.
                """
                params = [corpusId]
                response = self.__doRequest('corpus.getInfo',params)
                return self.__handleJSONResponse(response.read())
                
        def deleteCorpus(self, corpusId):
            """
            Removes the entire corpus, articles included.
            
            @type Number
            @param corpusId The unique id for the corpus you want to delete.
            @rtype Dictionary
            @return 
                    Bool        Returns whether the corpus was successfully deleted or not.         
            """
            params = [corpusId]
            response = self.__doRequest('corpus.deleteCorpus',params)
            return self.__handleJSONResponse(response.read())
                
        def createContext(self,contextName,contextDescription):
                """
                Creates a new context for your user which articles can be matched against. 
                A context is a set of articles that you have defined and created a semantic context for. 
                I.e. this can be a Sport Context, Technology Context etc.

                @type String
                @param contextName - Provide a name for your new context.
                @type String
                @param contextDescription - Provide a description for your new context.
                        Use something that describes what the corpus contains (i.e. English blog posts from my personal blog)
                @rtype dictionary
                @return
                        contextId    Int        A unique id for your newly created context.
                """
                params = (contextName,contextDescription)
                response = self.__doRequest('context.createContext', params)
                return self.__handleJSONResponse(response.read())
                
        def getContexts(self):
                """
                Gives you the id, name and description of all the created contexts.

                @rtype Dictionary
                @return
                        contextId           Int       A unique id for the context.
                        contextName         String    The context name provided when context was created.
                        contextDescription  String    The context description provided when context was created.
                """
                response = self.__doRequest('context.listContexts',())
                return self.__handleJSONResponse(response.read())
                
        def deleteContext(self, contextId):
            """
            Deletes an existing context
            
            @type Int
            @param contextId - ID for the context you want to delete.
            @return 
                    boolean
            """
            params = [contextId]
            response = self.__doRequest('context.deleteContext',params)
            return self.__handleJSONResponse(response.read())
            
        def updateContext(self, contextId, contextName, contextDescription):
            """
            Update an existing contexts name and/or description.
            
            @type Int
            @param contextId - Id for the context you want to update
            @type String
            @param contextName - The contexts name
            @type String
            @param contextDescription - A description for your context
            
            @return 
                boolean
            """
            params = (contextId, contextName, contextDescription)
            response = self.__doRequest('context.updateContext',params)
            return self.__handleJSONResponse(response.read())
                          
        def addContextArticles(self, contextId, corpusId, articleIds):
                """
                Add articles that you like to a specified context.
                
                @type Number
                @param contextId   - A unique id for the context you want to add the like articles to.
                @type Number
                @param corpusId  - The corpus id for where the articles you want to add as "like" articles exists.
                @type Array
                @param articleIds - A java formatted ArrayList containing all article ids you want to add as "like" articles.
       
                @rtype Bool
                @return
                        result            Bool        Returns true if request was successful.               
                """
                #Json-rpc-java compatible list
                javarpcList = {'javaClass':"java.util.ArrayList",
                                'list':articleIds}

                params = [contextId, corpusId,javarpcList]
                response = self.__doRequest('context.addLikeArticles', params)
                return self.__handleJSONResponse(response.read())
                
        def deleteContextArticles(self, contextId, corpusId, articleIds):
                """
                Delete articles that you have added from a specified context.

                @type Number
                @param contextId   - A unique id for the context you want to remove articles from.
                @type Number
                @param corpusId  - The corpus id for where the articles you want to remove articles from exists in.
                @type Array
                @param articleIds - A java formatted ArrayList containing all ids of the articles you want to remove from the context.

                @rtype Bool
                @return
                        result            Bool        Returns true if request was successful.               
                """
                #Json-rpc-java compatible list
                javarpcList = {'javaClass':"java.util.ArrayList",
                                'list':articleIds}

                params = [contextId, corpusId,javarpcList]
                response = self.__doRequest('context.deleteLikeArticles', params)
                return self.__handleJSONResponse(response.read())
                
        def getContextSimilarity(self, corpusId, articleId, againstContextIds, threshold, limit, wait):
                """
                Get how semantically like an article are to a list of contexts.


                @type Number
                @param corpusId -   The corpus id for where the article you want get similarity for exists 
                @type Number
                @param articleId -    The article id for your source article 
                @type Array
                @param articleIds -     A java formatted ArrayList containing all context ids you want to get similarity for.
                @type Float
                @param threshold -      Threshold for how like answers must be. E.g. 0.8 is 80 percent similar.
                @type Integer
                @param limit -          Number of max answers.
                @type Integer
                @param wait -           How long you maximum want to wait for an answer before shutting down the connection. (Max 120 sec)

                @rtype Bool
                @return
                        contextId               Int     The context id.
                        SemanticResultValue     Int     A value between 0-1 for how semantically like the source article are compared to the context.             
                """
                #Json-rpc-java compatible list
                javarpcList = {'javaClass':"java.util.ArrayList",
                                'list':againstContextIds}

                params = [corpusId,articleId,javarpcList, threshold, limit, wait]
                response = self.__doRequest('context.getContextSimilarity', params)
                return self.__handleJSONResponse(response.read()) 
        
        def __createSession(self,apiKey, secretKey):
                """
                Creates a session towards the Saplo API

                @type String
                @param apikey - The apikey to access the Saplo API
                @type String
                @param secretkey - The secret key to access the Saplo API
                """
                #Request a new session
                response = self.__doRequest('auth.createSession',(apiKey,secretKey))
               
                # Get the response
                jsonresponse = response.read()
                #If our request fails, raise an SaploException
                try:
                        self.__handleJSONResponse(jsonresponse)
                except SaploError, err:
                        raise err
                #Decode the JSON request and retrieve the token,establishing it as our given token
                result = json.loads(jsonresponse)
                token  = result['result']
                self.__setTokenTo(token)
                
        def __doRequest(self, meth, param,sapid=0):
                '''
                Creates an JSON request to the server from the params
                '''
                #HTTP params
                options = json.dumps(dict(
                        method = meth,
                        params = param,
                        id=sapid))
                        
                #Parse the url-string to contain our session-token
                url = self.url.format(token = self.token)

                #Create HTTP request
                request  = urllib2.Request(url,options)
                response = urllib2.urlopen(request)
                return response
                
        def __setTokenTo(self, t):
                '''
                Sets the class token string to the given param
                '''
                self.token = t;
                
        def __handleJSONResponse(self, jsonresponse):
                response = json.loads(jsonresponse)
                #If errors, handle them
                if "error" in response:
                        errormsg  =  "Unknown error" if ('msg'  not in response['error']) else response['error']['msg']
                        errorcode =  "" if ('code' not in response['error']) else response['error']['code']                    
                        
                        #Create a readable error message
                        msg = "An error has occured: '{errormessage}' With code = ({errorcode})".format(
                                        errormessage = errormsg,
                                        errorcode    = errorcode,
                                        );
                        #Raise an SaploError
                        raise SaploError(msg)
                ##Otherwise we have a sucessfull response
                return response     
