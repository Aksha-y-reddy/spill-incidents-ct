"""
Connecticut Spill Incidents Data Processing Module
This module handles data cleaning, preprocessing, and transformation
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import logging
from typing import Tuple, List, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpillDataProcessor:
    """
    A comprehensive data processor for Connecticut spill incidents data.
    """
    
    def __init__(self, raw_data_path: str):
        """
        Initialize the data processor.
        
        Args:
            raw_data_path (str): Path to the raw CSV data file
        """
        self.raw_data_path = raw_data_path
        self.df = None
        self.cleaned_df = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Load the raw data from CSV file.
        
        Returns:
            pd.DataFrame: Raw loaded dataframe
        """
        try:
            logger.info("Loading raw data from CSV...")
            self.df = pd.read_csv(self.raw_data_path, low_memory=False)
            logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
            return self.df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def clean_column_names(self) -> None:
        """Clean and standardize column names."""
        logger.info("Cleaning column names...")
        
        # Create a mapping for cleaner column names
        column_mapping = {
            'Case No.': 'case_number',
            'Date Reported Time Reported': 'date_reported',
            'Release date and time': 'release_datetime',
            'Town of Release': 'town',
            'State of Release': 'state',
            'Responsibile Party/Discharger': 'responsible_party',
            'Responsible Party Address': 'responsible_party_address',
            'Responsible Party Town': 'responsible_party_town',
            'Responsible Party State': 'responsible_party_state',
            'Responsible Party Zip': 'responsible_party_zip',
            'Responsible Party Accepts Responsibility (Y/N)': 'accepts_responsibility',
            'Release Type': 'release_type',
            'Location Of Reported Release': 'release_location',
            'Release Substance': 'substance',
            'Total Quantity Gallons': 'quantity_gallons',
            'Total Quantity Yards': 'quantity_yards',
            'Total Quantity Feet': 'quantity_feet',
            'Total Quantity Drums': 'quantity_drums',
            'Total Quantity Pounds': 'quantity_pounds',
            'Emergency Measures': 'emergency_measures',
            'Type of Waterbody Affected': 'waterbody_type',
            'Waterbodies Affected': 'waterbodies_affected',
            'Corrective Actions Taken': 'corrective_actions',
            'Cause Info': 'cause',
            'Media Info': 'media',
            'Assigned to': 'assigned_to',
            'Reported By': 'reported_by',
            'Representing': 'representing',
            'Status': 'status'
        }
        
        # Apply the mapping
        self.df.rename(columns=column_mapping, inplace=True)
        
        # Clean any remaining column names
        self.df.columns = [col.lower().replace(' ', '_').replace('/', '_') 
                          for col in self.df.columns]
        
        logger.info("Column names cleaned successfully.")
    
    def parse_datetime_columns(self) -> None:
        """Parse and clean datetime columns."""
        logger.info("Parsing datetime columns...")
        
        # Parse release datetime
        self.df['release_datetime'] = pd.to_datetime(
            self.df['release_datetime'], errors='coerce'
        )
        
        # Parse date reported
        self.df['date_reported'] = pd.to_datetime(
            self.df['date_reported'], errors='coerce'
        )
        
        # Extract useful datetime components
        self.df['release_year'] = self.df['release_datetime'].dt.year
        self.df['release_month'] = self.df['release_datetime'].dt.month
        self.df['release_day'] = self.df['release_datetime'].dt.day
        self.df['release_hour'] = self.df['release_datetime'].dt.hour
        self.df['release_dayofweek'] = self.df['release_datetime'].dt.dayofweek
        self.df['release_quarter'] = self.df['release_datetime'].dt.quarter
        
        # Create time periods for analysis
        self.df['time_period'] = self.df['release_hour'].apply(
            self._categorize_time_period
        )
        
        logger.info("Datetime columns parsed successfully.")
    
    def _categorize_time_period(self, hour: int) -> str:
        """Categorize hours into time periods."""
        if pd.isna(hour):
            return 'Unknown'
        elif 6 <= hour < 12:
            return 'Morning (06:00-12:00)'
        elif 12 <= hour < 18:
            return 'Afternoon (12:00-18:00)'
        elif 18 <= hour < 24:
            return 'Evening (18:00-24:00)'
        else:
            return 'Night (00:00-06:00)'
    
    def clean_numeric_columns(self) -> None:
        """Clean and standardize numeric quantity columns."""
        logger.info("Cleaning numeric columns...")
        
        quantity_columns = [
            'quantity_gallons', 'quantity_yards', 'quantity_feet',
            'quantity_drums', 'quantity_pounds'
        ]
        
        for col in quantity_columns:
            if col in self.df.columns:
                # Clean the column by removing non-numeric characters except decimal points
                self.df[col] = self.df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                
                # Fill NaN values with 0 for quantity columns
                self.df[col] = self.df[col].fillna(0)
        
        # Create total quantity in standardized unit (gallons equivalent)
        self.df['total_quantity_equivalent'] = (
            self.df.get('quantity_gallons', 0) +
            self.df.get('quantity_yards', 0) * 202 +  # Approximate conversion
            self.df.get('quantity_feet', 0) * 7.48 +  # Cubic feet to gallons
            self.df.get('quantity_drums', 0) * 55 +   # Standard drum size
            self.df.get('quantity_pounds', 0) * 0.12  # Approximate for petroleum
        )
        
        logger.info("Numeric columns cleaned successfully.")
    
    def clean_categorical_columns(self) -> None:
        """Clean and standardize categorical columns."""
        logger.info("Cleaning categorical columns...")
        
        # Clean town names
        if 'town' in self.df.columns:
            self.df['town'] = self.df['town'].str.upper().str.strip()
            
        # Clean substance categories
        if 'substance' in self.df.columns:
            self.df['substance_category'] = self.df['substance'].apply(
                self._categorize_substance
            )
        
        # Clean cause categories
        if 'cause' in self.df.columns:
            self.df['cause_category'] = self.df['cause'].apply(
                self._categorize_cause
            )
        
        # Clean state
        if 'state' in self.df.columns:
            self.df['state'] = self.df['state'].str.upper().str.strip()
        
        logger.info("Categorical columns cleaned successfully.")
    
    def _categorize_substance(self, substance: str) -> str:
        """Categorize substances into broader categories."""
        if pd.isna(substance):
            return 'Unknown'
        
        substance = str(substance).upper()
        
        if any(keyword in substance for keyword in [
            'GASOLINE', 'DIESEL', 'FUEL', 'OIL', 'PETROLEUM', 'HYDRAULIC'
        ]):
            return 'Petroleum Products'
        elif any(keyword in substance for keyword in [
            'CHEMICAL', 'ACID', 'SOLVENT', 'PAINT'
        ]):
            return 'Chemicals'
        elif any(keyword in substance for keyword in [
            'WASTE', 'SEWAGE'
        ]):
            return 'Waste Products'
        else:
            return 'Other'
    
    def _categorize_cause(self, cause: str) -> str:
        """Categorize causes into broader categories."""
        if pd.isna(cause):
            return 'Unknown'
        
        cause = str(cause).upper()
        
        if 'MV' in cause or 'MOTOR VEHICLE' in cause or 'ACCIDENT' in cause:
            return 'Motor Vehicle Accident'
        elif 'EQUIPMENT' in cause or 'FAILURE' in cause or 'MECHANICAL' in cause:
            return 'Equipment Failure'
        elif 'HUMAN' in cause or 'OPERATOR' in cause or 'ERROR' in cause:
            return 'Human Error'
        elif 'WEATHER' in cause or 'NATURAL' in cause:
            return 'Natural Causes'
        else:
            return 'Other'
    
    def filter_research_timeframe(self, start_year: int = 2019, end_year: int = 2022) -> None:
        """
        Filter data to the research timeframe (2019-2022 as per original research).
        
        Args:
            start_year (int): Starting year for analysis
            end_year (int): Ending year for analysis
        """
        logger.info(f"Filtering data to timeframe: {start_year}-{end_year}")
        
        if 'release_year' in self.df.columns:
            initial_count = len(self.df)
            self.df = self.df[
                (self.df['release_year'] >= start_year) & 
                (self.df['release_year'] <= end_year)
            ].copy()
            final_count = len(self.df)
            
            logger.info(f"Filtered from {initial_count} to {final_count} records")
        else:
            logger.warning("release_year column not found. Cannot filter by timeframe.")
    
    def handle_missing_values(self) -> None:
        """Handle missing values according to research methodology."""
        logger.info("Handling missing values...")
        
        # Fill categorical missing values
        categorical_columns = ['town', 'substance', 'cause', 'responsible_party']
        for col in categorical_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('Unknown')
        
        # Fill numeric missing values
        numeric_columns = ['release_hour', 'release_year']
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(self.df[col].median())
        
        logger.info("Missing values handled successfully.")
    
    def remove_outliers(self, columns: List[str] = None) -> None:
        """
        Remove outliers using IQR method.
        
        Args:
            columns (List[str]): Columns to check for outliers
        """
        if columns is None:
            columns = ['total_quantity_equivalent']
        
        logger.info(f"Removing outliers from columns: {columns}")
        
        initial_count = len(self.df)
        
        for col in columns:
            if col in self.df.columns:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                self.df = self.df[
                    (self.df[col] >= lower_bound) & 
                    (self.df[col] <= upper_bound)
                ].copy()
        
        final_count = len(self.df)
        logger.info(f"Removed {initial_count - final_count} outlier records")
    
    def create_derived_features(self) -> None:
        """Create additional features for analysis."""
        logger.info("Creating derived features...")
        
        # Create geographic regions
        self.df['region'] = self.df['town'].apply(self._assign_region)
        
        # Create incident severity based on quantity
        self.df['incident_severity'] = self.df['total_quantity_equivalent'].apply(
            self._categorize_severity
        )
        
        # Create response time (if possible)
        if 'date_reported' in self.df.columns and 'release_datetime' in self.df.columns:
            self.df['response_time_hours'] = (
                self.df['date_reported'] - self.df['release_datetime']
            ).dt.total_seconds() / 3600
        
        logger.info("Derived features created successfully.")
    
    def _assign_region(self, town: str) -> str:
        """Assign Connecticut regions based on town."""
        if pd.isna(town):
            return 'Unknown'
        
        # Connecticut regions (simplified)
        eastern_towns = ['GROTON', 'NEW LONDON', 'WATERFORD', 'MONTVILLE', 'LEBANON']
        western_towns = ['STAMFORD', 'NORWALK', 'DANBURY', 'BRIDGEPORT', 'WESTPORT']
        central_towns = ['HARTFORD', 'NEW BRITAIN', 'MIDDLETOWN', 'MERIDEN']
        northern_towns = ['ENFIELD', 'WINDSOR', 'MANCHESTER', 'VERNON']
        southern_towns = ['NEW HAVEN', 'MILFORD', 'WEST HAVEN', 'GUILFORD']
        
        town = str(town).upper()
        
        if any(t in town for t in eastern_towns):
            return 'Eastern Connecticut'
        elif any(t in town for t in western_towns):
            return 'Western Connecticut'
        elif any(t in town for t in central_towns):
            return 'Central Connecticut'
        elif any(t in town for t in northern_towns):
            return 'Northern Connecticut'
        elif any(t in town for t in southern_towns):
            return 'Southern Connecticut'
        else:
            return 'Other Connecticut'
    
    def _categorize_severity(self, quantity: float) -> str:
        """Categorize incident severity based on quantity."""
        if pd.isna(quantity) or quantity == 0:
            return 'Unknown/Minimal'
        elif quantity < 10:
            return 'Low'
        elif quantity < 100:
            return 'Medium'
        elif quantity < 1000:
            return 'High'
        else:
            return 'Very High'
    
    def validate_data_quality(self) -> Dict[str, int]:
        """Validate data quality and return summary statistics."""
        logger.info("Validating data quality...")
        
        validation_summary = {
            'total_records': len(self.df),
            'missing_town': self.df['town'].isna().sum(),
            'missing_datetime': self.df['release_datetime'].isna().sum(),
            'missing_substance': self.df['substance'].isna().sum(),
            'missing_cause': self.df['cause'].isna().sum(),
            'duplicate_records': self.df.duplicated().sum(),
            'invalid_years': ((self.df['release_year'] < 1990) | 
                             (self.df['release_year'] > 2024)).sum()
        }
        
        # Log validation results
        for key, value in validation_summary.items():
            logger.info(f"{key}: {value}")
        
        return validation_summary
    
    def process_all(self, 
                   filter_timeframe: bool = True,
                   remove_outliers_flag: bool = True,
                   start_year: int = 2019,
                   end_year: int = 2022) -> pd.DataFrame:
        """
        Execute the complete data processing pipeline.
        
        Args:
            filter_timeframe (bool): Whether to filter to research timeframe
            remove_outliers_flag (bool): Whether to remove outliers
            start_year (int): Start year for filtering
            end_year (int): End year for filtering
        
        Returns:
            pd.DataFrame: Cleaned and processed dataframe
        """
        logger.info("Starting complete data processing pipeline...")
        
        # Load data if not already loaded
        if self.df is None:
            self.load_data()
        
        # Execute processing steps
        self.clean_column_names()
        self.parse_datetime_columns()
        self.clean_numeric_columns()
        self.clean_categorical_columns()
        
        if filter_timeframe:
            self.filter_research_timeframe(start_year, end_year)
        
        self.handle_missing_values()
        
        if remove_outliers_flag:
            self.remove_outliers()
        
        self.create_derived_features()
        
        # Store cleaned dataframe
        self.cleaned_df = self.df.copy()
        
        # Validate data quality
        validation_summary = self.validate_data_quality()
        
        logger.info("Data processing pipeline completed successfully!")
        
        return self.cleaned_df
    
    def save_cleaned_data(self, output_path: str) -> None:
        """
        Save the cleaned data to CSV.
        
        Args:
            output_path (str): Path to save the cleaned data
        """
        if self.cleaned_df is not None:
            self.cleaned_df.to_csv(output_path, index=False)
            logger.info(f"Cleaned data saved to: {output_path}")
        else:
            logger.error("No cleaned data available. Run process_all() first.")
    
    def get_data_summary(self) -> pd.DataFrame:
        """Get a summary of the processed data."""
        if self.cleaned_df is not None:
            summary = pd.DataFrame({
                'Column': self.cleaned_df.columns,
                'Data_Type': self.cleaned_df.dtypes,
                'Non_Null_Count': self.cleaned_df.count(),
                'Null_Count': self.cleaned_df.isnull().sum(),
                'Unique_Values': self.cleaned_df.nunique()
            })
            return summary
        else:
            logger.error("No cleaned data available. Run process_all() first.")
            return None


# Example usage and testing
if __name__ == "__main__":
    # Initialize processor
    processor = SpillDataProcessor('data/raw/spill_incidents_raw.csv')
    
    # Process data
    cleaned_data = processor.process_all()
    
    # Save cleaned data
    processor.save_cleaned_data('data/processed/spill_incidents_clean.csv')
    
    # Get summary
    summary = processor.get_data_summary()
    print("Data Summary:")
    print(summary.head(10)) 