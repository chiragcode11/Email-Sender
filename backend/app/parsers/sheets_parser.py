import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Any, Optional
from app.config import settings


class GoogleSheetsParser:
    """Parser for Google Sheets."""
    
    def __init__(self):
        self.client = None
    
    def connect(self, credentials_file: Optional[str] = None):
        """Connect to Google Sheets API."""
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file or settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
            scope
        )
        
        self.client = gspread.authorize(creds)
    
    def parse_sheet(
        self,
        spreadsheet_id: str,
        worksheet_name: Optional[str] = None,
        worksheet_index: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Parse data from Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet (from URL)
            worksheet_name: Name of worksheet (None to use index)
            worksheet_index: Index of worksheet (0 for first sheet)
        
        Returns:
            List of dictionaries, one per row
        """
        if not self.client:
            raise Exception("Not connected to Google Sheets API")
        
        # Open spreadsheet
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        
        # Get worksheet
        if worksheet_name:
            worksheet = spreadsheet.worksheet(worksheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(worksheet_index)
        
        # Get all records (first row as headers)
        data = worksheet.get_all_records()
        
        return data
    
    def parse_sheet_by_url(self, url: str, worksheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Parse sheet by URL."""
        if not self.client:
            raise Exception("Not connected to Google Sheets API")
        
        # Open by URL
        spreadsheet = self.client.open_by_url(url)
        
        # Get worksheet
        if worksheet_name:
            worksheet = spreadsheet.worksheet(worksheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)
        
        # Get all records
        data = worksheet.get_all_records()
        
        return data
    
    def get_worksheets(self, spreadsheet_id: str) -> List[str]:
        """Get all worksheet names from spreadsheet."""
        if not self.client:
            raise Exception("Not connected to Google Sheets API")
        
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        worksheets = spreadsheet.worksheets()
        
        return [ws.title for ws in worksheets]
    
    def get_columns(self, spreadsheet_id: str, worksheet_name: Optional[str] = None) -> List[str]:
        """Get column headers from sheet."""
        if not self.client:
            raise Exception("Not connected to Google Sheets API")
        
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        
        if worksheet_name:
            worksheet = spreadsheet.worksheet(worksheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)
        
        # Get first row (headers)
        headers = worksheet.row_values(1)
        
        return headers
    
    def get_sample(
        self,
        spreadsheet_id: str,
        n: int = 5,
        worksheet_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get sample rows from sheet."""
        data = self.parse_sheet(spreadsheet_id, worksheet_name)
        return data[:n]


# Singleton instance
sheets_parser = GoogleSheetsParser()
