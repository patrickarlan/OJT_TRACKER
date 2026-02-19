# Modern OJT Tracker

A modernized On-the-Job Training tracker application built with Python and CustomTkinter, featuring proper architecture, data persistence, and comprehensive time tracking capabilities.

## 🚀 Key Improvements from Original

### **Architecture & Code Quality**
- **Object-Oriented Design**: Proper separation of concerns with dedicated classes
- **Type Hints**: Full type annotation support for better IDE integration and error catching
- **Error Handling**: Comprehensive exception handling throughout the application
- **Logging**: Proper logging system for debugging and monitoring
- **Documentation**: Complete docstrings and inline comments

### **Functionality**
- **Real Time Tracking**: Actually tracks time (not just display hardcoded values)
- **Data Persistence**: Saves data to JSON file, survives app restarts
- **State Management**: Proper tracking of clock in/out/break states
- **Manual Time Entry**: Add time manually with validation
- **Smart Button States**: Buttons enable/disable based on current state
- **Session Management**: Track individual sessions with timestamps

### **Modern Python Practices**
- **Dataclasses**: Clean data structures with `@dataclass`
- **Enums**: Type-safe state management with `Enum`
- **Path Handling**: Modern `pathlib.Path` instead of string manipulation
- **Configuration**: Externalized config in JSON file
- **Testing**: Comprehensive unit test suite included
- **Dependencies**: Proper `requirements.txt` for dependency management

## 📋 Features

- ⏰ **Real-time Clock In/Out** - Track actual work hours
- ☕ **Break Management** - Pause and resume time tracking
- 📊 **Progress Visualization** - Radial progress bar for goal tracking
- 💾 **Data Persistence** - All data saved automatically
- 🔄 **Session Recovery** - Recover from unexpected shutdowns
- ➕ **Manual Time Entry** - Add time manually with validation
- 🎯 **Goal Tracking** - Default 300-hour OJT target
- 📈 **Time History** - Complete log of all time entries
- 🛡️ **Input Validation** - Prevent invalid data entry
- 🖥️ **Modern UI** - Clean, dark theme interface

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python ojt_tracker_modern.py
```

### 3. Run Tests (Optional)
```bash
# Install pytest if not already installed
pip install pytest

# Run tests
python -m pytest test_ojt_tracker.py -v
```

## 📂 Project Structure

```
OJT_TRACKER/
│
├── ojt_tracker_modern.py      # Main modernized application
├── ojt_tracker2.py           # Original version
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
├── test_ojt_tracker.py       # Unit tests
├── ojt_data.json            # Data file (auto-created)
├── ojt_tracker.log          # Log file (auto-created)
└── README.md                # This file
```

## 🎮 How to Use

### Basic Workflow
1. **Clock In** - Start tracking your work time
2. **Take Breaks** - Pause tracking when on break
3. **Clock Out** - Stop tracking and save session duration
4. **Add Manual Time** - Add additional hours if needed
5. **Monitor Progress** - Watch your progress toward the 300-hour goal

### Button States
- **Green Clock In**: Available when not tracking
- **Red Clock Out**: Available when clocked in or on break
- **Orange Break/End Break**: Toggle break state when clocked in
- **Gray Reset**: Clear all tracked time (with confirmation)
- **Blue Add Time**: Add manual time using the time entry fields

### Data Safety
- All data is automatically saved to `ojt_data.json`
- Application recovers session state on restart
- Reset function requires confirmation to prevent accidental data loss

## ⚙️ Configuration

Edit `config.json` to customize:
- Window dimensions and colors
- Target hours goal
- Logging preferences
- UI appearance settings

## 🧪 Testing

The application includes comprehensive unit tests covering:
- Data management and persistence
- Time tracking logic
- State transitions
- Input validation
- Error handling

Run tests with:
```bash
python -m pytest test_ojt_tracker.py -v
```

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**Data not saving**
- Check file permissions in the application directory
- View logs in `ojt_tracker.log` for error details

**UI elements not displaying correctly**
- Update CustomTkinter: `pip install --upgrade customtkinter`
- Check system compatibility with CustomTkinter

### Logging
Application logs are saved to `ojt_tracker.log` with helpful error messages and debugging information.

## 🔄 Migration from Original

To migrate from the original `ojt_tracker2.py`:
1. Your existing `ojt_data.txt` won't be imported automatically
2. Start fresh with the new application
3. Manually add any existing hours using the "Add Time" feature
4. The new system provides much better tracking going forward

## 🚀 Future Enhancements

Potential improvements for future versions:
- Export data to CSV/Excel
- Weekly/monthly reports
- Multiple project tracking
- Time tracking analytics and charts
- Break reminders and productivity tips
- Cloud synchronization
- Mobile companion app

## 📝 License

This project is for educational purposes as part of OJT requirements.

---

**Note**: This modern version maintains the same visual appearance as the original while adding robust functionality, proper architecture, and modern Python practices. The goal is to provide a professional-grade application suitable for actual time tracking needs.