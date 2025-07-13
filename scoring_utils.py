from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def preprocess_text(text):
    """
    Preprocesses the input text by tokenizing and lemmatizing it.
    
    Args:
        text (str): The input text to preprocess.
    
    Returns:
        list: A list of lemmatized tokens.
    """
    # Tokenize the text into words
    tokens = word_tokenize(text)
    
    # Initialize the WordNet lemmatizer
    lemmatizer = WordNetLemmatizer()
    
    # Lemmatize each token and convert to lowercase
    lemmatized_tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
    
    return lemmatized_tokens
