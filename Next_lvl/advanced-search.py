

class SearchEngine:
    """Advanced search capabilities for the cheatsheet manager."""

    def __init__(self, manager):
        """Initialize with a CheatSheetManager instance."""
        self.manager = manager

    def _tokenize(self, text):
        """Split text into tokens, removing common punctuation."""
        if not text:
            return []
        # Simple tokenization - split on whitespace and remove punctuation
        tokens = re.sub(r'[^\w\s]', ' ', text.lower()).split()
        return [token for token in tokens if token]

    def _create_index(self):
        """Create an inverted index for faster text searches."""
        index = {}
        
        for i, cs in enumerate(self.manager.cheatsheets["cheatsheets"]):
            # Index the name
            for token in self._tokenize(cs["name"]):
                if token not in index:
                    index[token] = set()
                index[token].add(i)
                
            # Index the categories
            for category in cs["categories"]:
                for token in self._tokenize(category):
                    if token not in index:
                        index[token] = set()
                    index[token].add(i)
                    
            # Index the keyword path
            if "keyword_path" in cs:
                for keyword in cs["keyword_path"]:
                    for token in self._tokenize(keyword):
                        if token not in index:
                            index[token] = set()
                        index[token].add(i)
            
            # Index the description
            for token in self._tokenize(cs["description"]):
                if token not in index:
                    index[token] = set()
                index[token].add(i)
                
            # Index the content (but with lower weight)
            for token in self._tokenize(cs["content"]):
                if token not in index:
                    index[token] = set()
                index[token].add(i)
                
        return index

    def fuzzy_search(self, query, threshold=0.7):
        """
        Perform fuzzy matching search on cheatsheet metadata.
        
        Args:
            query (str): The search query
            threshold (float): Similarity threshold (0.0 to 1.0)
            
        Returns:
            list: Cheatsheets that match the query with similarity above threshold
        """
        from difflib import SequenceMatcher
        
        results = []
        query = query.lower()
        
        for cs in self.manager.cheatsheets["cheatsheets"]:
            # Check name similarity
            name_similarity = SequenceMatcher(None, query, cs["name"].lower()).ratio()
            
            # Check category similarity
            category_similarity = 0
            for category in cs["categories"]:
                similarity = SequenceMatcher(None, query, category.lower()).ratio()
                category_similarity = max(category_similarity, similarity)
                
            # Check keyword path similarity
            path_similarity = 0
            if "keyword_path" in cs:
                for keyword in cs["keyword_path"]:
                    similarity = SequenceMatcher(None, query, keyword.lower()).ratio()
                    path_similarity = max(path_similarity, similarity)
            
            # Take the maximum similarity
            max_similarity = max(name_similarity, category_similarity, path_similarity)
            
            if max_similarity >= threshold:
                results.append((cs, max_similarity))
                
        # Sort by similarity score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the cheatsheets
        return [result[0] for result in results]

    def semantic_search(self, query, keyword_path=None):
        """
        Perform semantic search using TF-IDF weighting.
        
        Args:
            query (str): The search query
            keyword_path (list): Optional path to restrict search to
            
        Returns:
            list: Ranked list of cheatsheets matching the query
        """
        # First filter by keyword path if provided
        if keyword_path:
            cheatsheets = self.manager.search_by_keyword_path(keyword_path, exact_match=False)
        else:
            cheatsheets = self.manager.cheatsheets["cheatsheets"]
            
        if not cheatsheets:
            return []
            
        # Tokenize the query
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
            
        # Create document corpus for TF-IDF
        corpus = []
        for cs in cheatsheets:
            # Combine metadata fields with higher weight for important fields
            doc = (cs["name"] + " " + cs["name"] + " " +  # Double weight for name
                  " ".join(cs["categories"]) + " " +
                  ((" ".join(cs["keyword_path"])) if "keyword_path" in cs else "") + " " +
                  cs["description"] + " " +
                  cs["content"])
            corpus.append(doc.lower())
            
        # Calculate TF-IDF scores
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(corpus)
            
            # Transform query to vector
            query_vector = vectorizer.transform([" ".join(query_tokens)])
            
            # Calculate similarity between query and documents
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
            
            # Create a list of (index, similarity) pairs
            similarity_scores = [(i, similarities[i]) for i in range(len(similarities))]
            
            # Sort by similarity score descending
            similarity_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return cheatsheets in order of relevance, filtering out zero scores
            return [cheatsheets[idx] for idx, score in similarity_scores if score > 0]
        except ImportError:
            # Fallback if sklearn is not available
            print("Warning: sklearn not available, falling back to basic search")
            return self.basic_search(query, keyword_path)

    def basic_search(self, query, keyword_path=None):
        """
        Perform basic keyword search.
        
        Args:
            query (str): The search query
            keyword_path (list): Optional path to restrict search to
            
        Returns:
            list: List of cheatsheets matching the query
        """
        # This is just a wrapper around the manager's search_cheatsheets
        return self.manager.search_cheatsheets(query, keyword_path)

    def full_text_search(self, query, keyword_path=None):
        """
        Perform full text search using inverted index for speed.
        
        Args:
            query (str): The search query
            keyword_path (list): Optional path to restrict search to
            
        Returns:
            list: List of cheatsheets matching all query terms
        """
        # Tokenize the query
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
            
        # Create inverted index
        index = self._create_index()
        
        # Find documents that contain all query tokens
        matching_docs = None
        for token in query_tokens:
            if token in index:
                if matching_docs is None:
                    matching_docs = index[token].copy()
                else:
                    matching_docs &= index[token]
            else:
                # If any token is not in the index, no documents will match
                return []
                
        if matching_docs is None:
            return []
            
        # Convert matching document indices to cheatsheets
        results = [self.manager.cheatsheets["cheatsheets"][i] for i in matching_docs]
        
        # Filter by keyword path if provided
        if keyword_path:
            results = [cs for cs in results if 
                       "keyword_path" in cs and 
                       self.manager._is_prefix(keyword_path, cs["keyword_path"])]
            
        return results