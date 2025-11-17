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

## Version Information

Current version: **2025.11.18_1**

To check your version: `python3 priceup.py --version`

The tool automatically checks for updates and will notify you when newer versions are available.

## Getting Started

### For Git Beginners (First-Time Setup)

**What is Git?** Git is a tool for downloading and managing code projects. Think of it like downloading an app, but for developer tools. You only need a few simple commands to get the pricing tool working on your computer.

#### Step 1: Check if Git is Installed

1. **Open Terminal** (found in Applications > Utilities on Mac, or press Cmd+Space and search "Terminal")
2. **Check if git is available** by typing:
   ```bash
   git --version
   ```
   - If you see a version number (like `git version 2.39.0`), git is installed ✅
   - If you see `command not found`, you need to install git ([see detailed guide](./docs/DETAILED.md#git-and-download-issues))

#### Step 2: Download the Tool

1. **Navigate to your desired location** (choose where you want the tool), for example:
   ```bash
   cd ~/Desktop  # Downloads to your Desktop
   # OR
   cd ~/Documents  # Downloads to your Documents folder  
   # OR
   cd ~/Downloads  # Downloads to your Downloads folder
   ```

2. **Download the pricing tool**:
   ```bash
   git clone https://github.com/keiranharris/dtt-pricing-tools-populator.git
   ```
   *You'll see messages like "Cloning into..." - this is normal and means it's working*

3. **Enter the downloaded folder**:
   ```bash
   cd dtt-pricing-tools-populator
   ```

#### Step 3: Verify the Download

Check that the tool downloaded correctly:
```bash
ls -la priceup.py
```
If you see file details, you're ready for setup! If you see "No such file", something went wrong with the download.

#### Step 4: First-Time Run/Setup

1. **Run the tool once** (this creates the easy 'priceup' shortcut):
   ```bash
   python3 priceup.py
   ```

2. **What to expect during first-time setup:**
   - 🔧 **OneDrive Path Configuration**: On first run, you'll be guided through setting up your OneDrive folder paths
   - ✅ **Shell alias setup**: You'll see a message like "Shell alias 'priceup' set up successfully!"
   - Then the program will run as normal
      - 📋 **Prompt for client details**: Enter client name, opportunity name, dates, and margin percentage
      - 📄 **File processing**: The tool will copy templates, populate data, and calculate rates
      - 📊 **Excel opens**: Your completed pricing tool will open automatically
      - 🔍 **Finder opens**: The output folder will open showing your new file

### Everyday Usage (After First-Time Setup)

Once you've completed the first-time setup above, using the pricing tool is simple:

1. **Open Terminal** from anywhere on your computer
2. **Type the magic command** (note this requires you to have restarted your teminal at least once to kick in the alias):
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

## Features

- ✅ **Dynamic Path Configuration** - Automatic OneDrive path detection and setup on first run
- ✅ **Single Excel Session** - Reduces permission dialogs and improves performance
- ✅ **OneDrive Integration** - Team collaboration with shared directories  
- ✅ **Smart Field Matching** - Automatic population from constants files
- ✅ **Resource Setup** - Copies standard resource allocation tables
- ✅ **Rate Card Calculation** - Applies client margins to standard rates
- ✅ **Streamlined Input** - Compact, single-line prompts for quick data entry

## Directory Structure

```
dtt-pricing-tools-populator/
├── priceup.py    # Main application entry point
├── src/                          # Core application modules
│   ├── constants.py              # Dynamic path configuration
│   ├── path_configuration.py     # OneDrive path management
│   ├── cli_interface.py          # User interaction handling
│   ├── excel_data_populator.py   # Excel automation
│   ├── excel_session_manager.py  # Consolidated Excel operations  
│   └── ...                       # Additional modules
├── tests/                        # Test suite
├── debug/                        # Development and debugging tools
├── docs/                         # Documentation
└── specs/                        # Feature specifications
```

## System Requirements

- Python 3.11+
- Microsoft Excel (for .xlsb file processing)
- OneDrive sync enabled
- macOS with zsh shell (default on modern Macs)
- Terminal access

## Team Collaboration

The system uses OneDrive shared libraries to enable:
- Consistent template access across team members
- Centralized constants management  
- Shared output location for easy file sharing
- Cross-platform compatibility with automatic path configuration

---

**Need more help?** See the [detailed documentation](./docs/DETAILED.md) for alternative download methods, troubleshooting, performance tips, and advanced configuration options.

