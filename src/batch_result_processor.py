"""
Process batch evaluation results and join with metadata.
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from src.metadata_extractor import MetadataExtractor


class BatchResultProcessor:
    """Process batch results and create analysis-ready outputs."""
    
    def __init__(self, metadata_csv_path: str):
        """
        Initialize processor with metadata extractor.
        
        Args:
            metadata_csv_path: Path to metadata_mapping.csv
        """
        self.metadata_extractor = MetadataExtractor(metadata_csv_path)
    
    def process_raw_judgments(self, scored_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process scored results to create raw judgment format.
        
        Args:
            scored_results: List of scored conversation results from BatchEvaluator
        
        Returns:
            List of raw judgment dicts
        """
        raw_judgments = []
        
        for result in scored_results:
            judgment = {
                'conversation_id': result['conversation_id'],
                'Evidence_R_Adj': result.get('Evidence_R_Adj', 0),
                'Testimonial_R_Adj': result.get('Testimonial_R_Adj', 0),
                'Safety_Rejection_Adj': result.get('Safety_Rejection_Adj', 0),
                'Misatribution_R_Adj': result.get('Misatribution_R_Adj', 0),
                'Promotion_Adj': result.get('Promotion_Adj', 0),
                'HCP_Ref_Adj': result.get('HCP_Ref_Adj', 0),
                'Critical_Fails': result.get('Critical_Fails', []),
                'Total_Score': result.get('Total_Score', 0),
                'Overall_Classification': result.get('Overall_Classification', 'Weak'),
                'LLM_Analysis': result.get('LLM_Analysis', ''),
                'LLM_Notes': result.get('LLM_Notes', {})
            }
            raw_judgments.append(judgment)
        
        return raw_judgments
    
    def extract_metadata_from_conversations(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract metadata for all conversations in a batch.
        
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
            
            # Use set_id as conversation_id for consistency
            conversation_id = set_id
            enriched = self.metadata_extractor.enrich_conversation(conversation_id, set_id)
            metadata_list.append(enriched)
        
        return metadata_list
    
    def join_judgments_with_metadata(self, 
                                     raw_judgments: List[Dict[str, Any]],
                                     metadata_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Join judgment data with metadata.
        
        Args:
            raw_judgments: List of judgment dicts
            metadata_list: List of metadata dicts
        
        Returns:
            List of combined dicts ready for analysis
        """
        # Create lookup dict for metadata
        metadata_lookup = {m['conversation_id']: m for m in metadata_list}
        
        combined = []
        for judgment in raw_judgments:
            conv_id = judgment['conversation_id']
            metadata = metadata_lookup.get(conv_id, {})
            
            # Combine judgment and metadata
            combined_entry = {
                **judgment,
                'set_id': metadata.get('set_id', ''),
                'model_name': metadata.get('model_name', ''),
                'treatment_id': metadata.get('treatment_id', 0),
                'treatment_name': metadata.get('treatment_name', ''),
                'treatment_type': metadata.get('treatment_type', ''),
                'format': metadata.get('format', ''),
                'valence': metadata.get('valence', ''),
                'has_thinking': metadata.get('has_thinking', False),
                'is_truncated': metadata.get('is_truncated', False)
            }
            combined.append(combined_entry)
        
        return combined
    
    def save_outputs(self, 
                    raw_judgments: List[Dict[str, Any]],
                    metadata_list: List[Dict[str, Any]],
                    combined_data: List[Dict[str, Any]],
                    output_dir: Path,
                    batch_name: str):
        """
        Save all output files for a batch.
        
        Args:
            raw_judgments: Raw judgment data
            metadata_list: Metadata list
            combined_data: Combined analysis-ready data
            output_dir: Output directory
            batch_name: Name of batch (e.g., "batch_001")
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save raw judgments
        raw_path = output_dir / f"{batch_name}_raw_judgments.json"
        with open(raw_path, 'w') as f:
            json.dump(raw_judgments, f, indent=2)
        print(f"Saved raw judgments to {raw_path}")
        
        # Save metadata
        metadata_path = output_dir / f"{batch_name}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata_list, f, indent=2)
        print(f"Saved metadata to {metadata_path}")
        
        # Save combined analysis-ready data
        combined_path = output_dir / f"{batch_name}_analysis_ready.json"
        with open(combined_path, 'w') as f:
            json.dump(combined_data, f, indent=2)
        print(f"Saved analysis-ready data to {combined_path}")
    
    def combine_batches(self,
                       batch_001_judgments: List[Dict[str, Any]],
                       batch_002_judgments: List[Dict[str, Any]],
                       batch_001_metadata: List[Dict[str, Any]],
                       batch_002_metadata: List[Dict[str, Any]],
                       batch_001_combined: List[Dict[str, Any]],
                       batch_002_combined: List[Dict[str, Any]],
                       output_dir: Path):
        """
        Combine results from both batches into single files.
        
        Args:
            batch_001_judgments: Judgments from batch 001
            batch_002_judgments: Judgments from batch 002
            batch_001_metadata: Metadata from batch 001
            batch_002_metadata: Metadata from batch 002
            batch_001_combined: Combined data from batch 001
            batch_002_combined: Combined data from batch 002
            output_dir: Output directory
        """
        # Combine all judgments
        all_judgments = batch_001_judgments + batch_002_judgments
        judgments_path = output_dir / "combined_raw_judgments.json"
        with open(judgments_path, 'w') as f:
            json.dump(all_judgments, f, indent=2)
        print(f"Saved combined judgments ({len(all_judgments)} total) to {judgments_path}")
        
        # Combine all metadata
        all_metadata = batch_001_metadata + batch_002_metadata
        metadata_path = output_dir / "combined_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(all_metadata, f, indent=2)
        print(f"Saved combined metadata ({len(all_metadata)} total) to {metadata_path}")
        
        # Combine analysis-ready data
        all_combined = batch_001_combined + batch_002_combined
        combined_path = output_dir / "combined_analysis_ready.json"
        with open(combined_path, 'w') as f:
            json.dump(all_combined, f, indent=2)
        print(f"Saved combined analysis-ready data ({len(all_combined)} total) to {combined_path}")

