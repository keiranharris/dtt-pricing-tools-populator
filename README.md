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

**What is Git?** Git is a tool for downloading and managing code projects. Think of it like downloading an app, but for developer tools. You only need a few simple commands to get the pricing tool working on your computer.

#### Step 1: Check if Git is Installed

1. **Open Terminal** (found in Applications > Utilities on Mac, or press Cmd+Space and search "Terminal")
2. **Check if git is available** by typing:
   ```bash
   git --version
   ```
   - If you see a version number (like `git version 2.39.0`), git is installed ✅
   - If you see `command not found`, you need to install git (see troubleshooting below)

#### Step 2: Download the Tool

1. **Navigate to your desired location** (choose where you want the tool):
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
ls -la pricing_tool_accelerator.py
```
If you see file details, you're ready for setup! If you see "No such file", something went wrong with the download.

#### Step 4: First-Time Setup

1. **Run the tool once** (this creates the easy 'priceup' shortcut):
   ```bash
   python3 pricing_tool_accelerator.py
   ```

2. **What to expect during first-time setup:**
   - ✅ **Shell alias setup**: You'll see a message like "Shell alias 'priceup' set up successfully!"
   - 📋 **Prompt for client details**: Enter client name, opportunity name, dates, and margin percentage
   - 📄 **File processing**: The tool will copy templates, populate data, and calculate rates
   - 📊 **Excel opens**: Your completed pricing tool will open automatically
   - 🔍 **Finder opens**: The output folder will open showing your new file

3. **Success indicators** - you'll see messages like:
   ```
   ✅ Shell alias 'priceup' set up successfully!
   ✅ Populated 63/63 matched fields from 18 constants
   🎉 All matched fields populated successfully!
   ✅ Successfully created: 20251026 - CLIENT - OPPORTUNITY - (LowCompV1.2).xlsb
   ```

4. **Activate the shortcut**:
   - **Option 1**: Open a new terminal window
   - **Option 2**: In the current terminal, run: `source ~/.zshrc`

5. **Test the shortcut**: In your new terminal, try typing:
   ```bash
   priceup
   ```
   If it works, you'll see the pricing tool start up! 🎉

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

### Alternative Download Methods

#### Method 1: Direct ZIP Download (No Git Required)

If git doesn't work or you prefer a simpler approach:

1. **Visit the repository webpage**: https://github.com/keiranharris/dtt-pricing-tools-populator
2. **Click the green "Code" button** → **"Download ZIP"**
3. **Save the ZIP file** to your desired location (Desktop, Documents, etc.)
4. **Extract the ZIP file** by double-clicking it
5. **Open Terminal** and navigate to the extracted folder:
   ```bash
   cd ~/Desktop/dtt-pricing-tools-populator-main  # Adjust path as needed
   ```
6. **Follow Step 4 above** for first-time setup

**Pros**: No git installation required, simple one-click download
**Cons**: Manual process for updates, no version history tracking

#### Method 2: Using Company File Share

If available through your organization:

1. **Access the shared network drive** where the tool is hosted
2. **Copy the entire folder** to your local machine
3. **Open Terminal** and navigate to the copied folder
4. **Follow Step 4 above** for first-time setup

#### Method 3: Request Access via IT

If other methods fail:

1. **Contact your IT support** and request:
   - Git installation on your Mac
   - Access to the pricing tool repository
   - Assistance with first-time setup
2. **Provide them this README** for reference
3. **Schedule a brief setup session** if needed

#### Updating Your Installation

- **Git users**: Run `git pull` in the tool directory
- **ZIP users**: Re-download and extract the latest ZIP file
- **File share users**: Re-copy from the shared location
- **After updating**: Re-run the setup to ensure aliases are current

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

### Shell and Environment Issues

**Problem**: "Only zsh is currently supported" error message  
**Solution**: Switch your terminal to use zsh (the default shell on modern Macs):
```bash
chsh -s /bin/zsh
```
Then **restart Terminal completely** and try again.

**Problem**: Permission denied when creating shell alias  
**Solution**: Try manual alias setup:
```bash
# Navigate to the tool directory first
cd /path/to/dtt-pricing-tools-populator
# Add the alias manually
echo "alias priceup='python3 $(pwd)/pricing_tool_accelerator.py'" >> ~/.zshrc
# Reload your shell configuration
source ~/.zshrc
```

**Problem**: 'priceup' command not found after setup  
**Solution**: 
1. **Open a new terminal window** (the alias only works in new terminals)
2. **Or reload your shell**: `source ~/.zshrc`
3. **Verify the alias exists**: `alias | grep priceup`
4. **Check your shell**: `echo $SHELL` (should show `/bin/zsh`)

### Git and Download Issues

**Problem**: "git: command not found"  
**Solution**: Install Apple's developer tools:
```bash
xcode-select --install
```
**Alternative**: Use the ZIP download method instead of git.

**Problem**: "Permission denied" during git clone  
**Solution**: 
1. **Check repository URL** is correct
2. **Ensure you have access** to the repository
3. **Try HTTPS instead of SSH**: Use `https://github.com/...` URLs
4. **Contact repository admin** for access permissions

**Problem**: "Repository not found" error  
**Solution**: 
1. **Verify the repository URL** is correct
2. **Check if you're on the company network** (VPN may be required)
3. **Try the ZIP download method** as an alternative

### Python and System Issues

**Problem**: "python3: command not found"  
**Solution**: Install Python 3:
```bash
# Check if Python 3 is available with different name
python --version
python3 --version
# If not available, install via Homebrew or python.org
```

**Problem**: "No module named 'xlwings'" or similar import errors  
**Solution**: Install required Python packages:
```bash
pip3 install xlwings openpyxl pandas
```

**Problem**: Excel doesn't open automatically  
**Solution**: 
1. **Check if Excel is installed** and can open .xlsb files
2. **Manually open the file** from the output directory
3. **Grant permissions** when prompted for Excel access

### File Access and OneDrive Issues

**Problem**: "File not found" for pricing templates  
**Solution**: 
1. **Verify OneDrive is syncing** (check OneDrive status in menu bar)
2. **Update paths in src/constants.py** if your OneDrive location differs
3. **Ensure you have access** to the shared OneDrive libraries
4. **Contact team admin** for OneDrive access permissions

**Problem**: Files saved to wrong location  
**Solution**: 
1. **Check OUTPUT_DIRECTORY** in `src/constants.py`
2. **Update the path** to match your OneDrive structure
3. **Create missing directories** if needed

**Problem**: "Permission denied" writing files  
**Solution**: 
1. **Check disk space** on your Mac
2. **Ensure OneDrive folders** are writable (not read-only)
3. **Restart OneDrive sync** if folders are locked
4. **Run with admin rights** if needed: `sudo python3 pricing_tool_accelerator.py`

### Advanced Troubleshooting

**Problem**: Tool runs but produces incorrect results  
**Solution**: 
1. **Check constants file** exists and is accessible
2. **Verify template version** matches expected format
3. **Run with verbose logging**: Edit `VERBOSE_LOGGING_ENABLED = True` in the script
4. **Review log output** for specific error details

**Problem**: Performance issues or timeouts  
**Solution**: 
1. **Close other Excel instances** before running
2. **Ensure sufficient disk space** (>1GB free)
3. **Check OneDrive sync status** (pause if needed during processing)
4. **Restart computer** if Excel processes are stuck

**Problem**: Need to reset everything  
**Solution**: Complete reset procedure:
```bash
# Remove the alias
sed -i '' '/# DTT Pricing Tool Alias/,/# DTT Pricing Tool Alias.*END/d' ~/.zshrc
# Reload shell
source ~/.zshrc  
# Re-run first-time setup
python3 pricing_tool_accelerator.py
```

### Getting Additional Help

1. **Check the error message carefully** - it often contains specific guidance
2. **Run the tool with verbose logging** enabled for detailed diagnostics
3. **Try the shell alias setup tool directly**: `python3 shell_alias_setup.py --debug`
4. **Contact your team's technical lead** with error details and screenshots
5. **Include your system information**:
   ```bash
   system_profiler SPSoftwareDataType | grep "System Version"
   echo $SHELL
   python3 --version
   git --version
   ```

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