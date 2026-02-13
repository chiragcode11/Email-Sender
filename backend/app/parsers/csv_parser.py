import pandas as pd
from typing import List, Dict, Any
import io


class CSVParser:
    """Parser for CSV files."""
    
    def parse(self, file_content: bytes) -> List[Dict[str, Any]]:
        """
        Parse CSV file content.
        
        Args:
            file_content: Raw bytes of CSV file
        
        Returns:
            List of dictionaries, one per row
        """
        # Read CSV
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Convert to list of dicts
        data = df.to_dict(orient="records")
        
        # Clean data (remove NaN values)
        cleaned_data = []
        for row in data:
            cleaned_row = {k: v for k, v in row.items() if pd.notna(v)}
            cleaned_data.append(cleaned_row)
        
        return cleaned_data
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse CSV file from path."""
        with open(file_path, "rb") as f:
            return self.parse(f.read())
    
    def get_columns(self, file_content: bytes) -> List[str]:
        """Get column names from CSV."""
        df = pd.read_csv(io.BytesIO(file_content))
        return df.columns.tolist()
    
    def get_sample(self, file_content: bytes, n: int = 5) -> List[Dict[str, Any]]:
        """Get sample rows from CSV."""
        data = self.parse(file_content)
        return data[:n]


# Singleton instance
csv_parser = CSVParser()
