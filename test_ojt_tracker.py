"""
Test suite for the Modern OJT Tracker Application.
Run with: python -m pytest test_ojt_tracker.py -v
"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import the classes we want to test
# Note: You may need to adjust the import based on your file structure
try:
    from ojt_tracker_modern import (
        DataManager, 
        TimeTracker, 
        TimeEntry, 
        TimeTrackingState,
        UIConfig
    )
except ImportError:
    print("Could not import ojt_tracker_modern. Make sure the file exists.")
    exit(1)


class TestDataManager(unittest.TestCase):
    """Test cases for DataManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.data_manager = DataManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_initial_data_structure(self):
        """Test that initial data structure is correct."""
        expected_keys = {"total_hours", "entries", "current_session_start", "state"}
        self.assertEqual(set(self.data_manager.data.keys()), expected_keys)
        self.assertEqual(self.data_manager.data["total_hours"], 0.0)
        self.assertEqual(self.data_manager.data["entries"], [])
        self.assertIsNone(self.data_manager.data["current_session_start"])
        self.assertEqual(self.data_manager.data["state"], TimeTrackingState.CLOCKED_OUT.value)
    
    def test_save_and_load_data(self):
        """Test saving and loading data."""
        # Modify data
        self.data_manager.data["total_hours"] = 5.5
        self.data_manager.data["state"] = TimeTrackingState.CLOCKED_IN.value
        
        # Save data
        result = self.data_manager.save_data()
        self.assertTrue(result)
        
        # Create new manager with same file
        new_manager = DataManager(self.temp_file.name)
        
        # Verify data was loaded correctly
        self.assertEqual(new_manager.data["total_hours"], 5.5)
        self.assertEqual(new_manager.data["state"], TimeTrackingState.CLOCKED_IN.value)
    
    def test_add_entry(self):
        """Test adding time entries."""
        entry = TimeEntry(
            timestamp=datetime.now().isoformat(),
            action="TEST_ACTION",
            duration=1.5
        )
        
        initial_count = len(self.data_manager.data["entries"])
        self.data_manager.add_entry(entry)
        
        self.assertEqual(len(self.data_manager.data["entries"]), initial_count + 1)
        added_entry = self.data_manager.data["entries"][-1]
        self.assertEqual(added_entry["action"], "TEST_ACTION")
        self.assertEqual(added_entry["duration"], 1.5)
    
    def test_update_total_hours(self):
        """Test updating total hours."""
        self.data_manager.update_total_hours(10.5)
        self.assertEqual(self.data_manager.get_total_hours(), 10.5)
    
    def test_state_management(self):
        """Test state management methods."""
        # Test setting and getting state
        self.data_manager.set_current_state(TimeTrackingState.CLOCKED_IN)
        self.assertEqual(self.data_manager.get_current_state(), TimeTrackingState.CLOCKED_IN)
        
        # Test session time management
        test_time = datetime.now()
        self.data_manager.set_session_start(test_time)
        retrieved_time = self.data_manager.get_session_start()
        
        # Compare timestamps (allow small difference due to serialization)
        self.assertAlmostEqual(
            test_time.timestamp(), 
            retrieved_time.timestamp(), 
            places=0
        )


class TestTimeTracker(unittest.TestCase):
    """Test cases for TimeTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.data_manager = DataManager(self.temp_file.name)
        self.time_tracker = TimeTracker(self.data_manager)
    
    def tearDown(self):
        """Clean up test fixtures."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    @patch('ojt_tracker_modern.messagebox')
    def test_clock_in_success(self, mock_messagebox):
        """Test successful clock in."""
        result = self.time_tracker.clock_in()
        
        self.assertTrue(result)
        self.assertEqual(self.data_manager.get_current_state(), TimeTrackingState.CLOCKED_IN)
        self.assertIsNotNone(self.data_manager.get_session_start())
        mock_messagebox.showwarning.assert_not_called()
    
    @patch('ojt_tracker_modern.messagebox')
    def test_clock_in_already_clocked_in(self, mock_messagebox):
        """Test clock in when already clocked in."""
        # First clock in
        self.time_tracker.clock_in()
        
        # Try to clock in again
        result = self.time_tracker.clock_in()
        
        self.assertFalse(result)
        mock_messagebox.showwarning.assert_called_with("Already Clocked In", "You are already clocked in!")
    
    @patch('ojt_tracker_modern.messagebox')
    def test_clock_out_success(self, mock_messagebox):
        """Test successful clock out."""
        # First clock in
        self.time_tracker.clock_in()
        
        # Wait a small amount (simulate work time)
        import time
        time.sleep(0.1)
        
        # Clock out
        result = self.time_tracker.clock_out()
        
        self.assertTrue(result)
        self.assertEqual(self.data_manager.get_current_state(), TimeTrackingState.CLOCKED_OUT)
        self.assertIsNone(self.data_manager.get_session_start())
        self.assertGreater(self.data_manager.get_total_hours(), 0)
    
    @patch('ojt_tracker_modern.messagebox')
    def test_clock_out_not_clocked_in(self, mock_messagebox):
        """Test clock out when not clocked in."""
        result = self.time_tracker.clock_out()
        
        self.assertFalse(result)
        mock_messagebox.showwarning.assert_called_with("Not Clocked In", "You are not currently clocked in!")
    
    @patch('ojt_tracker_modern.messagebox')
    def test_add_manual_time_success(self, mock_messagebox):
        """Test adding manual time successfully."""
        initial_hours = self.data_manager.get_total_hours()
        
        result = self.time_tracker.add_manual_time(2, 30, 45)  # 2h 30m 45s
        
        self.assertTrue(result)
        expected_hours = 2 + (30/60) + (45/3600)
        self.assertAlmostEqual(
            self.data_manager.get_total_hours(),
            initial_hours + expected_hours,
            places=4
        )
    
    @patch('ojt_tracker_modern.messagebox')
    def test_add_manual_time_invalid_input(self, mock_messagebox):
        """Test adding manual time with invalid input."""
        # Test negative values
        result = self.time_tracker.add_manual_time(-1, 30, 45)
        self.assertFalse(result)
        
        # Test invalid minutes/seconds
        result = self.time_tracker.add_manual_time(1, 70, 45)
        self.assertFalse(result)
        
        result = self.time_tracker.add_manual_time(1, 30, 70)
        self.assertFalse(result)
        
        # Test zero time
        result = self.time_tracker.add_manual_time(0, 0, 0)
        self.assertFalse(result)
    
    @patch('ojt_tracker_modern.messagebox')
    def test_observer_notification(self, mock_messagebox):
        """Test that observers are notified of changes."""
        observer_called = False
        
        def test_observer():
            nonlocal observer_called
            observer_called = True
        
        self.time_tracker.add_observer(test_observer)
        self.time_tracker.clock_in()
        
        self.assertTrue(observer_called)


class TestUIConfig(unittest.TestCase):
    """Test cases for UIConfig class."""
    
    def test_default_values(self):
        """Test that UIConfig has expected default values."""
        config = UIConfig()
        
        self.assertEqual(config.window_width, 400)
        self.assertEqual(config.window_height, 400)
        self.assertEqual(config.corner_radius, 10)
        self.assertEqual(config.frame_color, "#242424")
        
        # Test color values
        self.assertEqual(config.clock_in_color, "#4CAF50")
        self.assertEqual(config.clock_out_color, "#f44336")
        self.assertEqual(config.break_color, "#FF9800")
        self.assertEqual(config.reset_color, "#9E9E9E")
        self.assertEqual(config.add_time_color, "#2196F3")


class TestTimeEntry(unittest.TestCase):
    """Test cases for TimeEntry dataclass."""
    
    def test_time_entry_creation(self):
        """Test creating TimeEntry objects."""
        timestamp = datetime.now().isoformat()
        entry = TimeEntry(timestamp=timestamp, action="TEST", duration=2.5)
        
        self.assertEqual(entry.timestamp, timestamp)
        self.assertEqual(entry.action, "TEST")
        self.assertEqual(entry.duration, 2.5)
    
    def test_time_entry_optional_duration(self):
        """Test TimeEntry with optional duration."""
        timestamp = datetime.now().isoformat()
        entry = TimeEntry(timestamp=timestamp, action="TEST")
        
        self.assertEqual(entry.timestamp, timestamp)
        self.assertEqual(entry.action, "TEST")
        self.assertIsNone(entry.duration)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)