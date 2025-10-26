# DTT Pricing Tool Accelerator

**Automated pricing tool spreadsheet setup and population system**

## Overview

The DTT Pricing Tool Accelerator automates the time-consuming process of setting up pricing spreadsheets by:

- 📄 Copying template Excel files with intelligent naming
- 📋 Populating data from CLI inputs and constants files  
- 👥 Setting up resource allocation tables
- 💰 Calculating rate cards with client margins
- 🔍 Opening completed files in Excel and Finder

**✨ After first-time setup, just type `priceup` from anywhere to use the tool!**

## Getting Started

### For Git Beginners (First-Time Setup)

**What is Git?** Git is a tool for downloading and managing code projects. Don't worry - you only need these simple steps to get the pricing tool on your computer.

#### Step 1: Download the Tool

1. **Open Terminal** (found in Applications > Utilities on Mac)
2. **Navigate to your desired location** (choose where you want the tool):
   ```bash
   cd ~/Desktop  # Downloads to your Desktop
   # OR
   cd ~/Documents  # Downloads to your Documents folder
   ```
3. **Download the pricing tool**:
   ```bash
   git clone https://github.com/your-org/dtt-pricing-tools-populator.git
   ```
4. **Enter the downloaded folder**:
   ```bash
   cd dtt-pricing-tools-populator
   ```

#### Step 2: First-Time Setup

1. **Run the tool once** (this creates the easy 'priceup' shortcut):
   ```bash
   python3 pricing_tool_accelerator.py
   ```

2. **Follow the setup prompts** - the tool will:
   - Create a convenient 'priceup' command for future use
   - Show you a success message when ready
   - Guide you through your first pricing tool creation

3. **Open a new terminal window** to activate the shortcut

### Everyday Usage (After First-Time Setup)

Once you've completed the first-time setup above, using the pricing tool is simple:

1. **Open Terminal** from anywhere on your computer
2. **Type the magic command:**
   ```bash
   priceup
   ```
3. **Follow the prompts:**
   - Enter client name and opportunity details
   - Specify project duration and margin
   - System handles the rest automatically

4. **Results:**
   - Completed pricing tool opens in Excel
   - File saved to OneDrive shared location
   - All team members have access

### Alternative Download (If Git Doesn't Work)

If you cannot use git or prefer not to:

1. **Download as ZIP**: Visit the repository webpage and click "Download ZIP"
2. **Extract the ZIP file** to your desired location
3. **Follow Step 2 above** for first-time setup
4. **Note**: You'll need to manually download updates instead of using git

## Features

- ✅ **Single Excel Session** - Reduces permission dialogs and improves performance
- ✅ **OneDrive Integration** - Team collaboration with shared directories  
- ✅ **Smart Field Matching** - Automatic population from constants files
- ✅ **Resource Setup** - Copies standard resource allocation tables
- ✅ **Rate Card Calculation** - Applies client margins to standard rates
- ✅ **Verbose Logging** - Detailed feedback for troubleshooting

## Directory Structure

```
dtt-pricing-tools-populator/
├── pricing_tool_accelerator.py    # Main application entry point
├── src/                          # Core application modules
│   ├── constants.py              # Centralized configuration
│   ├── cli_interface.py          # User interaction handling
│   ├── excel_data_populator.py   # Excel automation
│   ├── excel_session_manager.py  # Consolidated Excel operations  
│   └── ...                       # Additional modules
├── tests/                        # Test suite
├── debug/                        # Development and debugging tools
├── docs/                         # Documentation
└── specs/                        # Feature specifications
```

## Configuration

All directory paths are centralized in `src/constants.py`:

```python
# OneDrive shared library paths - update here for all users
CONSTANTS_DIRECTORY = '~/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(...)/00-CONSTANTS/'
PRICING_TOOL_SOURCE_DIRECTORY = '~/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(...)/10-LATEST-PRICING-TOOLS/'
OUTPUT_DIRECTORY = '~/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(...)/20-OUTPUT/'
```

## Troubleshooting

### Common Setup Issues

**Problem**: "zsh required" error message  
**Solution**: Switch your terminal to use zsh (the modern Mac shell):
```bash
chsh -s /bin/zsh
```
Then restart Terminal and try again.

**Problem**: Permission denied when creating shortcut  
**Solution**: Manual alias setup (copy and paste this command):
```bash
echo "alias priceup='python3 $(pwd)/pricing_tool_accelerator.py'" >> ~/.zshrc
```
Then restart Terminal.

**Problem**: "git: command not found"  
**Solution**: Either:
- Install git using: `xcode-select --install`
- OR use the "Alternative Download" method above

**Problem**: 'priceup' command not found after setup  
**Solution**: 
1. Make sure you opened a **new** terminal window after first-time setup
2. If still not working, try the manual setup command above

**Problem**: Tool runs but can't find pricing templates  
**Solution**: Make sure you have access to the OneDrive shared libraries and they are synced to your computer.

## System Requirements

- Python 3.11+
- Microsoft Excel (for .xlsb file processing)
- OneDrive sync enabled
- macOS with zsh shell (default on modern Macs)
- Terminal access

## Performance

- **Single Session Processing:** 95%+ performance improvement through consolidated Excel operations
- **Smart Verification:** 100% field population accuracy with intelligent type handling  
- **Batch Operations:** Reduced API calls from 200+ to 2 per worksheet scan

## Team Collaboration

The system uses OneDrive shared libraries to enable:
- Consistent template access across team members
- Centralized constants management  
- Shared output location for easy file sharing
- Cross-platform compatibility with `~` path expansion

---

*Built for DTT Cloud Network & Security Practice*