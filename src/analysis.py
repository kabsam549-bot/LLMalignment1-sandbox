"""
Agreement analysis module for LLM Judge evaluation system.
"""
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sklearn.metrics import confusion_matrix, cohen_kappa_score
from statsmodels.stats.inter_rater import fleiss_kappa
from src.config import RUBRIC_DIMENSIONS, CLASSIFICATION_THRESHOLDS
from src.data_cleaning import normalize_columns, validate_labels


class AgreementAnalyzer:
    """Analyzer for agreement metrics between LLM and human annotations."""
    
    def __init__(self, predictions: List[Dict[str, Any]], output_dir: Path):
        """
        Initialize agreement analyzer.
        
        Args:
            predictions: List of LLM predictions
            output_dir: Directory to save analysis results
        """
        self.predictions = predictions
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load human annotations
        self.human_data = self._load_human_annotations()
        
    def _load_human_annotations(self) -> pd.DataFrame:
        """Load human annotation data."""
        data_file = Path("data/pilot_all_with_adjudicated_scores_with_text.csv")
        if not data_file.exists():
            raise FileNotFoundError(f"Human annotation data not found: {data_file}")
        
        df = pd.read_csv(data_file)
        return df
    
    def _merge_predictions_with_human_data(self) -> pd.DataFrame:
        """Merge LLM predictions with human annotations."""
        # Convert predictions to DataFrame
        pred_df = pd.DataFrame(self.predictions)
        
        # Merge with human data on conversation_id (set_id in human data)
        merged = pd.merge(
            pred_df, 
            self.human_data, 
            left_on='conversation_id', 
            right_on='set_id', 
            how='inner'
        )

        # Normalize column names (e.g., Misattribution spelling) and coerce label values
        merged = normalize_columns(merged)
        merged, _ = validate_labels(merged)

        return merged

    def _get_llm_and_adj_cols(self, merged_data: pd.DataFrame, dimension: str) -> Tuple[pd.Series, pd.Series]:
        """Resolve LLM and adjudicated series with spelling/_x/_y safeguards."""
        llm_col = f'{dimension}_x' if f'{dimension}_x' in merged_data.columns else dimension
        llm_series = merged_data[llm_col]

        if f'{dimension}_y' in merged_data.columns:
            adj_series = merged_data[f'{dimension}_y']
        elif dimension == 'Misatribution_R_Adj' and 'Misattribution_R_Adj' in merged_data.columns:
            adj_series = merged_data['Misattribution_R_Adj']
        else:
            adj_series = merged_data[dimension]
        return llm_series, adj_series

    def _pairwise_kappa(self, a: pd.Series, b: pd.Series) -> Tuple[float, str]:
        """Compute Cohen's kappa with basic sanity checks. Returns (kappa, note)."""
        # Drop rows where either is NaN
        valid = a.notna() & b.notna()
        a_valid = a[valid]
        b_valid = b[valid]
        if len(a_valid) == 0:
            return np.nan, 'insufficient data'
        if a_valid.nunique() == 1 or b_valid.nunique() == 1:
            return np.nan, 'no variance'
        try:
            return cohen_kappa_score(a_valid, b_valid), ''
        except Exception as e:
            return np.nan, f'error: {e}'

    def calculate_pairwise_agreements(self, merged_data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Compute percentage agreement for RA↔ML, RA↔LLM, ML↔LLM per dimension.
        Returns percentage agreement (0-100) for each pair.
        """
        agreement_results: Dict[str, Dict[str, float]] = {}

        dimension_mapping = {
            'Evidence_R_Adj': 'Evidence_R',
            'Testimonial_R_Adj': 'Testimonial_R', 
            'Safety_Rejection_Adj': 'Safety_Rejection',
            'Misatribution_R_Adj': 'Misatribution_R',
            'Promotion_Adj': 'Promotion',
            'HCP_Ref_Adj': 'HCP_Ref'
        }

        for dimension in RUBRIC_DIMENSIONS:
            base_name = dimension_mapping[dimension]
            ml = merged_data.get(f'{base_name}_ML')
            ra = merged_data.get(f'{base_name}_RA')
            llm, _adj = self._get_llm_and_adj_cols(merged_data, dimension)

            dim_res: Dict[str, float] = {}

            # RA ↔ ML percentage agreement
            if ml is not None and ra is not None:
                valid = ml.notna() & ra.notna()
                if valid.sum() > 0:
                    agreement = (ml[valid] == ra[valid]).sum() / valid.sum() * 100
                    dim_res['pct_RA_ML'] = agreement
                else:
                    dim_res['pct_RA_ML'] = np.nan
            else:
                dim_res['pct_RA_ML'] = np.nan

            # RA ↔ LLM percentage agreement
            if ra is not None:
                valid = ra.notna() & llm.notna()
                if valid.sum() > 0:
                    agreement = (ra[valid] == llm[valid]).sum() / valid.sum() * 100
                    dim_res['pct_RA_LLM'] = agreement
                else:
                    dim_res['pct_RA_LLM'] = np.nan
            else:
                dim_res['pct_RA_LLM'] = np.nan

            # ML ↔ LLM percentage agreement
            if ml is not None:
                valid = ml.notna() & llm.notna()
                if valid.sum() > 0:
                    agreement = (ml[valid] == llm[valid]).sum() / valid.sum() * 100
                    dim_res['pct_ML_LLM'] = agreement
                else:
                    dim_res['pct_ML_LLM'] = np.nan
            else:
                dim_res['pct_ML_LLM'] = np.nan

            agreement_results[dimension] = dim_res

        return agreement_results

    def calculate_overall_classification(self, merged_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate overall classification metrics across all dimensions."""
        # Get all dimension columns
        dim_columns = list(RUBRIC_DIMENSIONS.keys())
        
        # Map adjudicated dimension names to ML/RA column names
        dimension_mapping = {
            'Evidence_R_Adj': 'Evidence_R',
            'Testimonial_R_Adj': 'Testimonial_R', 
            'Safety_Rejection_Adj': 'Safety_Rejection',
            'Misatribution_R_Adj': 'Misatribution_R',
            'Promotion_Adj': 'Promotion',
            'HCP_Ref_Adj': 'HCP_Ref'
        }
        
        # Calculate overall agreement for each conversation
        overall_agreements = []
        
        for _, row in merged_data.iterrows():
            # Count agreements per conversation across all dimensions
            total_dims = 0
            llm_vs_any_agreements = 0
            
            for dim in dim_columns:
                base = dimension_mapping.get(dim, dim.replace('_Adj', ''))
                ml_col = f"{base}_ML"
                ra_col = f"{base}_RA"
                
                # Get LLM column (might be dim or dim_x)
                llm_col = dim if dim in merged_data.columns else f"{dim}_x"
                if llm_col not in merged_data.columns:
                    continue
                
                # Skip if any value is NaN
                if pd.isna(row[ml_col]) or pd.isna(row[ra_col]) or pd.isna(row[llm_col]):
                    continue
                    
                total_dims += 1
                
                # LLM vs Any: agreement with at least one human rater
                if (row[llm_col] == row[ml_col]) or (row[llm_col] == row[ra_col]):
                    llm_vs_any_agreements += 1
            
            if total_dims > 0:
                overall_agreements.append({
                    'total_dims': total_dims,
                    'llm_vs_any': llm_vs_any_agreements / total_dims
                })
        
        if not overall_agreements:
            return {"llm_vs_any_overall": np.nan, "avg_dims_per_conversation": np.nan}
        
        # Calculate overall metrics
        llm_vs_any_overall = np.mean([ag['llm_vs_any'] for ag in overall_agreements]) * 100
        avg_dims_per_conversation = np.mean([ag['total_dims'] for ag in overall_agreements])
        
        # Determine overall classification category
        if llm_vs_any_overall >= 80:
            classification = "Strong"
        elif llm_vs_any_overall >= 60:
            classification = "Moderate"
        else:
            classification = "Weak"
        
        return {
            "llm_vs_any_overall": llm_vs_any_overall,
            "avg_dims_per_conversation": avg_dims_per_conversation,
            "classification": classification
        }
    
    def calculate_fleiss_kappa(self, merged_data: pd.DataFrame) -> Tuple[Dict[str, float], Dict[str, str]]:
        """Calculate Fleiss' kappa for 3-way agreement (ML, RA, LLM).
        Returns (kappa_results, notes) with reasons for NaNs.
        """
        kappa_results = {}
        notes = {}
        
        # Map adjudicated dimension names to ML/RA column names
        dimension_mapping = {
            'Evidence_R_Adj': 'Evidence_R',
            'Testimonial_R_Adj': 'Testimonial_R', 
            'Safety_Rejection_Adj': 'Safety_Rejection',
            'Misatribution_R_Adj': 'Misatribution_R',
            'Promotion_Adj': 'Promotion',
            'HCP_Ref_Adj': 'HCP_Ref'
        }
        
        for dimension in RUBRIC_DIMENSIONS:
            base_name = dimension_mapping[dimension]
            # Get ML, RA, and LLM scores for this dimension
            ml_col = f'{base_name}_ML'
            ra_col = f'{base_name}_RA'
            llm_col = f'{dimension}_x' if f'{dimension}_x' in merged_data.columns else dimension
            
            if ml_col not in merged_data.columns or ra_col not in merged_data.columns:
                kappa_results[dimension] = np.nan
                notes[dimension] = 'missing rater columns'
                continue
            
            ml_scores = merged_data[ml_col]
            ra_scores = merged_data[ra_col]
            llm_scores = merged_data[llm_col]
            
            # Drop rows with any NaN
            valid = ml_scores.notna() & ra_scores.notna() & llm_scores.notna()
            if valid.sum() == 0:
                kappa_results[dimension] = np.nan
                notes[dimension] = 'no valid rows'
                continue
            
            ml_valid = ml_scores[valid].astype(int).values
            ra_valid = ra_scores[valid].astype(int).values
            llm_valid = llm_scores[valid].astype(int).values
            
            # Check for variance
            if len(np.unique(ml_valid)) == 1 and len(np.unique(ra_valid)) == 1 and len(np.unique(llm_valid)) == 1:
                kappa_results[dimension] = np.nan
                notes[dimension] = 'no variance across all raters'
                continue
            
            # Fleiss kappa needs aggregate table format: n_subjects x n_categories
            # where each cell is the count of raters who assigned that category
            min_val = RUBRIC_DIMENSIONS[dimension]['min']
            max_val = RUBRIC_DIMENSIONS[dimension]['max']
            categories = list(range(min_val, max_val + 1))
            n_subjects = len(ml_valid)
            
            # Build the aggregate table
            aggregate = np.zeros((n_subjects, len(categories)), dtype=int)
            for i in range(n_subjects):
                for score in [ml_valid[i], ra_valid[i], llm_valid[i]]:
                    if min_val <= score <= max_val:
                        cat_idx = score - min_val
                        aggregate[i, cat_idx] += 1
            
            try:
                kappa = fleiss_kappa(aggregate, method='fleiss')
                kappa_results[dimension] = kappa
                notes[dimension] = ''
            except Exception as e:
                kappa_results[dimension] = np.nan
                notes[dimension] = f'calculation error: {str(e)[:50]}'
        
        return kappa_results, notes
    
    def calculate_cohens_kappa(self, merged_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate Cohen's kappa for LLM vs Adjudicated agreement."""
        kappa_results = {}
        
        for dimension in RUBRIC_DIMENSIONS:
            llm_series, adj_series = self._get_llm_and_adj_cols(merged_data, dimension)
            kappa, _ = self._pairwise_kappa(adj_series, llm_series)
            kappa_results[dimension] = kappa
        
        return kappa_results
    
    def calculate_agreement_percentages(self, merged_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate agreement percentages."""
        results = {}
        
        # Map adjudicated dimension names to ML/RA column names
        dimension_mapping = {
            'Evidence_R_Adj': 'Evidence_R',
            'Testimonial_R_Adj': 'Testimonial_R', 
            'Safety_Rejection_Adj': 'Safety_Rejection',
            'Misatribution_R_Adj': 'Misatribution_R',
            'Promotion_Adj': 'Promotion',
            'HCP_Ref_Adj': 'HCP_Ref'
        }
        
        # 3-way exact match
        three_way_matches = 0
        total_conversations = len(merged_data)
        
        for dimension in RUBRIC_DIMENSIONS:
            base_name = dimension_mapping[dimension]
            ml_scores = merged_data[f'{base_name}_ML'].values
            ra_scores = merged_data[f'{base_name}_RA'].values
            
            # Handle LLM scores - check if column has _x suffix or not
            llm_col = f'{dimension}_x' if f'{dimension}_x' in merged_data.columns else dimension
            llm_scores = merged_data[llm_col].values
            
            # Count exact 3-way matches
            matches = np.sum((ml_scores == ra_scores) & (ra_scores == llm_scores))
            percentage = (matches / total_conversations) * 100
            results[f'{dimension}_3way_match'] = percentage
        
        # LLM vs any human match
        for dimension in RUBRIC_DIMENSIONS:
            base_name = dimension_mapping[dimension]
            ml_scores = merged_data[f'{base_name}_ML'].values
            ra_scores = merged_data[f'{base_name}_RA'].values
            
            # Handle LLM scores - check if column has _x suffix or not
            llm_col = f'{dimension}_x' if f'{dimension}_x' in merged_data.columns else dimension
            llm_scores = merged_data[llm_col].values
            
            # Count LLM matches with either ML or RA
            matches = np.sum((llm_scores == ml_scores) | (llm_scores == ra_scores))
            percentage = (matches / total_conversations) * 100
            results[f'{dimension}_llm_vs_any_human'] = percentage
        
        return results
    
    def create_confusion_matrices(self, merged_data: pd.DataFrame, timestamp: str):
        """Create confusion matrices for each dimension."""
        n_dims = len(RUBRIC_DIMENSIONS)
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, dimension in enumerate(RUBRIC_DIMENSIONS):
            if i >= len(axes):
                break
                
            # Resolve columns safely
            llm_series, adj_series = self._get_llm_and_adj_cols(merged_data, dimension)
            llm_scores = llm_series.fillna(-1).astype(int).values
            adj_scores = adj_series.fillna(-1).astype(int).values
            
            # Create confusion matrix
            cm = confusion_matrix(adj_scores, llm_scores)
            
            # Plot
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[i])
            axes[i].set_title(f'{dimension}')
            axes[i].set_xlabel('LLM Prediction')
            axes[i].set_ylabel('Adjudicated Score')
        
        # Hide unused subplots
        for i in range(len(RUBRIC_DIMENSIONS), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f'confusion_matrices_{timestamp}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_overall_classification_confusion(self, merged_data: pd.DataFrame, timestamp: str):
        """Create confusion matrix for overall classification."""
        # Calculate overall classifications
        llm_classifications = []
        adj_classifications = []
        
        for _, row in merged_data.iterrows():
            # LLM classification - handle column naming issues
            llm_total = 0
            for dim in RUBRIC_DIMENSIONS:
                llm_col = f'{dim}_x' if f'{dim}_x' in merged_data.columns else dim
                if not pd.isna(row[llm_col]):
                    llm_total += row[llm_col]
            llm_class = self._get_classification(llm_total)
            llm_classifications.append(llm_class)
            
            # Adjudicated classification - handle column naming issues
            adj_total = 0
            for dim in RUBRIC_DIMENSIONS:
                if f'{dim}_y' in merged_data.columns:
                    adj_col = f'{dim}_y'
                elif dim == 'Misatribution_R_Adj' and 'Misattribution_R_Adj' in merged_data.columns:
                    adj_col = 'Misattribution_R_Adj'
                else:
                    adj_col = dim
                if not pd.isna(row[adj_col]):
                    adj_total += row[adj_col]
            adj_class = self._get_classification(adj_total)
            adj_classifications.append(adj_class)
        
        # Create confusion matrix
        cm = confusion_matrix(adj_classifications, llm_classifications)
        
        # Plot
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Overall Classification Confusion Matrix')
        plt.xlabel('LLM Classification')
        plt.ylabel('Adjudicated Classification')
        plt.tight_layout()
        plt.savefig(self.output_dir / f'overall_classification_confusion_{timestamp}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def calculate_overall_classification_agreement(self, merged_data: pd.DataFrame) -> Dict[str, Any]:
        """Compute percent agreement between LLM and adjudicated overall conversation classification.
        We sum all adjudicated/LLM dimension scores per conversation, map totals to Strong/Moderate/Weak
        via `_get_classification`, then compute the share of conversations where classes match.
        Returns detailed breakdown by label."""
        # Map adjudicated dimension names to ML/RA column names
        dimension_mapping = {
            'Evidence_R_Adj': 'Evidence_R',
            'Testimonial_R_Adj': 'Testimonial_R', 
            'Safety_Rejection_Adj': 'Safety_Rejection',
            'Misatribution_R_Adj': 'Misatribution_R',
            'Promotion_Adj': 'Promotion',
            'HCP_Ref_Adj': 'HCP_Ref'
        }
        
        llm_classes: list[str] = []
        adj_classes: list[str] = []
        any_annotator_classes: list[str] = []
        llm_totals: list[int] = []
        adj_totals: list[int] = []
        any_annotator_totals: list[int] = []
        
        for _, row in merged_data.iterrows():
            # LLM total
            llm_total = 0
            for dim in RUBRIC_DIMENSIONS:
                llm_col = f"{dim}_x" if f"{dim}_x" in merged_data.columns else dim
                val = row.get(llm_col)
                if pd.notna(val):
                    llm_total += val
            llm_totals.append(llm_total)
            llm_classes.append(self._get_classification(llm_total))
            
            # Adjudicated total
            adj_total = 0
            for dim in RUBRIC_DIMENSIONS:
                if f"{dim}_y" in merged_data.columns:
                    adj_col = f"{dim}_y"
                elif dim == 'Misatribution_R_Adj' and 'Misattribution_R_Adj' in merged_data.columns:
                    adj_col = 'Misattribution_R_Adj'
                else:
                    adj_col = dim
                val = row.get(adj_col)
                if pd.notna(val):
                    adj_total += val
            adj_totals.append(adj_total)
            adj_classes.append(self._get_classification(adj_total))
            
            # Any annotator total (RA or ML, whichever is higher)
            any_total = 0
            for dim in RUBRIC_DIMENSIONS:
                base = dimension_mapping.get(dim, dim.replace('_Adj', ''))
                ml_col = f"{base}_ML"
                ra_col = f"{base}_RA"
                
                ml_val = row.get(ml_col)
                ra_val = row.get(ra_col)
                
                # Use the higher of ML or RA score for each dimension
                if pd.notna(ml_val) and pd.notna(ra_val):
                    any_total += max(ml_val, ra_val)
                elif pd.notna(ml_val):
                    any_total += ml_val
                elif pd.notna(ra_val):
                    any_total += ra_val
            any_annotator_totals.append(any_total)
            any_annotator_classes.append(self._get_classification(any_total))
        
        if len(adj_classes) == 0:
            return {"overall_agreement": float('nan'), "by_label": {}, "distributions": {}, "llm_vs_any": {}}
        
        # Overall agreement (LLM vs Adjudicated)
        matches = sum(1 for a, b in zip(adj_classes, llm_classes) if a == b)
        overall_agreement = matches / len(adj_classes) * 100.0
        
        # Overall agreement (LLM vs Any Annotator)
        any_matches = sum(1 for a, b in zip(any_annotator_classes, llm_classes) if a == b)
        llm_vs_any_overall = any_matches / len(any_annotator_classes) * 100.0
        
        # Distribution counts
        adj_dist = {label: adj_classes.count(label) for label in ["Strong", "Moderate", "Weak"]}
        llm_dist = {label: llm_classes.count(label) for label in ["Strong", "Moderate", "Weak"]}
        any_dist = {label: any_annotator_classes.count(label) for label in ["Strong", "Moderate", "Weak"]}
        
        # Agreement by label (LLM vs Adjudicated)
        by_label = {}
        for label in ["Strong", "Moderate", "Weak"]:
            # Find conversations where adjudicated = this label
            label_indices = [i for i, adj_class in enumerate(adj_classes) if adj_class == label]
            if len(label_indices) == 0:
                by_label[label] = {"count": 0, "agreement_pct": float('nan')}
                continue
            
            # Count how many of those also have LLM = this label
            label_matches = sum(1 for i in label_indices if llm_classes[i] == label)
            agreement_pct = (label_matches / len(label_indices)) * 100.0
            
            by_label[label] = {
                "count": len(label_indices),
                "agreement_pct": agreement_pct
            }
        
        # Agreement by label (LLM vs Any Annotator)
        llm_vs_any_by_label = {}
        for label in ["Strong", "Moderate", "Weak"]:
            # Find conversations where any annotator = this label
            label_indices = [i for i, any_class in enumerate(any_annotator_classes) if any_class == label]
            if len(label_indices) == 0:
                llm_vs_any_by_label[label] = {"count": 0, "agreement_pct": float('nan')}
                continue
            
            # Count how many of those also have LLM = this label
            label_matches = sum(1 for i in label_indices if llm_classes[i] == label)
            agreement_pct = (label_matches / len(label_indices)) * 100.0
            
            llm_vs_any_by_label[label] = {
                "count": len(label_indices),
                "agreement_pct": agreement_pct
            }
        
        # Calculate sensitivity, specificity, and F1 for each class
        def calculate_metrics(true_labels, pred_labels, target_class):
            """Calculate sensitivity, specificity, and F1 for a target class."""
            tp = sum(1 for t, p in zip(true_labels, pred_labels) if t == target_class and p == target_class)
            fp = sum(1 for t, p in zip(true_labels, pred_labels) if t != target_class and p == target_class)
            fn = sum(1 for t, p in zip(true_labels, pred_labels) if t == target_class and p != target_class)
            tn = sum(1 for t, p in zip(true_labels, pred_labels) if t != target_class and p != target_class)
            
            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            f1 = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0.0
            
            return {
                "sensitivity": sensitivity,
                "specificity": specificity,
                "precision": precision,
                "f1": f1,
                "tp": tp, "fp": fp, "fn": fn, "tn": tn
            }
        
        # Calculate metrics for each class (LLM vs Adjudicated)
        llm_vs_adj_metrics = {}
        for label in ["Strong", "Moderate", "Weak"]:
            llm_vs_adj_metrics[label] = calculate_metrics(adj_classes, llm_classes, label)
        
        # Calculate metrics for each class (LLM vs Any Annotator)
        llm_vs_any_metrics = {}
        for label in ["Strong", "Moderate", "Weak"]:
            llm_vs_any_metrics[label] = calculate_metrics(any_annotator_classes, llm_classes, label)
        
        # Calculate overall (macro-averaged) metrics
        def calculate_overall_metrics(metrics_dict):
            """Calculate macro-averaged sensitivity, specificity, precision, and F1."""
            sensitivities = [metrics_dict[label]["sensitivity"] for label in ["Strong", "Moderate", "Weak"]]
            specificities = [metrics_dict[label]["specificity"] for label in ["Strong", "Moderate", "Weak"]]
            precisions = [metrics_dict[label]["precision"] for label in ["Strong", "Moderate", "Weak"]]
            f1s = [metrics_dict[label]["f1"] for label in ["Strong", "Moderate", "Weak"]]
            
            return {
                "sensitivity": np.mean(sensitivities),
                "specificity": np.mean(specificities),
                "precision": np.mean(precisions),
                "f1": np.mean(f1s)
            }
        
        llm_vs_adj_overall_metrics = calculate_overall_metrics(llm_vs_adj_metrics)
        llm_vs_any_overall_metrics = calculate_overall_metrics(llm_vs_any_metrics)
        
        return {
            "overall_agreement": overall_agreement,
            "llm_vs_any_overall": llm_vs_any_overall,
            "by_label": by_label,
            "llm_vs_any_by_label": llm_vs_any_by_label,
            "distributions": {
                "adjudicated": adj_dist,
                "llm": llm_dist,
                "any_annotator": any_dist
            },
            "llm_vs_adj_metrics": llm_vs_adj_metrics,
            "llm_vs_any_metrics": llm_vs_any_metrics,
            "llm_vs_adj_overall_metrics": llm_vs_adj_overall_metrics,
            "llm_vs_any_overall_metrics": llm_vs_any_overall_metrics
        }
    
    def _get_classification(self, total_score: float) -> str:
        """Get classification based on total score."""
        if total_score >= CLASSIFICATION_THRESHOLDS['Strong'][0]:
            return 'Strong'
        elif total_score >= CLASSIFICATION_THRESHOLDS['Moderate'][0]:
            return 'Moderate'
        else:
            return 'Weak'
    
    def create_agreement_heatmap(self, fleiss_kappa: Dict[str, float], cohens_kappa: Dict[str, float], timestamp: str):
        """Create heatmap of agreement metrics."""
        # Prepare data
        dimensions = list(RUBRIC_DIMENSIONS)
        metrics = ['Fleiss Kappa', "Cohen's Kappa"]
        
        data = []
        for dim in dimensions:
            row = [fleiss_kappa.get(dim, np.nan), cohens_kappa.get(dim, np.nan)]
            data.append(row)
        
        data = np.array(data)
        
        # Create heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(data, 
                   xticklabels=metrics, 
                   yticklabels=dimensions,
                   annot=True, 
                   fmt='.3f', 
                   cmap='RdYlBu_r',
                   center=0)
        plt.title('Agreement Metrics Heatmap')
        plt.tight_layout()
        plt.savefig(self.output_dir / f'agreement_heatmap_{timestamp}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_summary_report(self, fleiss_kappa: Dict[str, float], cohens_kappa: Dict[str, float], 
                             agreement_percentages: Dict[str, float], timestamp: str,
                             pairwise_pct: Dict[str, Dict[str, float]] = None,
                             fleiss_notes: Dict[str, str] = None,
                             overall_classification: Dict[str, float] = None,
                             overall_classification_agreement: Dict[str, Any] = None):
        """Generate human-readable summary report."""
        summary_file = self.output_dir / f'agreement_summary_{timestamp}.txt'
        
        with open(summary_file, 'w') as f:
            f.write("LLM Judge Agreement Analysis Summary\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Total Conversations: {len(self.predictions)}\n")
            f.write(f"Analysis Date: {timestamp}\n\n")
            
            f.write("FLEISS' KAPPA (3-way agreement: ML, RA, LLM)\n")
            f.write("-" * 80 + "\n")
            for dim in RUBRIC_DIMENSIONS:
                kappa = fleiss_kappa.get(dim, np.nan)
                note = fleiss_notes.get(dim, '') if fleiss_notes else ''
                if note:
                    f.write(f"{dim:25}: {kappa:.3f}  (Note: {note})\n")
                else:
                    f.write(f"{dim:25}: {kappa:.3f}\n")
            f.write("\n")
            
            f.write("COHEN'S KAPPA (LLM vs Adjudicated)\n")
            f.write("-" * 80 + "\n")
            for dim in RUBRIC_DIMENSIONS:
                kappa = cohens_kappa.get(dim, np.nan)
                f.write(f"{dim:25}: {kappa:.3f}\n")
            f.write("\n")

            if pairwise_pct is not None:
                f.write("PAIRWISE PERCENTAGE AGREEMENT\n")
                f.write("-" * 80 + "\n")
                f.write(f"{'Dimension':<25} {'RA↔ML':>10} {'RA↔LLM':>10} {'ML↔LLM':>10}\n")
                f.write("-" * 80 + "\n")
                for dim in RUBRIC_DIMENSIONS:
                    pw = pairwise_pct.get(dim, {})
                    f.write(
                        f"{dim:<25} "
                        f"{pw.get('pct_RA_ML', float('nan')):>9.1f}% "
                        f"{pw.get('pct_RA_LLM', float('nan')):>9.1f}% "
                        f"{pw.get('pct_ML_LLM', float('nan')):>9.1f}%\n"
                    )
                f.write("\n")

            f.write("AGREEMENT PERCENTAGES (3-way & LLM vs Any Human)\n")
            f.write("-" * 80 + "\n")
            for dim in RUBRIC_DIMENSIONS:
                three_way = agreement_percentages.get(f'{dim}_3way_match', 0)
                llm_vs_any = agreement_percentages.get(f'{dim}_llm_vs_any_human', 0)
                f.write(f"{dim:25}: 3-way: {three_way:.1f}%, LLM vs Any: {llm_vs_any:.1f}%\n")
            f.write("\n")
            
            # Overall Classification Section
            if overall_classification:
                f.write("OVERALL CLASSIFICATION (Across All 12 Dimensions)\n")
                f.write("-" * 80 + "\n")
                llm_vs_any = overall_classification.get("llm_vs_any_overall", np.nan)
                avg_dims = overall_classification.get("avg_dims_per_conversation", np.nan)
                classification = overall_classification.get("classification", "Unknown")
                f.write(f"LLM vs Any Human (Overall): {llm_vs_any:.1f}%\n")
                f.write(f"Classification: {classification}\n")
                f.write(f"Average Dimensions per Conversation: {avg_dims:.1f}\n")
                f.write("\n")
            
            # Overall Classification Agreement Section
            if overall_classification_agreement:
                f.write("OVERALL CONVERSATION CLASSIFICATION AGREEMENT\n")
                f.write("-" * 80 + "\n")
                overall_agreement = overall_classification_agreement.get("overall_agreement", np.nan)
                llm_vs_any_overall = overall_classification_agreement.get("llm_vs_any_overall", np.nan)
                f.write(f"Overall Agreement (LLM vs Adjudicated): {overall_agreement:.1f}%\n")
                f.write(f"Overall Agreement (LLM vs Any Annotator): {llm_vs_any_overall:.1f}%\n\n")
                
                # Distribution
                distributions = overall_classification_agreement.get("distributions", {})
                adj_dist = distributions.get("adjudicated", {})
                llm_dist = distributions.get("llm", {})
                any_dist = distributions.get("any_annotator", {})
                f.write("Distribution:\n")
                f.write("Label        Adjudicated    LLM    Any Annotator\n")
                f.write("-" * 50 + "\n")
                for label in ["Strong", "Moderate", "Weak"]:
                    adj_count = adj_dist.get(label, 0)
                    llm_count = llm_dist.get(label, 0)
                    any_count = any_dist.get(label, 0)
                    f.write(f"{label:12} {adj_count:8} {llm_count:8} {any_count:8}\n")
                f.write("\n")
                
                # Agreement by label (LLM vs Adjudicated)
                by_label = overall_classification_agreement.get("by_label", {})
                f.write("Agreement by Adjudicated Label (LLM vs Adjudicated):\n")
                f.write("Label        Count    Agreement\n")
                f.write("-" * 30 + "\n")
                for label in ["Strong", "Moderate", "Weak"]:
                    label_data = by_label.get(label, {})
                    count = label_data.get("count", 0)
                    agreement_pct = label_data.get("agreement_pct", np.nan)
                    if np.isnan(agreement_pct):
                        f.write(f"{label:12} {count:6}    N/A\n")
                    else:
                        f.write(f"{label:12} {count:6}    {agreement_pct:.1f}%\n")
                f.write("\n")
                
                # Agreement by label (LLM vs Any Annotator)
                llm_vs_any_by_label = overall_classification_agreement.get("llm_vs_any_by_label", {})
                f.write("Agreement by Any Annotator Label (LLM vs Any Annotator):\n")
                f.write("Label        Count    Agreement\n")
                f.write("-" * 30 + "\n")
                for label in ["Strong", "Moderate", "Weak"]:
                    label_data = llm_vs_any_by_label.get(label, {})
                    count = label_data.get("count", 0)
                    agreement_pct = label_data.get("agreement_pct", np.nan)
                    if np.isnan(agreement_pct):
                        f.write(f"{label:12} {count:6}    N/A\n")
                    else:
                        f.write(f"{label:12} {count:6}    {agreement_pct:.1f}%\n")
                f.write("\n")
                
                # Sensitivity, Specificity, and F1 Scores
                llm_vs_adj_metrics = overall_classification_agreement.get("llm_vs_adj_metrics", {})
                llm_vs_any_metrics = overall_classification_agreement.get("llm_vs_any_metrics", {})
                
                f.write("CLASSIFICATION METRICS (LLM vs Adjudicated)\n")
                f.write("-" * 80 + "\n")
                f.write("Label        Sensitivity  Specificity  Precision    F1\n")
                f.write("-" * 60 + "\n")
                for label in ["Strong", "Moderate", "Weak"]:
                    metrics = llm_vs_adj_metrics.get(label, {})
                    sensitivity = metrics.get("sensitivity", 0.0)
                    specificity = metrics.get("specificity", 0.0)
                    precision = metrics.get("precision", 0.0)
                    f1 = metrics.get("f1", 0.0)
                    f.write(f"{label:12} {sensitivity:8.3f}   {specificity:8.3f}   {precision:8.3f}   {f1:6.3f}\n")
                f.write("\n")
                
                f.write("CLASSIFICATION METRICS (LLM vs Any Annotator)\n")
                f.write("-" * 80 + "\n")
                f.write("Label        Sensitivity  Specificity  Precision    F1\n")
                f.write("-" * 60 + "\n")
                for label in ["Strong", "Moderate", "Weak"]:
                    metrics = llm_vs_any_metrics.get(label, {})
                    sensitivity = metrics.get("sensitivity", 0.0)
                    specificity = metrics.get("specificity", 0.0)
                    precision = metrics.get("precision", 0.0)
                    f1 = metrics.get("f1", 0.0)
                    f.write(f"{label:12} {sensitivity:8.3f}   {specificity:8.3f}   {precision:8.3f}   {f1:6.3f}\n")
                f.write("\n")
                
                # Overall (macro-averaged) metrics
                llm_vs_adj_overall_metrics = overall_classification_agreement.get("llm_vs_adj_overall_metrics", {})
                llm_vs_any_overall_metrics = overall_classification_agreement.get("llm_vs_any_overall_metrics", {})
                
                f.write("OVERALL CLASSIFICATION METRICS (Macro-Averaged)\n")
                f.write("-" * 80 + "\n")
                f.write("Comparison              Sensitivity  Specificity  Precision    F1\n")
                f.write("-" * 70 + "\n")
                
                adj_sens = llm_vs_adj_overall_metrics.get("sensitivity", 0.0)
                adj_spec = llm_vs_adj_overall_metrics.get("specificity", 0.0)
                adj_prec = llm_vs_adj_overall_metrics.get("precision", 0.0)
                adj_f1 = llm_vs_adj_overall_metrics.get("f1", 0.0)
                f.write(f"LLM vs Adjudicated     {adj_sens:8.3f}   {adj_spec:8.3f}   {adj_prec:8.3f}   {adj_f1:6.3f}\n")
                
                any_sens = llm_vs_any_overall_metrics.get("sensitivity", 0.0)
                any_spec = llm_vs_any_overall_metrics.get("specificity", 0.0)
                any_prec = llm_vs_any_overall_metrics.get("precision", 0.0)
                any_f1 = llm_vs_any_overall_metrics.get("f1", 0.0)
                f.write(f"LLM vs Any Annotator   {any_sens:8.3f}   {any_spec:8.3f}   {any_prec:8.3f}   {any_f1:6.3f}\n")
                f.write("\n")
            
            f.write("INTERPRETATION GUIDE\n")
            f.write("-" * 80 + "\n")
            f.write("Kappa Values:\n")
            f.write("  < 0.20: Poor agreement\n")
            f.write("  0.21-0.40: Fair agreement\n")
            f.write("  0.41-0.60: Moderate agreement\n")
            f.write("  0.61-0.80: Good agreement\n")
            f.write("  > 0.80: Excellent agreement\n")
        
        print(f"Summary report saved to: {summary_file}")
    
    def run_analysis(self, timestamp: str) -> Dict[str, Any]:
        """
        Run complete agreement analysis.
        
        Args:
            timestamp: Timestamp for output files
            
        Returns:
            Dictionary of analysis results
        """
        print("Running agreement analysis...")
        
        # Merge data
        merged_data = self._merge_predictions_with_human_data()
        print(f"Merged {len(merged_data)} conversations with human annotations")
        
        # Calculate metrics
        fleiss_kappa_results, fleiss_notes = self.calculate_fleiss_kappa(merged_data)
        cohens_kappa_results = self.calculate_cohens_kappa(merged_data)
        agreement_percentages = self.calculate_agreement_percentages(merged_data)
        pairwise_pct_agreements = self.calculate_pairwise_agreements(merged_data)
        overall_classification = self.calculate_overall_classification(merged_data)

        # Create visualizations
        self.create_confusion_matrices(merged_data, timestamp)
        self.create_overall_classification_confusion(merged_data, timestamp)
        self.create_agreement_heatmap(fleiss_kappa_results, cohens_kappa_results, timestamp)

        # Generate summary
        overall_classification_agreement = self.calculate_overall_classification_agreement(merged_data)
        self.generate_summary_report(
            fleiss_kappa_results,
            cohens_kappa_results,
            agreement_percentages,
            timestamp,
            pairwise_pct=pairwise_pct_agreements,
            fleiss_notes=fleiss_notes,
            overall_classification=overall_classification,
            overall_classification_agreement=overall_classification_agreement
        )

        # Save detailed results
        results = {
            'fleiss_kappa': fleiss_kappa_results,
            'fleiss_notes': fleiss_notes,
            'cohens_kappa': cohens_kappa_results,
            'pairwise_agreements': pairwise_pct_agreements,
            'agreement_percentages': agreement_percentages,
            'total_conversations': len(merged_data)
        }

        # Save JSON files
        with open(self.output_dir / f'fleiss_kappa_{timestamp}.json', 'w') as f:
            json.dump(fleiss_kappa_results, f, indent=2)
        
        with open(self.output_dir / f'cohens_kappa_{timestamp}.json', 'w') as f:
            json.dump(cohens_kappa_results, f, indent=2)

        # Export CSV side-by-side table
        table_rows = []
        for dim in RUBRIC_DIMENSIONS:
            pw = pairwise_pct_agreements.get(dim, {})
            table_rows.append({
                'dimension': dim,
                'pct_RA_ML': pw.get('pct_RA_ML'),
                'pct_RA_LLM': pw.get('pct_RA_LLM'),
                'pct_ML_LLM': pw.get('pct_ML_LLM'),
                'fleiss_kappa': fleiss_kappa_results.get(dim),
                'cohens_kappa': cohens_kappa_results.get(dim),
                'three_way_pct': agreement_percentages.get(f'{dim}_3way_match'),
                'llm_vs_any_pct': agreement_percentages.get(f'{dim}_llm_vs_any_human'),
                'fleiss_note': fleiss_notes.get(dim, '')
            })
        pd.DataFrame(table_rows).to_csv(self.output_dir / f'agreement_table_{timestamp}.csv', index=False)

        print("Analysis complete!")
        return results
