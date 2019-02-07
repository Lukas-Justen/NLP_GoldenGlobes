
import spacy
import json
#this function goes through the tweets and then tries to extract the named entities

def named_entities(cleaned_tweet_data):
    nlp = spacy.load("en")

 #this dictionary will hold all the names and will have the value as the frequency
    names_dictionary = {}
    for tweet in cleaned_tweet_data:
        curr_tweet = tweet['text']
        texts = nlp(curr_tweet)

        for word in texts.ents:
            
            word_text = word.text
            word_label = word.label_
            
            #check if they are a person then append to dict else move on
            if(word_label == "PERSON"):
                #check if already present in dict
                if(word_text in names_dictionary):
                    curr = names_dictionary[word_text]
                    curr+=1
                else:
                    names_dictionary[word_text]=1
                    
    return names_dictionary