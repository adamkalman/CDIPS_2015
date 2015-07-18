import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
import nltk
#nltk.download()
from nltk.corpus import stopwords # Import the stop word list
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier

def status_to_words(raw_status):
    # Function to convert a raw status to a string of words
    # The input is a single string (a raw status update), and 
    # the output is a single string (a preprocessed status update)
    #
    # 1. Remove HTML
    status_text = BeautifulSoup(raw_status).get_text() 
    #
    # 2. Remove non-letters        
    letters_only = re.sub("[^a-zA-Z]", " ", status_text)
    # remove http URLs
    letters_only = re.sub(r"[^https?:\/\/.*[\r\n]*]", "", letters_only)
    #
    # 3. Convert to lower case, split into individual words
    words = letters_only.lower().split()                             
    #
    # 4. In Python, searching a set is much faster than searching
    #   a list, so convert the stop words to a set
    stops = set(stopwords.words("english"))
    #Remove a few more trivial words not identified by NLTK
    stops = stops.union([u'hasn',u'm',u've',u'll',u're',u'didn',u'us',
                         u'im',u'doesn',u'couldn',u'won',u'isn',u'http',
                         u'www']) 
    # 
    # 5. Remove stop words
    meaningful_words = [w for w in words if not w in stops]   
    #
    # 6. Join the words back into one string separated by space, 
    # and return the result.
    return( " ".join( meaningful_words ))

def text_feature(data,text_var,nfeature):
    """Calculate the text features for the given data.
    text_var specifies the name of the column that contains the text.
    nfeature specifies the max number of features to be extracted 
    from the text."""
    # First clean and parse the text data
    clean_statuses = []
    nitem = data.shape[0]
    data.index=range(nitem)
    for i in xrange( 0, nitem):
        if( (i+1)%1000 == 0 ):
            print "Status %d of %d\n" % ( i+1, nitem)                                                                    
        clean_statuses.append( status_to_words(data[text_var][i]))
    
    # Then extract features from the cleaned text
    print "Creating the bag of words...\n"
    vectorizer = CountVectorizer(analyzer = "word",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             max_features = nfeature) 
    data_features = vectorizer.fit_transform(clean_statuses)
    data_features = data_features.toarray()
    return data_features


def rand_forest_predict(data,text_var,target_var,
                   train_size,test_size,nfeature,nestimator):
    
    data_train, data_test = train_test_split(data, train_size=train_size)
    data_test = data_test[:test_size]
    
    # Calculate text features for the training set
    print "Cleaning and parsing train statuses...\n"
    train_features = text_feature(data_train,text_var,nfeature)
    
    # Fit the training set features to a random forest
    forest = RandomForestClassifier(n_estimators = nestimator) 
    print "Fitting to a random forest with ",nestimator," parameters...\n"
    forest = forest.fit( train_features, data_train[target_var] )
    
    # Calculate text features for the testing set
    print "Cleaning and parsing test statuses...\n"
    test_features = text_feature(data_test,text_var,nfeature)
    
    # Use the random forest fitted from the training set to predict the 
    # testing features
    result = forest.predict(test_features)

    # Copy the results to a pandas dataframe with a "Prediction" column containing 
    # the random tree predictions for the target variable, a "True Value" column containing the true
    # values for the target variable
    output = pd.DataFrame( data={"Prediction":result,"True Value":data_test[target_var]} )
    return output

if __name__=="__main__":
    EP = pd.read_csv("EP_data.csv", header=0).dropna()
    target = 'gender'
    ntrain = 3000
    ntest = 3000
    result = rand_forest_predict(EP,'content',target,
                   ntrain,ntest,nfeature=1000,nestimator=50)
    print "The proportion of correct prediction for ",target, " is ", round(sum(result['Prediction']==result['True Value']),2)/test_size
 


