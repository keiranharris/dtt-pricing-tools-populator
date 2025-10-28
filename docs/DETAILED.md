# DTT Pricing Tool Accelerator - Detailed Documentation

This document provides comprehensive information for advanced use cases, troubleshooting, and alternative setup methods.

## Alternative Download Methods

### Method 1: Direct ZIP Download (No Git Required)

If git doesn't work or you prefer a simpler approach:

1. **Visit the repository webpage**: https://github.com/keiranharris/dtt-pricing-tools-populator
2. **Click the green "Code" button** → **"Download ZIP"**
3. **Save the ZIP file** to your desired location (Desktop, Documents, etc.)
4. **Extract the ZIP file** by double-clicking it
5. **Open Terminal** and navigate to the extracted folder:
   ```bash
   cd ~/Desktop/dtt-pricing-tools-populator-main  # Adjust path as needed
   ```
6. **Follow the first-time setup** from the main README

**Pros**: No git installation required, simple one-click download
**Cons**: Manual process for updates, no version history tracking

### Method 2: Using Company File Share

If available through your organization:

1. **Access the shared network drive** where the tool is hosted
2. **Copy the entire folder** to your local machine
3. **Open Terminal** and navigate to the copied folder
4. **Follow the first-time setup** from the main README

### Method 3: Request Access via IT

If other methods fail:

1. **Contact your IT support** and request:
   - Git installation on your Mac
   - Access to the pricing tool repository
   - Assistance with first-time setup
2. **Provide them the main README** for reference
3. **Schedule a brief setup session** if needed

### Updating Your Installation

- **Git users**: Run `git pull` in the tool directory
- **ZIP users**: Re-download and extract the latest ZIP file
- **File share users**: Re-copy from the shared location
- **After updating**: Re-run the setup to ensure aliases are current

## Configuration

### Dynamic Path Configuration

The tool now uses dynamic OneDrive path configuration. On first run, you'll be guided through a setup wizard that:

1. **Detects your OneDrive structure** automatically
2. **Prompts for your PricingToolAccel folder path** if needed
3. **Validates the configuration** to ensure all required directories exist
4. **Saves the configuration** for future use

### Configuration Commands

You can manage path configuration using command-line options:

```bash
# Show current configuration
python3 pricing_tool_accelerator.py --show-config

# Force reconfiguration (if paths change)
python3 pricing_tool_accelerator.py --configure-paths
```

### Manual Configuration File

The configuration is stored in `~/.dtt-pricing-tool-populator-config` as JSON:

```json
{
  "version": "1.0",
  "onedrive_base_path": "/Users/username/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(...)/AU CBO Practice - MO - Cloud Network & Security/_PRESALES/_PROPOSALS/_PricingToolAccel",
  "constants_directory": "00-CONSTANTS",
  "source_directory": "10-LATEST-PRICING-TOOLS", 
  "output_directory": "20-OUTPUT",
  "last_validated": "2024-10-28T15:30:00.000Z",
  "validation_status": "VALID"
}
```

You can manually edit this file if needed, though the setup wizard is recommended.

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
2. **Run the configuration wizard**: `python3 pricing_tool_accelerator.py --configure-paths`
3. **Ensure you have access** to the shared OneDrive libraries
4. **Contact team admin** for OneDrive access permissions

**Problem**: Files saved to wrong location  
**Solution**: 
1. **Reconfigure paths**: `python3 pricing_tool_accelerator.py --configure-paths`
2. **Check your OneDrive folder structure** matches expected layout
3. **Create missing directories** if needed

**Problem**: "Permission denied" writing files  
**Solution**: 
1. **Check disk space** on your Mac
2. **Ensure OneDrive folders** are writable (not read-only)
3. **Restart OneDrive sync** if folders are locked
4. **Run with admin rights** if needed: `sudo python3 pricing_tool_accelerator.py`

### OneDrive Path Configuration Issues

**Problem**: "OneDrive Configuration Error" or path validation failures  
**Solution**:
1. **Check OneDrive sync status** - ensure folders are fully synced
2. **Verify folder structure** - ensure you have access to the shared library
3. **Run reconfiguration**: `python3 pricing_tool_accelerator.py --configure-paths`
4. **Check folder permissions** - ensure you can read/write to the directories

**Problem**: "No valid configuration exists" error  
**Solution**:
1. **Delete the config file**: `rm ~/.dtt-pricing-tool-populator-config`
2. **Run the tool again** to start fresh configuration
3. **Ensure OneDrive is fully synced** before configuration

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
# Remove configuration
rm ~/.dtt-pricing-tool-populator-config
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

## Performance

### Single Session Processing
- **95%+ performance improvement** through consolidated Excel operations
- **Reduced API calls** from 200+ to 2 per worksheet scan
- **Minimized permission dialogs** by using single Excel session
- **Faster file processing** with temporary workspace approach

### Smart Verification
- **100% field population accuracy** with intelligent type handling  
- **Automatic data validation** ensures correct formatting
- **Comprehensive error reporting** for debugging issues

### Batch Operations
- **Consolidated Excel operations** reduce overhead
- **Optimized memory usage** for large spreadsheets
- **Background processing** minimizes user interruption

### Performance Tips

1. **Close other Excel instances** before running the tool
2. **Ensure adequate free disk space** (minimum 1GB recommended)
3. **Pause OneDrive sync temporarily** during processing if experiencing slowdowns
4. **Use SSD storage** for better file I/O performance
5. **Keep constants files in local OneDrive cache** for faster access

---

*For additional support, contact the DTT Cloud Network & Security Practice team.*