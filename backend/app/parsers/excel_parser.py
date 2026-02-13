import pandas as pd
from typing import List, Dict, Any
import io


class ExcelParser:
    """Parser for Excel files (.xlsx, .xls)."""
    
    def parse(self, file_content: bytes, sheet_name: str = None) -> List[Dict[str, Any]]:
        """
        Parse Excel file content.
        
        Args:
            file_content: Raw bytes of Excel file
            sheet_name: Name of sheet to parse (None for first sheet)
        
        Returns:
            List of dictionaries, one per row
        """
        # Read Excel
        df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name or 0)
        
        # Convert to list of dicts
        data = df.to_dict(orient="records")
        
        # Clean data (remove NaN values)
        cleaned_data = []
        for row in data:
            cleaned_row = {k: v for k, v in row.items() if pd.notna(v)}
            cleaned_data.append(cleaned_row)
        
        return cleaned_data
    
    def parse_file(self, file_path: str, sheet_name: str = None) -> List[Dict[str, Any]]:
        """Parse Excel file from path."""
        with open(file_path, "rb") as f:
            return self.parse(f.read(), sheet_name)
    
    def get_sheet_names(self, file_content: bytes) -> List[str]:
        """Get all sheet names from Excel file."""
        excel_file = pd.ExcelFile(io.BytesIO(file_content))
        return excel_file.sheet_names
    
    def get_columns(self, file_content: bytes, sheet_name: str = None) -> List[str]:
        """Get column names from Excel."""
        df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name or 0)
        return df.columns.tolist()
    
    def get_sample(self, file_content: bytes, n: int = 5, sheet_name: str = None) -> List[Dict[str, Any]]:
        """Get sample rows from Excel."""
        data = self.parse(file_content, sheet_name)
        return data[:n]


# Singleton instance
excel_parser = ExcelParser()
