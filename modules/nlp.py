import re
import nltk
import pandas as pd
import numpy as np
from tqdm import tqdm
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
        filtered_tokens = [
            token for token in tokens if token not in self.stopwords]

        return filtered_tokens

    def generate_tfidf_weighted_embeddings(self, tokens_column: pd.Series, word_vectors: dict) -> pd.Series:
        """Generate embeddings weighted by TF-IDF scores for each document in the corpus."""
        if not isinstance(tokens_column, pd.Series):
            raise ValueError('Input must be a pandas Series.')

        # Convert lists of tokens to strings for TF-IDF calculation
        token_strings = tokens_column.apply(lambda x: ' '.join(x))

        # Generate TF-IDF matrix
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(token_strings.values)

        # Get feature names (vocabulary)
        feature_names = tfidf_vectorizer.get_feature_names_out()

        # Get embedding dimension from word vectors
        embedding_dim = word_vectors.vector_size

        # Initialize array to store document embeddings
        num_docs = len(tokens_column)
        weighted_embeddings = np.zeros((num_docs, embedding_dim))

        # For each document
        for doc_idx in tqdm(range(num_docs), desc="Generating weighted embeddings"):
            doc_vector = np.zeros(embedding_dim)
            total_weight = 0

            # Get the document's TF-IDF scores
            doc_tfidf = tfidf_matrix[doc_idx].toarray().flatten()

            # For each word in the vocabulary
            for word_idx, word in enumerate(feature_names):
                if word in word_vectors.key_to_index and doc_tfidf[word_idx] > 0:
                    # Multiply word embedding by its TF-IDF score
                    doc_vector += word_vectors[word] * doc_tfidf[word_idx]
                    total_weight += doc_tfidf[word_idx]

            # Normalize by total weight to get weighted average
            if total_weight > 0:
                doc_vector /= total_weight

            weighted_embeddings[doc_idx] = doc_vector

        # Create a Series of numpy arrays with the same index as the input
        embedding_series = pd.Series(
            [np.array(emb) for emb in weighted_embeddings],
            index=tokens_column.index,
            name='weighted_embeddings'
        )

        return embedding_series

    def calculate_grouped_similarities(self, group: pd.DataFrame, figure_column: str, figure_1: str,
                                       figure_2: str, embeddings_column: str,
                                       category_column: str = None, category: str = None) -> float:
        """
        Calculate the average cosine similarity between two groups of embeddings.
        """
        # Filter for each figure
        figure_1_data = group[group[figure_column] == figure_1]
        figure_2_data = group[group[figure_column] == figure_2]

        if category_column and category:
            # Filter for each section
            figure_1_data = figure_1_data[figure_1_data[category_column] == category]
            figure_2_data = figure_2_data[figure_2_data[category_column] == category]

        # Skip if either figure is missing in this month
        if figure_1_data.empty or figure_2_data.empty:
            return np.nan

        # Use stack_embeddings to create matrices
        figure_1_embeddings = np.vstack(figure_1_data[embeddings_column])
        figure_2_embeddings = np.vstack(figure_2_data[embeddings_column])

        # Calculate similarity
        similarity_matrix = cosine_similarity(
            figure_1_embeddings, figure_2_embeddings)
        average_similarity = np.mean(similarity_matrix)

        return average_similarity


if __name__ == '__main__':
    text = 'This is a sample text for tokenization.'
    nlp = NLP()
    tokens = nlp.tokenize_text(text.values)
    print(tokens)
