from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from app.config import settings


class MongoDBParser:
    """Parser for MongoDB collections."""
    
    def __init__(self):
        self.client = None
        self.db = None
    
    def connect(self, uri: Optional[str] = None, database: Optional[str] = None):
        """Connect to MongoDB."""
        self.client = MongoClient(uri or settings.MONGODB_URI)
        self.db = self.client[database or settings.MONGODB_DATABASE]
    
    def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
    
    def get_collections(self) -> List[str]:
        """Get all collection names."""
        if not self.db:
            raise Exception("Not connected to MongoDB")
        return self.db.list_collection_names()
    
    def parse_collection(
        self,
        collection_name: str,
        query: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Parse data from MongoDB collection.
        
        Args:
            collection_name: Name of collection
            query: MongoDB query filter (None for all documents)
            limit: Max number of documents to retrieve
        
        Returns:
            List of documents as dictionaries
        """
        if not self.db:
            raise Exception("Not connected to MongoDB")
        
        collection = self.db[collection_name]
        cursor = collection.find(query or {})
        
        if limit:
            cursor = cursor.limit(limit)
        
        # Convert to list and remove _id field
        data = []
        for doc in cursor:
            # Convert ObjectId to string
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            data.append(doc)
        
        return data
    
    def get_sample(self, collection_name: str, n: int = 5) -> List[Dict[str, Any]]:
        """Get sample documents from collection."""
        return self.parse_collection(collection_name, limit=n)
    
    def get_schema(self, collection_name: str) -> Dict[str, Any]:
        """Get schema (field names and types) from collection."""
        sample = self.get_sample(collection_name, n=100)
        
        if not sample:
            return {}
        
        # Collect all field names and types
        schema = {}
        for doc in sample:
            for key, value in doc.items():
                if key not in schema:
                    schema[key] = type(value).__name__
        
        return schema


# Singleton instance
mongodb_parser = MongoDBParser()
