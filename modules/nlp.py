import re
import ssl
import nltk
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

# Ignore SSL certificate errors
ssl._create_default_https_context = ssl._create_unverified_context

nltk.download('punkt')
nltk.download('stopwords')

class NLP:
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))

    def tokenize_text(self, text: str) -> list:
        """Tokenize text and remove stopwords."""
        if not isinstance(text, str):
            raise ValueError('Input must be a string.')
        
        text = text.lower()
        # Remove characters that are not lowercase letters or whitespace
        text = re.sub(r'[^a-z\s]', '', text)

        tokens = nltk.word_tokenize(text)
        # Remove stopwords
        filtered_tokens = [token for token in tokens if token not in self.stopwords]

        return filtered_tokens 

    def generate_tfidf_matrix(self, tokens_column: pd.Series) -> np.array:
        """Generate weighted TF-IDF embeddings for a given corpus.""" 
        if not isinstance(tokens_column, pd.Series):
            raise ValueError('Input must be a pandas Series.')
        
        # Convert lists of tokens to strings
        token_strings = tokens_column.apply(lambda x: ' '.join(x))

        # Generate TF-IDF matrix
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(token_strings.values)
        feature_names = tfidf_vectorizer.get_feature_names_out()

        print(feature_names)

    def generate_weighted_embeddings(self, tokens: list, word_vectors: dict) -> np.array:
        assert isinstance(tokens, list), 'Input must be a list.'

        embeddings = [word_vectors[token] for token in tokens if token in word_vectors]
        
        # Calculate the average of the token's embeddings
        return np.mean(embeddings, axis=0)

    
    

if __name__ == '__main__':
    text = 'This is a sample text for tokenization.'
    nlp = NLP()
    tokens = nlp.tokenize_text(text.values)
    print(tokens)

