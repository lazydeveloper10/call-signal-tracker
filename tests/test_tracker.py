"""
Unit tests for Call & Signal Tracker (call_signal_tracker.py)
"""

import unittest
import os
import pandas as pd
import call_signal_tracker as tracker

class TestCallSignalTracker(unittest.TestCase):
    
    def setUp(self):
        self.csv_path = 'data/call_data.csv'
        self.json_path = 'data/call_data.json'
        
    def test_load_csv_data(self):
        df = tracker.load_data(self.csv_path)
        self.assertFalse(df.empty)
        self.assertIn('rsrp', df.columns)
        self.assertIn('call_type', df.columns)
        
    def test_load_json_data(self):
        df = tracker.load_data(self.json_path)
        self.assertFalse(df.empty)
        self.assertIn('rsrp', df.columns)
        
    def test_classify_rsrp(self):
        self.assertEqual(tracker.classify_rsrp(-65), "Excellent")
        self.assertEqual(tracker.classify_rsrp(-80), "Good")
        self.assertEqual(tracker.classify_rsrp(-100), "Fair")
        self.assertEqual(tracker.classify_rsrp(-115), "Poor")
        self.assertEqual(tracker.classify_rsrp(-130), "Very Poor (Dead Zone)")
        self.assertEqual(tracker.classify_rsrp("invalid"), "Unknown")
        
    def test_normalize_columns(self):
        raw_df = pd.DataFrame({'Signal_Strength': [-85], 'Call_Type': ['INCOMING']})
        norm_df = tracker.normalize_columns(raw_df)
        self.assertIn('rsrp', norm_df.columns)
        self.assertIn('signal_strength', norm_df.columns)
        
    def test_export_report_csv_and_json(self):
        df = tracker.load_data(self.csv_path)
        csv_report = 'reports/test_unittest.csv'
        json_report = 'reports/test_unittest.json'
        
        tracker.export_report(df, csv_report)
        self.assertTrue(os.path.exists(csv_report))
        
        tracker.export_report(df, json_report)
        self.assertTrue(os.path.exists(json_report))
        
        # Cleanup
        if os.path.exists(csv_report):
            os.remove(csv_report)
        if os.path.exists(json_report):
            os.remove(json_report)

if __name__ == '__main__':
    unittest.main()
