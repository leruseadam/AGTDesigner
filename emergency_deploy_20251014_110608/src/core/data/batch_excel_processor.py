"""
Batch Excel processing with smart normalization.
Handles multiple Excel files and provides comprehensive data quality reports.
"""

import os
import logging
import pandas as pd
from typing import List, Dict, Any, Tuple
from pathlib import Path
import sqlite3
from datetime import datetime

from src.core.data.smart_excel_normalizer import SmartExcelNormalizer
from src.core.data.product_database import ProductDatabase

logger = logging.getLogger(__name__)

class BatchExcelProcessor:
    """Process multiple Excel files with comprehensive normalization and reporting."""
    
    def __init__(self, db_path: str = None):
        self.normalizer = SmartExcelNormalizer()
        self.db_path = db_path or 'uploads/product_database_AGT_Bothell.db'
        self.product_db = ProductDatabase(self.db_path)
        
        self.batch_stats = {
            'files_processed': 0,
            'total_products': 0,
            'products_stored': 0,
            'products_updated': 0,
            'errors': 0,
            'normalization_summary': {},
            'processing_time': 0
        }
        
        self.file_reports = []
    
    def process_excel_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Process multiple Excel files with smart normalization.
        
        Args:
            file_paths: List of Excel file paths to process
            
        Returns:
            Dictionary with batch processing results
        """
        start_time = datetime.now()
        
        logger.info(f"Starting batch processing of {len(file_paths)} Excel files")
        
        for file_path in file_paths:
            try:
                self._process_single_file(file_path)
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
                self.batch_stats['errors'] += 1
        
        end_time = datetime.now()
        self.batch_stats['processing_time'] = (end_time - start_time).total_seconds()
        
        # Generate final report
        final_report = self._generate_final_report()
        
        logger.info(f"Batch processing completed in {self.batch_stats['processing_time']:.2f} seconds")
        
        return final_report
    
    def _process_single_file(self, file_path: str):
        """Process a single Excel file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Processing file: {file_path.name}")
        
        # Reset normalizer stats for this file
        self.normalizer.reset_stats()
        
        # Load Excel file
        try:
            df = pd.read_excel(file_path)
            logger.info(f"Loaded {len(df)} rows from {file_path.name}")
        except Exception as e:
            raise Exception(f"Failed to load Excel file: {e}")
        
        # Process each row
        file_stats = {
            'file_name': file_path.name,
            'total_rows': len(df),
            'processed_rows': 0,
            'stored_rows': 0,
            'updated_rows': 0,
            'error_rows': 0,
            'normalization_stats': {}
        }
        
        for index, row in df.iterrows():
            try:
                # Convert row to dictionary
                row_dict = self._row_to_dict(row)
                
                # Skip invalid rows
                if not self._is_valid_row(row_dict):
                    continue
                
                # Smart normalize the row data
                normalized_data = self.normalizer.normalize_product_data(row_dict)
                
                # Store in database
                result = self._store_normalized_data(normalized_data, file_path.name)
                
                file_stats['processed_rows'] += 1
                
                if result == 'stored':
                    file_stats['stored_rows'] += 1
                elif result == 'updated':
                    file_stats['updated_rows'] += 1
                
            except Exception as e:
                logger.error(f"Error processing row {index + 1} in {file_path.name}: {e}")
                file_stats['error_rows'] += 1
        
        # Get normalization stats for this file
        file_stats['normalization_stats'] = self.normalizer.get_normalization_stats()
        
        # Update batch stats
        self.batch_stats['files_processed'] += 1
        self.batch_stats['total_products'] += file_stats['total_rows']
        self.batch_stats['products_stored'] += file_stats['stored_rows']
        self.batch_stats['products_updated'] += file_stats['updated_rows']
        self.batch_stats['errors'] += file_stats['error_rows']
        
        # Add to file reports
        self.file_reports.append(file_stats)
        
        logger.info(f"Completed processing {file_path.name}: {file_stats['processed_rows']} rows processed")
    
    def _row_to_dict(self, row: pd.Series) -> Dict[str, Any]:
        """Convert pandas row to dictionary."""
        row_dict = {}
        for col in row.index:
            value = row[col]
            if pd.isna(value):
                row_dict[col] = None
            else:
                row_dict[col] = str(value).strip() if isinstance(value, str) else value
        
        return row_dict
    
    def _is_valid_row(self, row_dict: Dict[str, Any]) -> bool:
        """Check if row contains valid product data."""
        # Must have product name
        product_name = row_dict.get('Product Name*', row_dict.get('Product Name', ''))
        if not product_name or str(product_name).strip().lower() in ['', 'nan', 'none']:
            return False
        
        return True
    
    def _store_normalized_data(self, normalized_data: Dict[str, Any], source_file: str) -> str:
        """Store normalized data in database."""
        try:
            # Add source information
            normalized_data['Source'] = f'Batch Excel Import - {source_file}'
            normalized_data['Date Added'] = datetime.now().isoformat()
            
            # Store using product database
            product_id = self.product_db.add_or_update_product(normalized_data)
            
            if product_id:
                return 'stored'
            else:
                return 'updated'
                
        except Exception as e:
            logger.error(f"Failed to store normalized data: {e}")
            raise
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report."""
        # Aggregate normalization stats
        total_normalization = {}
        for file_report in self.file_reports:
            for stat_name, count in file_report['normalization_stats'].items():
                total_normalization[stat_name] = total_normalization.get(stat_name, 0) + count
        
        self.batch_stats['normalization_summary'] = total_normalization
        
        final_report = {
            'batch_summary': self.batch_stats,
            'file_reports': self.file_reports,
            'normalization_summary': total_normalization,
            'data_quality_metrics': self._calculate_data_quality_metrics(),
            'recommendations': self._generate_recommendations()
        }
        
        return final_report
    
    def _calculate_data_quality_metrics(self) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        if self.batch_stats['total_products'] == 0:
            return {}
        
        success_rate = ((self.batch_stats['products_stored'] + self.batch_stats['products_updated']) / 
                       self.batch_stats['total_products']) * 100
        
        error_rate = (self.batch_stats['errors'] / self.batch_stats['total_products']) * 100
        
        return {
            'success_rate_percent': round(success_rate, 2),
            'error_rate_percent': round(error_rate, 2),
            'normalization_impact': self._calculate_normalization_impact()
        }
    
    def _calculate_normalization_impact(self) -> Dict[str, Any]:
        """Calculate the impact of normalization."""
        total_products = self.batch_stats['total_products']
        if total_products == 0:
            return {}
        
        normalization_summary = self.batch_stats['normalization_summary']
        
        impact = {}
        for stat_name, count in normalization_summary.items():
            percentage = (count / total_products) * 100
            impact[stat_name] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        return impact
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on processing results."""
        recommendations = []
        
        # Error rate recommendations
        error_rate = self.batch_stats['errors'] / max(self.batch_stats['total_products'], 1)
        if error_rate > 0.1:  # More than 10% errors
            recommendations.append("High error rate detected. Review Excel file format and data quality.")
        
        # Normalization recommendations
        normalization_summary = self.batch_stats['normalization_summary']
        
        if normalization_summary.get('weights_normalized', 0) > 0:
            recommendations.append("Weight normalization applied. Consider standardizing weight units in source Excel files.")
        
        if normalization_summary.get('names_cleaned', 0) > 0:
            recommendations.append("Product names were cleaned. Review naming conventions in source data.")
        
        if normalization_summary.get('brands_standardized', 0) > 0:
            recommendations.append("Brand names were standardized. Consider using consistent brand naming.")
        
        if normalization_summary.get('types_corrected', 0) > 0:
            recommendations.append("Product types were corrected. Verify product type classifications.")
        
        if normalization_summary.get('prices_normalized', 0) > 0:
            recommendations.append("Prices were normalized. Use consistent price formatting in source files.")
        
        # Performance recommendations
        if self.batch_stats['processing_time'] > 60:  # More than 1 minute
            recommendations.append("Processing took longer than expected. Consider breaking large files into smaller batches.")
        
        return recommendations
    
    def export_processing_report(self, output_path: str):
        """Export processing report to file."""
        try:
            final_report = self._generate_final_report()
            
            with open(output_path, 'w') as f:
                f.write("# Excel Batch Processing Report\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Batch summary
                f.write("## Batch Summary\n\n")
                f.write(f"- Files Processed: {final_report['batch_summary']['files_processed']}\n")
                f.write(f"- Total Products: {final_report['batch_summary']['total_products']}\n")
                f.write(f"- Products Stored: {final_report['batch_summary']['products_stored']}\n")
                f.write(f"- Products Updated: {final_report['batch_summary']['products_updated']}\n")
                f.write(f"- Errors: {final_report['batch_summary']['errors']}\n")
                f.write(f"- Processing Time: {final_report['batch_summary']['processing_time']:.2f} seconds\n\n")
                
                # Data quality metrics
                f.write("## Data Quality Metrics\n\n")
                metrics = final_report['data_quality_metrics']
                f.write(f"- Success Rate: {metrics.get('success_rate_percent', 0)}%\n")
                f.write(f"- Error Rate: {metrics.get('error_rate_percent', 0)}%\n\n")
                
                # Normalization summary
                f.write("## Normalization Summary\n\n")
                for stat_name, data in final_report['normalization_summary'].items():
                    if isinstance(data, dict):
                        f.write(f"- {stat_name}: {data['count']} ({data['percentage']}%)\n")
                    else:
                        f.write(f"- {stat_name}: {data}\n")
                
                f.write("\n## Recommendations\n\n")
                for i, rec in enumerate(final_report['recommendations'], 1):
                    f.write(f"{i}. {rec}\n")
                
                f.write("\n## File Reports\n\n")
                for file_report in final_report['file_reports']:
                    f.write(f"### {file_report['file_name']}\n")
                    f.write(f"- Total Rows: {file_report['total_rows']}\n")
                    f.write(f"- Processed: {file_report['processed_rows']}\n")
                    f.write(f"- Stored: {file_report['stored_rows']}\n")
                    f.write(f"- Updated: {file_report['updated_rows']}\n")
                    f.write(f"- Errors: {file_report['error_rows']}\n\n")
            
            logger.info(f"Processing report exported to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export processing report: {e}")
            raise

# Utility function for batch processing
def batch_process_excel_files(file_paths: List[str], db_path: str = None, 
                            export_report: str = None) -> Dict[str, Any]:
    """
    Convenience function for batch processing Excel files.
    
    Args:
        file_paths: List of Excel file paths
        db_path: Database path (optional)
        export_report: Path to export report (optional)
        
    Returns:
        Processing results dictionary
    """
    processor = BatchExcelProcessor(db_path)
    results = processor.process_excel_files(file_paths)
    
    if export_report:
        processor.export_processing_report(export_report)
    
    return results
