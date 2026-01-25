"""
Metadata extraction utilities for conversation analysis.
"""
import csv
from pathlib import Path
from typing import Dict, List


class MetadataExtractor:
    """Extract and enrich metadata for conversations."""
    
    def __init__(self, metadata_csv_path: str):
        """
        Initialize metadata extractor.
        
        Args:
            metadata_csv_path: Path to metadata_mapping.csv
        """
        self.metadata_csv_path = Path(metadata_csv_path)
        self.metadata_map = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Dict]:
        """
        Load metadata from CSV into a dictionary keyed by set_id.
        
        Returns:
            Dict mapping set_id to metadata dict
        """
        metadata_map = {}
        
        with open(self.metadata_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                set_id = row['set_id']
                metadata_map[set_id] = {
                    'model_name': row['model_name'],
                    'treatment_id': int(row['treatment_id']),
                    'treatment_name': row['treatment_name'],
                    'treatment_type': row['treatment_type'],
                    'format': row['format'],
                    'valence': row['valence'],
                    'has_thinking': row['has_thinking'] == 'True',
                    'is_truncated': row['is_truncated'] == 'True',
                    'original_file_path': row['original_file_path']
                }
        
        return metadata_map
    
    def get_metadata(self, set_id: str) -> Dict:
        """
        Get metadata for a given set_id.
        
        Args:
            set_id: The conversation set_id
        
        Returns:
            Dict with metadata fields
        """
        return self.metadata_map.get(set_id, {})
    
    def enrich_conversation(self, conversation_id: str, set_id: str) -> Dict:
        """
        Create enriched metadata dict for a conversation.
        
        Args:
            conversation_id: The conversation ID
            set_id: The set_id from batch data
        
        Returns:
            Dict with conversation_id, set_id, and all metadata
        """
        metadata = self.get_metadata(set_id)
        
        return {
            'conversation_id': conversation_id,
            'set_id': set_id,
            **metadata
        }
    
    def extract_metadata_batch(self, conversations: List[Dict]) -> List[Dict]:
        """
        Extract metadata for a batch of conversations.
        
        Args:
            conversations: List of conversation dicts with set_id
        
        Returns:
            List of metadata dicts
        """
        metadata_list = []
        
        for conv in conversations:
            set_id = conv.get('set_id')
            if not set_id:
                continue
            
            # Generate conversation ID from set_id (unique identifier)
            conversation_id = f"{set_id}"
            
            enriched = self.enrich_conversation(conversation_id, set_id)
            metadata_list.append(enriched)
        
        return metadata_list

