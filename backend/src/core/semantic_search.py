from typing import Optional
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from src.repository.interface.database import DbBase
from src.repository.pet_data_handler import PetDataHandler

def normalize(vectors):
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


class SemanticSearch:
    def __init__(self, db: Optional[DbBase] = None, model_name="all-mpnet-base-v2") -> None:
        self.battle_pet_index = None
        self.ability_index = None
        self.db = db or PetDataHandler()
        self.model = SentenceTransformer(model_name)
        self.battle_pet_embeddings = None
        self.ability_embeddings = None



    async def set_embeddings(self):
        all_battle_pets = await self.db.get_all_battle_pets()
        battle_pets_texts = [str(pet) for pet in all_battle_pets]
        self.battle_pet_embeddings = self.model.encode(battle_pets_texts)
        self.battle_pet_embeddings = normalize(self.battle_pet_embeddings)
        self.battle_pet_index = faiss.IndexFlatIP(self.battle_pet_embeddings.shape[1])
        self.battle_pet_index.add(self.battle_pet_embeddings)

        all_abilities = await self.db.get_all_abilities()
        ability_texts = [str(ability) for ability in all_abilities]
        self.ability_embeddings = self.model.encode(ability_texts)
        self.ability_embeddings = normalize(self.ability_embeddings)
        self.ability_index = faiss.IndexFlatIP(self.ability_embeddings.shape[1])
        self.ability_index.add(self.ability_embeddings)


    def search_pet(self, search_query: str, k=5):
        """Search for the top k most similar documents to the query."""
        query_vector = self.model.encode([search_query])
        D, I = self.battle_pet_index.search(query_vector, k)
        return I[0], D[0]  # Return indices and distances

    def search_ability(self, search_query: str, k=5):
        """Search for the top k most similar documents to the query."""
        query_vector = normalize(self.model.encode([search_query]))
        D, I = self.ability_index.search(query_vector, k)
        return I[0], D[0]


# Load sentence transformer model
# model = SentenceTransformer("all-mpnet-base-v2")

# Generate embeddings for the pet descriptions
# embeddings = model.encode(pet_descriptions)

# Normalize embeddings for cosine similarity


# normalized_embeddings = normalize(embeddings)

# Build a FAISS index using inner product (cosine similarity when vectors are normalized)
# dimension = normalized_embeddings.shape[1]
# index = faiss.IndexFlatIP(dimension)
# index.add(normalized_embeddings)

# Define a query
# query = "burning attacks"
# query_vector = model.encode([query])
# normalized_query = normalize(query_vector)

# Search the index
# D, I = index.search(normalized_query, k=3)

# Print top results
# for i, (idx, score) in enumerate(zip(I[0], D[0])):
#     print(f"{i+1}: {pet_descriptions[idx]} (cosine similarity: {score:.2f})")
