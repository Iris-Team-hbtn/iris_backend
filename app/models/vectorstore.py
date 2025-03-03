import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
import spacy

class VectorStore:
    """
    A class for creating and searching through vector representations of PDF text documents.
    Uses sentence transformers for embeddings and FAISS for efficient similarity search.
    """
    def __init__(self, pdf_path, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        # Initialize Spanish language model
        self.nlp = spacy.load('es_core_news_sm')
        # Load the sentence transformer model
        self.model = SentenceTransformer(model_name)
        
        # Process the PDF document
        raw_text = self._extract_text_from_pdf(pdf_path)
        self.sentences = self._tokenize_text(raw_text)
        
        # Create vector representations and search index
        self.embeddings = self._create_embeddings(self.sentences)
        self.index = self._create_faiss_index(self.embeddings)
    
    def _extract_text_from_pdf(self, pdf_path):
        """
        Extracts text content from a PDF file.
        Returns: Combined text from all readable pages
        """
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text
    
    def _tokenize_text(self, text):
        """
        Splits text into sentences using spaCy's sentence segmentation.
        Returns: List of sentences
        """
        text = ' '.join(text.split())  # Remove extra whitespace and newlines
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents]
    
    def _create_embeddings(self, text_fragments):
        """
        Converts text fragments into vector embeddings using the sentence transformer.
        Returns: NumPy array of embeddings
        """
        return self.model.encode(text_fragments, show_progress_bar=True)
    
    def _create_faiss_index(self, embeddings):
        """
        Creates a FAISS index for efficient similarity search.
        Returns: FAISS index initialized with embeddings
        """
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        return index
    
    def search(self, query, top_k=5, distance_threshold=1.1):
        """
        Searches for similar sentences to the query in the vector store.
        Args:
            query: Search query text
            top_k: Number of results to return
            distance_threshold: Maximum L2 distance for considering a match
        Returns: Concatenated string of matching sentences
        """
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(query_vector, top_k)
        results = [
            self.sentences[i]
            for dist, i in zip(distances[0], indices[0])
            if dist <= distance_threshold
        ]
        return " ".join(results)
