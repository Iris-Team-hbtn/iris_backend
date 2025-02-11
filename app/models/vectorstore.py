import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
import spacy

class VectorStore:
    def __init__(self, pdf_path, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.nlp = spacy.load('es_core_news_sm')
        self.model = SentenceTransformer(model_name)
        
        # Extraer, limpiar y tokenizar texto
        raw_text = self._extract_text_from_pdf(pdf_path)
        self.sentences = self._tokenize_text(raw_text)
        
        # Generar embeddings y construir índice FAISS
        self.embeddings = self._create_embeddings(self.sentences)
        self.index = self._create_faiss_index(self.embeddings)
    
    def _extract_text_from_pdf(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text
    
    def _tokenize_text(self, text):
        text = ' '.join(text.split())  # Limpiar saltos de línea y espacios
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents]
    
    def _create_embeddings(self, text_fragments):
        return self.model.encode(text_fragments, show_progress_bar=True)
    
    def _create_faiss_index(self, embeddings):
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        return index
    
    def search(self, query, top_k=5, distance_threshold=1.1):
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(query_vector, top_k)
        results = [
            self.sentences[i]
            for dist, i in zip(distances[0], indices[0])
            if dist <= distance_threshold
        ]
        return " ".join(results)
