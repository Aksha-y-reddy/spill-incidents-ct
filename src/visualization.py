"""
Connecticut Spill Incidents Visualization Module

Author: Akshay Govindareddy
Date: 2022
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium.plugins import HeatMap
import warnings
warnings.filterwarnings('ignore')


# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Color palettes
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#C73E1D',
    'warning': '#F4B942',
    'info': '#3D5A80'
}

class SpillVisualization:
    """
    Comprehensive visualization class for Connecticut spill incidents analysis.
    """
    
    def __init__(self, data: pd.DataFrame, figsize: tuple = (12, 8)):
        """
        Initialize the visualization class.
        
        Args:
            data (pd.DataFrame): Cleaned spill incidents data
            figsize (tuple): Default figure size for matplotlib plots
        """
        self.data = data
        self.figsize = figsize
        
        # Set up plotting style
        plt.rcParams['figure.figsize'] = figsize
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
    
    def year_wise_incidents_by_cities(self, top_n: int = 10, save_path: str = None):
        """
        Analyze year-wise distribution of spill incidents across top cities.
        
        Args:
            top_n (int): Number of top cities to display
            save_path (str): Path to save the figure
        """
        # Get top cities by total incidents
        top_cities = self.data.groupby('town').size().nlargest(top_n).index
        
        # Filter data for top cities
        city_data = self.data[self.data['town'].isin(top_cities)]
        
        # Create year-wise incident counts
        incident_counts = city_data.groupby(['release_year', 'town']).size().unstack(fill_value=0)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Create stacked bar plot
        incident_counts.plot(kind='bar', stacked=True, ax=ax, 
                           colormap='tab20', alpha=0.8)
        
        ax.set_title('Year-wise Number of Spill Incidents by Top Cities\n(2019-2022)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Number of Incidents', fontsize=12)
        ax.legend(title='Town', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=0)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return fig
    
    def cities_highest_spills(self, top_n: int = 25, save_path: str = None):
        """
        Analyze cities with highest number of spill incidents from 2019-2022.
        
        Args:
            top_n (int): Number of top cities to display
            save_path (str): Path to save the figure
        """
        # Get top cities by incident count
        city_counts = self.data.groupby('town').size().nlargest(top_n)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Create horizontal bar plot
        bars = ax.barh(range(len(city_counts)), city_counts.values, 
                      color=COLORS['primary'], alpha=0.8)
        
        # Customize the plot
        ax.set_yticks(range(len(city_counts)))
        ax.set_yticklabels(city_counts.index)
        ax.set_xlabel('Number of Spill Incidents', fontsize=12)
        ax.set_title(f'Top {top_n} Cities with Highest Spills (2019-2022)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()  # Show highest at top
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return fig
    
    def time_of_day_incidents(self, save_path: str = None):
        """
        Analyze temporal patterns of spill incidents throughout the day.
        
        Args:
            save_path (str): Path to save the figure
        """
        # Group by hour
        hourly_counts = self.data.groupby('release_hour').size()
        
        # Create the plot
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Create line plot with markers
        ax.plot(hourly_counts.index, hourly_counts.values, 
               marker='o', linewidth=3, markersize=8, 
               color=COLORS['primary'], alpha=0.8)
        
        # Highlight peak hours (15-18)
        peak_hours = hourly_counts[15:19]
        ax.fill_between(peak_hours.index, peak_hours.values, 
                       alpha=0.3, color=COLORS['secondary'],
                       label='Peak Hours (15:00-18:00)')
        
        ax.set_title('Spill Incidents by Time of Day (2019-2022)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Hour of Day', fontsize=12)
        ax.set_ylabel('Number of Incidents', fontsize=12)
        ax.set_xticks(range(0, 24, 2))
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Add annotation for peak
        max_hour = hourly_counts.idxmax()
        max_count = hourly_counts.max()
        ax.annotate(f'Peak: {max_hour}:00\n({max_count} incidents)', 
                   xy=(max_hour, max_count), xytext=(max_hour+2, max_count+50),
                   arrowprops=dict(arrowstyle='->', color='red', lw=2),
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return fig
    
    def main_causes_analysis(self, save_path: str = None):
        """
        Analyze the main causes and contributing factors for spill incidents.
        
        Args:
            save_path (str): Path to save the figure
        """
        # Get cause distribution
        cause_counts = self.data['cause_category'].value_counts()
        
        # Create subplot with pie and bar chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(cause_counts)))
        wedges, texts, autotexts = ax1.pie(cause_counts.values, labels=cause_counts.index, 
                                          autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.set_title('Distribution of Spill Causes\n(Pie Chart)', fontsize=14, fontweight='bold')
        
        # Bar chart
        bars = ax2.bar(range(len(cause_counts)), cause_counts.values, 
                      color=colors, alpha=0.8)
        ax2.set_title('Distribution of Spill Causes\n(Bar Chart)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Cause Category', fontsize=12)
        ax2.set_ylabel('Number of Incidents', fontsize=12)
        ax2.set_xticks(range(len(cause_counts)))
        ax2.set_xticklabels(cause_counts.index, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('Main Causes for Spill Incidents (2019-2022)', 
                    fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return fig
    
    def top_cities_spillages(self, top_n: int = 25, save_path: str = None):
        """
        Analyze top cities with the most spillage incidents for comprehensive assessment.
        
        Args:
            top_n (int): Number of top cities to display
            save_path (str): Path to save the figure
        """
        # This provides similar analysis to cities_highest_spills with different styling
        return self.cities_highest_spills(top_n, save_path)
    
    def spill_amount_per_incident(self, save_path: str = None):
        """
        Analyze the distribution and patterns of spill quantities per incident.
        
        Args:
            save_path (str): Path to save the figure
        """
        # Filter out zero quantities for better visualization
        non_zero_data = self.data[self.data['total_quantity_equivalent'] > 0]
        
        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Histogram
        ax1.hist(non_zero_data['total_quantity_equivalent'], bins=50, 
                alpha=0.7, color=COLORS['primary'], edgecolor='black')
        ax1.set_title('Distribution of Spill Quantities\n(Histogram)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Spill Quantity (Gallons Equivalent)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_yscale('log')  # Log scale for better visualization
        ax1.grid(True, alpha=0.3)
        
        # Box plot by severity category
        severity_data = [non_zero_data[non_zero_data['incident_severity'] == severity]['total_quantity_equivalent'].values 
                        for severity in non_zero_data['incident_severity'].unique()]
        severity_labels = non_zero_data['incident_severity'].unique()
        
        bp = ax2.boxplot(severity_data, labels=severity_labels, patch_artist=True)
        ax2.set_title('Spill Quantities by Severity Category\n(Box Plot)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Incident Severity', fontsize=12)
        ax2.set_ylabel('Spill Quantity (Gallons Equivalent)', fontsize=12)
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3)
        
        # Color the box plots
        colors = plt.cm.viridis(np.linspace(0, 1, len(bp['boxes'])))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        plt.suptitle('Amount of Spill per Incident (2019-2022)', 
                    fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return fig
    
    def common_substances_analysis(self, top_n: int = 15, save_path: str = None):
        """
        Analyze the most frequently released substance types in spill incidents.
        
        Args:
            top_n (int): Number of top substances to display
            save_path (str): Path to save the figure
        """
        # Get top substances
        substance_counts = self.data['substance_category'].value_counts().head(top_n)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Create bar plot
        bars = ax.bar(range(len(substance_counts)), substance_counts.values, 
                     color=COLORS['accent'], alpha=0.8)
        
        ax.set_title(f'Top {top_n} Most Common Substances Released (2019-2022)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Substance Category', fontsize=12)
        ax.set_ylabel('Number of Incidents', fontsize=12)
        ax.set_xticks(range(len(substance_counts)))
        ax.set_xticklabels(substance_counts.index, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return fig
    
    def create_interactive_geographic_map(self):
        """
        Create an interactive map showing spill incidents by location.
        
        Returns:
            folium.Map: Interactive map object
        """
        # Get incident counts by town
        town_counts = self.data.groupby('town').agg({
            'case_number': 'count',
            'total_quantity_equivalent': 'sum'
        }).rename(columns={'case_number': 'incident_count'})
        
        # Connecticut coordinates (approximate center)
        ct_coords = [41.6032, -73.0877]
        
        # Create base map
        m = folium.Map(location=ct_coords, zoom_start=8, 
                      tiles='OpenStreetMap')
        
        # Add incident data (simplified - would need geocoding for exact coordinates)
        # This is a conceptual implementation
        for town, data in town_counts.iterrows():
            if pd.notna(town):
                # Add markers (coordinates would need to be geocoded)
                folium.CircleMarker(
                    location=[ct_coords[0] + np.random.uniform(-0.5, 0.5),
                             ct_coords[1] + np.random.uniform(-0.5, 0.5)],
                    radius=min(data['incident_count'] / 10, 50),
                    popup=f"Town: {town}<br>Incidents: {data['incident_count']}<br>Total Quantity: {data['total_quantity_equivalent']:.2f}",
                    color='red',
                    fill=True,
                    fillOpacity=0.6
                ).add_to(m)
        
        return m
    
    def create_interactive_time_series(self):
        """
        Create an interactive time series plot using Plotly.
        
        Returns:
            plotly.graph_objects.Figure: Interactive time series plot
        """
        # Create monthly time series
        monthly_data = self.data.groupby([
            self.data['release_datetime'].dt.to_period('M')
        ]).agg({
            'case_number': 'count',
            'total_quantity_equivalent': 'sum'
        }).reset_index()
        
        monthly_data['date'] = monthly_data['release_datetime'].dt.to_timestamp()
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Number of Incidents Over Time', 'Total Quantity Spilled Over Time'),
            vertical_spacing=0.1
        )
        
        # Add incident count trace
        fig.add_trace(
            go.Scatter(
                x=monthly_data['date'],
                y=monthly_data['case_number'],
                mode='lines+markers',
                name='Incident Count',
                line=dict(color=COLORS['primary'], width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Add quantity trace
        fig.add_trace(
            go.Scatter(
                x=monthly_data['date'],
                y=monthly_data['total_quantity_equivalent'],
                mode='lines+markers',
                name='Total Quantity',
                line=dict(color=COLORS['secondary'], width=3),
                marker=dict(size=8)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title_text="Connecticut Spill Incidents Time Series Analysis",
            title_x=0.5,
            height=600,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Number of Incidents", row=1, col=1)
        fig.update_yaxes(title_text="Total Quantity (Gallons Equiv.)", row=2, col=1)
        
        return fig
    
    def create_correlation_heatmap(self, save_path: str = None):
        """
        Create a correlation heatmap of numeric variables.
        
        Args:
            save_path (str): Path to save the figure
        """
        # Select numeric columns
        numeric_cols = [
            'release_year', 'release_month', 'release_hour', 
            'quantity_gallons', 'total_quantity_equivalent',
            'response_time_hours'
        ]
        
        # Filter columns that exist in the data
        available_cols = [col for col in numeric_cols if col in self.data.columns]
        
        if len(available_cols) < 2:
            print("Not enough numeric columns for correlation analysis")
            return None
        
        # Calculate correlation matrix
        corr_matrix = self.data[available_cols].corr()
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create heatmap
        sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0,
                   square=True, ax=ax, cbar_kws={'label': 'Correlation Coefficient'})
        
        ax.set_title('Correlation Matrix of Numeric Variables', 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return fig
    
    def create_comprehensive_dashboard_data(self):
        """
        Prepare data for interactive dashboard.
        
        Returns:
            dict: Dictionary containing processed data for dashboard
        """
        dashboard_data = {
            'summary_stats': {
                'total_incidents': len(self.data),
                'total_quantity': self.data['total_quantity_equivalent'].sum(),
                'avg_quantity': self.data['total_quantity_equivalent'].mean(),
                'top_town': self.data['town'].value_counts().index[0],
                'peak_hour': self.data['release_hour'].mode().iloc[0] if not self.data['release_hour'].mode().empty else 'N/A',
                'primary_cause': self.data['cause_category'].value_counts().index[0],
                'primary_substance': self.data['substance_category'].value_counts().index[0]
            },
            'town_data': self.data.groupby('town').agg({
                'case_number': 'count',
                'total_quantity_equivalent': 'sum'
            }).reset_index(),
            'time_data': self.data.groupby('release_hour').size().reset_index(name='count'),
            'cause_data': self.data['cause_category'].value_counts().reset_index(),
            'substance_data': self.data['substance_category'].value_counts().reset_index(),
            'monthly_trends': self.data.groupby([
                self.data['release_datetime'].dt.to_period('M')
            ]).size().reset_index(name='count')
        }
        
        return dashboard_data
    
    def save_all_figures(self, output_dir: str = 'reports/figures'):
        """
        Generate and save all research figures.
        
        Args:
            output_dir (str): Directory to save figures
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("Generating all research figures...")
        
        # Year-wise incidents analysis
        self.year_wise_incidents_by_cities(
            save_path=f'{output_dir}/year_wise_incidents_by_cities.png'
        )
        
        # Cities with highest spills analysis
        self.cities_highest_spills(
            save_path=f'{output_dir}/cities_highest_spills.png'
        )
        
        # Time of day analysis
        self.time_of_day_incidents(
            save_path=f'{output_dir}/time_of_day_incidents.png'
        )
        
        # Main causes analysis
        self.main_causes_analysis(
            save_path=f'{output_dir}/main_causes_analysis.png'
        )
        
        # Spill amount analysis
        self.spill_amount_per_incident(
            save_path=f'{output_dir}/spill_amount_per_incident.png'
        )
        
        # Common substances analysis
        self.common_substances_analysis(
            save_path=f'{output_dir}/common_substances_analysis.png'
        )
        
        # Additional analysis
        self.create_correlation_heatmap(
            save_path=f'{output_dir}/correlation_heatmap.png'
        )
        
        print(f"All figures saved to {output_dir}")


# Example usage
if __name__ == "__main__":
    # This would be used with actual processed data
    print("Visualization module loaded successfully!")
    print("Use with processed spill data: viz = SpillVisualization(cleaned_data)") 