from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from src.repository.mongo_db import MongoDb
# class SemanticSearch:
#     def __init__(self, model_name="all-mpnet-base-v2"):
#         self.model = SentenceTransformer(model_name)
#         self.index = None
#         self.embeddings = None
#
#     def fit(self, documents):
#         """Fit the model to the provided documents."""
#         self.embeddings = self.model.encode(documents)
#         self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
#         self.index.add(self.embeddings)
my_db = MongoDb()
def search(query, k=5):
    """Search for the top k most similar documents to the query."""
    query_vector = self.model.encode([query])
    D, I = self.index.search(query_vector, k)
    return I[0], D[0]  # Return indices and distances
# Example pet descriptions
pet_descriptions = [
    "A fierce aquatic turtle with strong armor",
    "Flying eagle that strikes fast from above",
    "Undead skeletal dog with poison bite",
    "Mechanical spider with flame thrower",
    "Cute critter with healing abilities",
    "Magical owl with arcane storm attack",
    "Elemental fire imp with area damage",
    "Beast lion with powerful roar"
]

# Load sentence transformer model
# model = SentenceTransformer("all-mpnet-base-v2")
#
# # Generate embeddings for the pet descriptions
# embeddings = model.encode(pet_descriptions)
#
# # Normalize embeddings for cosine similarity
# def normalize(vectors):
#     return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
#
# normalized_embeddings = normalize(embeddings)
#
# # Build a FAISS index using inner product (cosine similarity when vectors are normalized)
# dimension = normalized_embeddings.shape[1]
# index = faiss.IndexFlatIP(dimension)
# index.add(normalized_embeddings)
#
# # Define a query
# query = "burning attacks"
# query_vector = model.encode([query])
# normalized_query = normalize(query_vector)
#
# # Search the index
# D, I = index.search(normalized_query, k=3)
#
# # Print top results
# for i, (idx, score) in enumerate(zip(I[0], D[0])):
#     print(f"{i+1}: {pet_descriptions[idx]} (cosine similarity: {score:.2f})")
