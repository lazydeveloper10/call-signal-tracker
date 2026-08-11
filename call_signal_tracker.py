"""
* CALL & SIGNAL TRACKER (Python) *
Author: h4cker_fawad
Version: 1.2
Description: Analyze your own call logs & mobile network signals.
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

# Project folders
DATA_DIR = 'data'
REPORTS_DIR = 'reports'
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Supported data file
DATA_FILE = os.path.join(DATA_DIR, 'call_data.csv')

# Program info
APP_NAME = "CALL & SIGNAL TRACKER"
APP_VERSION = "1.2"
AUTHOR = "h4cker_fawad"
DESCRIPTION = "Analyze your own call logs & mobile network signals."

def clear_screen():
    """Clear terminal screen depending on OS."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Display the main interactive menu."""
    clear_screen()
    print("=" * 60)
    print(f"   {APP_NAME} v{APP_VERSION}   ")
    print("=" * 60)
    print("1. Import Data (CSV / JSON)")
    print("2. View Call Logs")
    print("3. View All / Search Records")
    print("4. Analyze Signal Strength & Network Data")
    print("5. Export Report (CSV / JSON)")
    print("6. Exit")
    print("-" * 60)

def classify_rsrp(rsrp_val):
    """
    Classify RSRP signal strength (dBm) according to cellular standards:
    >= -70 dBm    : Excellent
    -70 to -90    : Good
    -90 to -110   : Fair
    -110 to -120  : Poor
    <= -120 dBm   : Very Poor (Dead Zone)
    """
    try:
        val = float(rsrp_val)
        if val >= -70:
            return "Excellent"
        elif val >= -90:
            return "Good"
        elif val >= -110:
            return "Fair"
        elif val >= -120:
            return "Poor"
        else:
            return "Very Poor (Dead Zone)"
    except (ValueError, TypeError):
        return "Unknown"

def normalize_columns(df):
    """
    Standardize column names so both 'signal_strength' and 'rsrp' work seamlessly.
    Strips spaces and converts headers to lower-case.
    """
    if df.empty:
        return df
    
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # Alias 'signal_strength' and 'rsrp'
    if 'signal_strength' in df.columns and 'rsrp' not in df.columns:
        df['rsrp'] = df['signal_strength']
    elif 'rsrp' in df.columns and 'signal_strength' not in df.columns:
        df['signal_strength'] = df['rsrp']
        
    return df

# --------- 2. IMPORT DATA (CSV / JSON) ---------
def load_data(file_path):
    """Load dataset from a CSV or JSON file into a pandas DataFrame."""
    file_path = file_path.strip().strip("'").strip('"')
    if not os.path.exists(file_path):
        print(f"[!] File not found: {file_path}")
        return pd.DataFrame()
    
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext == '.json':
            df = pd.read_json(file_path)
        else:
            print("[!] Unsupported file format. Please use CSV or JSON.")
            return pd.DataFrame()
    except Exception as e:
        print(f"[!] Error loading file: {e}")
        return pd.DataFrame()
    
    if df.empty:
        print("[!] No data found in the file.")
        return pd.DataFrame()
    
    df = normalize_columns(df)
    print(f"[+] Data loaded successfully. Total records: {len(df)}")
    return df

def import_data():
    """Prompt user to choose format and enter path to import data."""
    print("\n[1] Import CSV file")
    print("[2] Import JSON file")
    choice = input("Select option (1-2): ").strip()
    file_path = input("Enter file path: ").strip().strip("'").strip('"')
    
    if choice == '1' and not file_path.lower().endswith('.csv'):
        print("[!] Please select a CSV file.")
        return pd.DataFrame()
    if choice == '2' and not file_path.lower().endswith('.json'):
        print("[!] Please select a JSON file.")
        return pd.DataFrame()
        
    return load_data(file_path)

def print_df_formatted(df):
    """Utility to print DataFrames nicely with tabulate if installed."""
    if df.empty:
        print("[!] No records to display.")
        return
    if HAS_TABULATE:
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    else:
        with pd.option_context('display.max_rows', None, 'display.width', None):
            print(df.reset_index(drop=True))

# --------- 3. VIEW & SEARCH RECORDS ---------
def view_all_records(df):
    """Display all loaded records sorted by timestamp."""
    if df.empty:
        print("[!] No records to display.")
        return
    
    if 'timestamp' in df.columns:
        sorted_df = df.sort_values('timestamp', ascending=False).reset_index(drop=True)
    else:
        sorted_df = df.reset_index(drop=True)
        
    print_df_formatted(sorted_df)

def view_call_logs(df):
    """Filter and view only INCOMING, OUTGOING, and MISSED call records."""
    if df.empty:
        print("[!] No data available.")
        return
    if 'call_type' not in df.columns:
        print("[!] 'call_type' column not found in dataset.")
        return
        
    calls = df[df['call_type'].astype(str).str.upper().isin(['INCOMING', 'OUTGOING', 'MISSED'])]
    if calls.empty:
        print("[!] No call logs found.")
        return
        
    if 'timestamp' in calls.columns:
        sorted_calls = calls.sort_values('timestamp', ascending=False).reset_index(drop=True)
    else:
        sorted_calls = calls.reset_index(drop=True)
        
    print_df_formatted(sorted_calls)

def search_by_number(df):
    """Search records by matching phone number substring."""
    if df.empty:
        print("[!] No data available.")
        return
    if 'phone_number' not in df.columns:
        print("[!] 'phone_number' column not found in dataset.")
        return
        
    number = input("\nEnter phone number to search: ").strip()
    if not number:
        print("[!] Empty search query.")
        return
        
    res = df[df['phone_number'].astype(str).str.contains(number, na=False)]
    if res.empty:
        print(f"[!] No records found for {number}")
    else:
        if 'timestamp' in res.columns:
            sorted_res = res.sort_values('timestamp', ascending=False).reset_index(drop=True)
        else:
            sorted_res = res.reset_index(drop=True)
        print_df_formatted(sorted_res)

def filter_by_date(df):
    """Filter records within a specified timestamp range."""
    if df.empty:
        print("[!] No data available.")
        return
    if 'timestamp' not in df.columns:
        print("[!] 'timestamp' column not found in dataset.")
        return
        
    start = input("Start date (YYYY-MM-DD HH:MM:SS): ").strip()
    end = input("End date (YYYY-MM-DD HH:MM:SS): ").strip()
    try:
        res = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
        if res.empty:
            print("[!] No records found in this range.")
        else:
            sorted_res = res.sort_values('timestamp', ascending=False).reset_index(drop=True)
            print_df_formatted(sorted_res)
    except Exception as e:
        print(f"[!] Invalid date format or error: {e}")

# --------- 4. ANALYZE SIGNAL STRENGTH & NETWORK DATA ---------
def analyze_signal_strength(df):
    """Perform analysis on signal strength (RSRP) with ratings and dead zone counts."""
    if df.empty:
        print("[!] No data available to analyze.")
        return
    if 'rsrp' not in df.columns:
        print("[!] 'rsrp' / 'signal_strength' column not found in dataset.")
        return
    
    valid_df = df.copy()
    valid_df['rsrp'] = pd.to_numeric(valid_df['rsrp'], errors='coerce')
    valid_df = valid_df.dropna(subset=['rsrp'])
    
    if valid_df.empty:
        print("[!] No valid RSRP values found.")
        return
    
    max_idx = valid_df['rsrp'].idxmax()
    min_idx = valid_df['rsrp'].idxmin()
    max_row = valid_df.loc[max_idx]
    min_row = valid_df.loc[min_idx]
    avg_rsrp = valid_df['rsrp'].mean()
    
    cell_col = 'cell_id' if 'cell_id' in valid_df.columns else valid_df.columns[0]
    
    dead_zones = valid_df[valid_df['rsrp'] <= -110]
    
    print("\n========== SIGNAL STRENGTH ANALYSIS ==========")
    print(f"Total records analyzed : {len(valid_df)}")
    print(f"Average RSRP           : {avg_rsrp:.2f} dBm ({classify_rsrp(avg_rsrp)})")
    print(f"Strongest Signal       : {max_row['rsrp']} dBm ({classify_rsrp(max_row['rsrp'])})")
    print(f"  Cell ID              : {max_row.get(cell_col, 'N/A')}")
    print(f"Weakest Signal         : {min_row['rsrp']} dBm ({classify_rsrp(min_row['rsrp'])})")
    print(f"  Cell ID              : {min_row.get(cell_col, 'N/A')}")
    print(f"Poor/Dead Zone Records : {len(dead_zones)} (RSRP <= -110 dBm)")
    print("==============================================")
    return valid_df

def plot_signal_distribution(df):
    """Render a visual ASCII horizontal bar chart of signal quality distribution."""
    if df.empty or 'rsrp' not in df.columns:
        return
        
    valid_df = df.copy()
    valid_df['rsrp'] = pd.to_numeric(valid_df['rsrp'], errors='coerce')
    valid_df = valid_df.dropna(subset=['rsrp'])
    
    if valid_df.empty:
        return
        
    categories = {
        "Excellent (>= -70 dBm)": 0,
        "Good (-70 to -90 dBm)": 0,
        "Fair (-90 to -110 dBm)": 0,
        "Poor (-110 to -120 dBm)": 0,
        "Very Poor (<= -120 dBm)": 0
    }
    
    for val in valid_df['rsrp']:
        if val >= -70:
            categories["Excellent (>= -70 dBm)"] += 1
        elif val >= -90:
            categories["Good (-70 to -90 dBm)"] += 1
        elif val >= -110:
            categories["Fair (-90 to -110 dBm)"] += 1
        elif val >= -120:
            categories["Poor (-110 to -120 dBm)"] += 1
        else:
            categories["Very Poor (<= -120 dBm)"] += 1
            
    total = len(valid_df)
    print("\n========== SIGNAL DISTRIBUTION CHART ==========")
    for cat, count in categories.items():
        pct = (count / total) * 100 if total > 0 else 0
        bar_len = int(pct / 5)  # 20 blocks max
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"{cat:<25} [{bar}] {pct:>5.1f}% ({count})")
    print("===============================================")

def analyze_network_types(df):
    """Display count distribution of network radio types."""
    if df.empty:
        print("[!] No data available to analyze.")
        return
    if 'radio_type' not in df.columns:
        print("[!] 'radio_type' column not found in dataset.")
        return
        
    dist = df['radio_type'].value_counts(dropna=False)
    print("\n========== NETWORK TYPE DISTRIBUTION ==========")
    for net_type, count in dist.items():
        print(f"{str(net_type):<15} : {count}")
    print("===============================================")
    return dist

def top_cells_by_signal(df, top_n=5):
    """List top N cell IDs by average signal strength with ratings."""
    if df.empty:
        print("[!] No data available to analyze.")
        return
    if 'rsrp' not in df.columns or 'cell_id' not in df.columns:
        print("[!] 'rsrp' or 'cell_id' column missing in dataset.")
        return
    
    valid_df = df.copy()
    valid_df['rsrp'] = pd.to_numeric(valid_df['rsrp'], errors='coerce')
    valid_df = valid_df.dropna(subset=['rsrp'])
    
    top_cells = (valid_df
                 .groupby('cell_id')['rsrp'].mean()
                 .sort_values(ascending=False)
                 .head(top_n))
    
    print(f"\n========== TOP {top_n} CELLS (by Avg RSRP) ==========")
    for cell_id, avg in top_cells.items():
        rating = classify_rsrp(avg)
        print(f"Cell ID: {cell_id:<20} Avg RSRP: {avg:.2f} dBm ({rating})")
    print("===================================================")
    return top_cells

def identify_dead_zones(df, threshold=-110):
    """Identify and display records with poor signal strength (<= threshold dBm)."""
    if df.empty:
        print("[!] No data available.")
        return
    if 'rsrp' not in df.columns:
        print("[!] 'rsrp' / 'signal_strength' column missing.")
        return
        
    valid_df = df.copy()
    valid_df['rsrp'] = pd.to_numeric(valid_df['rsrp'], errors='coerce')
    dead_zones = valid_df[valid_df['rsrp'] <= threshold]
    
    if dead_zones.empty:
        print(f"[+] Good news! No records found with signal <= {threshold} dBm.")
    else:
        print(f"\n[!] WARNING: Found {len(dead_zones)} poor/dead zone records (<= {threshold} dBm):")
        print_df_formatted(dead_zones)

# --------- 5. EXPORT REPORT & MAIN PROGRAM LOOP ---------
def export_report(df, filename='report.csv'):
    """Export dataset to a CSV or JSON file in the reports directory."""
    if df.empty:
        print("[!] No data to export.")
        return
    try:
        if not os.path.isabs(filename) and not filename.startswith(REPORTS_DIR):
            filename = os.path.join(REPORTS_DIR, filename)
        
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.json':
            df.to_json(filename, orient='records', indent=2)
        else:
            df.to_csv(filename, index=False)
            
        print(f"[+] Report exported successfully: {filename}")
    except Exception as e:
        print(f"[!] Error exporting report: {e}")

def show_summary(df):
    """Display overall summary statistics with signal ratings."""
    if df.empty:
        print("[!] No data available.")
        return
    if 'rsrp' not in df.columns:
        print("[!] 'rsrp' / 'signal_strength' column missing.")
        return
        
    valid_df = df.copy()
    valid_df['rsrp'] = pd.to_numeric(valid_df['rsrp'], errors='coerce')
    valid_df = valid_df.dropna(subset=['rsrp'])
    
    if valid_df.empty:
        print("[!] No valid signal strength values.")
        return

    total = len(df)
    avg_rsrp = valid_df['rsrp'].mean()
    strongest = valid_df['rsrp'].max()
    weakest = valid_df['rsrp'].min()
    
    cell_col = 'cell_id' if 'cell_id' in valid_df.columns else valid_df.columns[0]
    strongest_cell = valid_df.loc[valid_df['rsrp'].idxmax(), cell_col]
    weakest_cell = valid_df.loc[valid_df['rsrp'].idxmin(), cell_col]
    
    print("\n========== DATA SUMMARY ==========")
    print(f"Total Records          : {total}")
    print(f"Average RSRP           : {avg_rsrp:.2f} dBm ({classify_rsrp(avg_rsrp)})")
    print(f"Strongest Signal       : {strongest} dBm ({classify_rsrp(strongest)}) [Cell ID: {strongest_cell}]")
    print(f"Weakest Signal         : {weakest} dBm ({classify_rsrp(weakest)}) [Cell ID: {weakest_cell}]")
    print("==================================\n")

def pause():
    """Prompt user to press Enter to prevent menu screen clear from hiding output immediately."""
    input("\nPress Enter to return to main menu...")

def main():
    """Main program execution loop with CLI argument support."""
    parser = argparse.ArgumentParser(description="Call & Signal Tracker CLI Utility")
    parser.add_argument("-f", "--file", help="Path to input CSV or JSON call data file")
    parser.add_argument("-a", "--analyze", action="store_true", help="Run full signal analysis non-interactively")
    parser.add_argument("-e", "--export", help="Export output report to specified filename (CSV or JSON)")
    
    args, unknown = parser.parse_known_args()
    
    df = pd.DataFrame()
    
    # Check CLI non-interactive mode
    if args.file:
        df = load_data(args.file)
        if args.analyze:
            analyze_signal_strength(df)
            analyze_network_types(df)
            top_cells_by_signal(df)
            plot_signal_distribution(df)
            show_summary(df)
        if args.export:
            export_report(df, args.export)
        if args.analyze or args.export:
            return

    # Auto-load default dataset if present
    default_csv = os.path.join(DATA_DIR, 'call_data.csv')
    if df.empty and os.path.exists(default_csv):
        print(f"[+] Auto-loading default dataset from {default_csv}...")
        df = load_data(default_csv)
    
    while True:
        show_menu()
        if not df.empty:
            print(f"Active dataset: {len(df)} records loaded.")
        else:
            print("Active dataset: None (Please import CSV/JSON data)")
        print("-" * 60)
        
        choice = input("Select an option (1-6): ").strip()
        if choice == '1':
            df = import_data()
            pause()
        elif choice == '2':
            view_call_logs(df)
            pause()
        elif choice == '3':
            print("\nSub-menu:")
            print("  1. View All Records")
            print("  2. Search by Phone Number")
            print("  3. Filter by Date Range")
            sub_choice = input("Select option (1-3): ").strip()
            if sub_choice == '1':
                view_all_records(df)
            elif sub_choice == '2':
                search_by_number(df)
            elif sub_choice == '3':
                filter_by_date(df)
            else:
                view_all_records(df)
            pause()
        elif choice == '4':
            print("\nSignal & Network Analysis Sub-menu:")
            print("  1. Full Analysis Report & Chart")
            print("  2. Identify Coverage Dead Zones (<= -110 dBm)")
            print("  3. Top Cell Towers")
            print("  4. Signal Distribution Chart")
            sub_choice = input("Select option (1-4): ").strip()
            if sub_choice == '2':
                identify_dead_zones(df)
            elif sub_choice == '3':
                top_cells_by_signal(df)
            elif sub_choice == '4':
                plot_signal_distribution(df)
            else:
                analyze_signal_strength(df)
                analyze_network_types(df)
                top_cells_by_signal(df)
                plot_signal_distribution(df)
                show_summary(df)
            pause()
        elif choice == '5':
            filename = input("Enter report filename (e.g. report.csv or report.json): ").strip()
            if not filename:
                filename = 'report.csv'
            export_report(df, filename)
            pause()
        elif choice == '6':
            print("[+] Exiting... Stay safe!")
            break
        else:
            print("[!] Invalid option. Please choose 1-6.")
            pause()

if __name__ == "__main__":
    main()
