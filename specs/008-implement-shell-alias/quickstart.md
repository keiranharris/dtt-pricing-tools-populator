# Quickstart: Shell Alias Auto-Setup Implementation

**Feature**: Shell Alias Auto-Setup for Easy Access  
**Implementation Time**: ~4-6 hours  
**Complexity**: Medium (file system operations, shell integration)

## Prerequisites

✅ **Environment**: macOS with zsh shell (development requirement)  
✅ **Python**: 3.11+ with existing project dependencies  
✅ **Codebase**: Clean feature branch `008-implement-shell-alias`  
✅ **Specifications**: Complete with clarifications and research  

## Implementation Order

### Phase 1: Core Module (60 minutes)

**File**: `src/shell_alias_manager.py`

```python
# 1. Create shell detection functions (15 min)
def detect_shell_environment() -> ShellEnvironment:
    # Use os.environ['SHELL'] + ps command validation
    
# 2. Create path resolution functions (15 min)  
def resolve_script_path() -> Path:
    # Use pathlib.Path(__file__).resolve() + validation
    
# 3. Create file manipulation functions (30 min)
def read_shell_config() -> str:
def write_shell_config() -> None:
def find_existing_alias() -> Optional[str]:
```

**Testing**: Unit tests with mocked file system operations

### Phase 2: Integration Hook (30 minutes)

**File**: `pricing_tool_accelerator.py` (minimal changes)

```python
# Add at top of main()
def main():
    try:
        if not setup_shell_alias_if_needed():
            return
    except Exception as e:
        logger.warning(f"Shell alias setup failed: {e}")
    
    # ... existing main() logic unchanged
```

**File**: `src/shell_alias_manager.py` (add integration function)

```python
def setup_shell_alias_if_needed() -> bool:
    """CLI integration hook - never raises exceptions"""
    try:
        manager = ShellAliasManager()
        result = manager.check_and_setup_alias()
        
        if result.success:
            logger.info(result.message)
        else:
            logger.error(result.message)
            if result.manual_instructions:
                logger.info(result.manual_instructions)
        return True
        
    except Exception as e:
        logger.error(f"Shell alias setup failed: {e}")
        return True  # Don't block main app
```

### Phase 3: Data Models (45 minutes)

**File**: `src/shell_alias_manager.py` (add to existing file)

```python
# 1. Create enums (10 min)
class AliasOperationType(Enum):
class ShellType(Enum):  
class OperationResult(Enum):

# 2. Create dataclasses (15 min)
@dataclass
class AliasOperationResult:
@dataclass  
class AliasValidationResult:
@dataclass
class ShellEnvironment:

# 3. Create exception classes (10 min)
class ShellAliasError(Exception):
class UnsupportedShellError(ShellAliasError):
class AliasPermissionError(ShellAliasError):

# 4. Create main manager class (10 min)
class ShellAliasManager:
    def __init__(self, ...):
    def check_and_setup_alias(self) -> AliasOperationResult:
```

### Phase 4: Core Logic Implementation (90 minutes)

**Focus**: Complete `ShellAliasManager.check_and_setup_alias()` method

```python
def check_and_setup_alias(self) -> AliasOperationResult:
    # 1. Shell detection and validation (20 min)
    shell_env = self._detect_and_validate_shell()
    if shell_env.shell_type != ShellType.ZSH:
        return AliasOperationResult(
            success=False,
            operation_type=AliasOperationType.SKIP,
            message=f"❌ zsh required. Current shell: {shell_env.shell_type.value}",
            manual_instructions=self.get_manual_setup_instructions()
        )
    
    # 2. Check existing alias (20 min)
    validation = self.validate_existing_alias()
    if validation.exists and validation.is_correct:
        return AliasOperationResult(
            success=True,
            operation_type=AliasOperationType.SKIP,
            message=""  # Silent for existing correct aliases
        )
    
    # 3. Create or update alias (30 min)
    operation_type = AliasOperationType.UPDATE if validation.exists else AliasOperationType.CREATE
    try:
        self._write_alias_to_config(shell_env.config_file)
        return AliasOperationResult(
            success=True,
            operation_type=operation_type,
            message="✅ Shell alias 'priceup' created successfully. Open new terminal to use."
        )
    except PermissionError:
        return AliasOperationResult(
            success=False,
            operation_type=operation_type,
            message="❌ Cannot write to ~/.zshrc. Manual setup required:",
            manual_instructions=self.get_manual_setup_instructions()
        )
    
    # 4. Add timeout wrapper (20 min)
    # Wrap entire method with signal.alarm() for 60-second timeout
```

### Phase 5: File Operations (60 minutes)

**Focus**: Safe ~/.zshrc manipulation with comment markers

```python
def _write_alias_to_config(self, config_path: Path) -> None:
    # 1. Read existing content (10 min)
    if config_path.exists():
        content = config_path.read_text()
    else:
        content = ""
    
    # 2. Remove existing alias block if present (20 min)
    start_marker = "# DTT Pricing Tool - START (auto-generated)"
    end_marker = "# DTT Pricing Tool - END"
    
    # Remove content between markers using regex
    import re
    pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
    content = re.sub(pattern, "", content, flags=re.DOTALL)
    
    # 3. Add new alias block (20 min)  
    alias_block = f"""
{start_marker}
alias {self.alias_name}='python3 {shlex.quote(str(self.script_path))}'
{end_marker}"""
    
    # 4. Atomic write with backup (10 min)
    backup_path = config_path.with_suffix('.bak')
    if config_path.exists():
        shutil.copy2(config_path, backup_path)
    
    try:
        config_path.write_text(content + alias_block)
        if backup_path.exists():
            backup_path.unlink()  # Remove backup on success
    except Exception:
        if backup_path.exists():
            shutil.move(backup_path, config_path)  # Restore on failure
        raise
```

### Phase 6: README Updates (45 minutes)

**File**: `README.md` (add new sections)

```markdown
# 1. Add git clone section for beginners (20 min)
## Getting Started

### For Git Beginners

Git is a tool for downloading and managing code projects. Don't worry - you only need these simple steps:

1. **Open Terminal** (found in Applications > Utilities on Mac)
2. **Navigate to your desired location**:
   ```bash
   cd ~/Desktop  # or wherever you want the tool
   ```
3. **Download the pricing tool**:
   ```bash
   git clone https://github.com/your-org/dtt-pricing-tools-populator.git
   ```
4. **Enter the downloaded folder**:
   ```bash
   cd dtt-pricing-tools-populator
   ```

# 2. Add first-time usage section (15 min)  
### First Time Setup

1. **Run the pricing tool once** (this creates the 'priceup' shortcut):
   ```bash
   python3 pricing_tool_accelerator.py
   ```
2. **Follow the setup prompts** - the tool will create a shortcut for you
3. **Open a new terminal** to activate the shortcut

### Everyday Usage  

After first-time setup, simply type from anywhere:
```bash
priceup
```

# 3. Add troubleshooting section (10 min)
### Troubleshooting

**Problem**: "zsh required" error message  
**Solution**: Switch your terminal to use zsh:
```bash
chsh -s /bin/zsh
```

**Problem**: Permission denied errors  
**Solution**: Manual alias setup:
```bash
echo "alias priceup='python3 $(pwd)/pricing_tool_accelerator.py'" >> ~/.zshrc
```
```

### Phase 7: Testing Suite (90 minutes)

**File**: `tests/test_shell_alias_manager.py`

```python
# 1. Unit tests with mocked file system (45 min)
def test_detect_shell_environment_zsh():
def test_detect_shell_environment_bash_fails():
def test_validate_existing_alias_not_found():
def test_validate_existing_alias_correct():
def test_validate_existing_alias_wrong_path():
def test_write_alias_creates_new_file():
def test_write_alias_updates_existing():
def test_write_alias_preserves_other_content():

# 2. Integration tests with temporary directories (45 min)
def test_full_workflow_clean_zshrc(tmp_path):
def test_full_workflow_existing_zshrc(tmp_path):
def test_permission_denied_handling(tmp_path):
def test_timeout_handling():
```

## Validation Checklist

### Functional Testing
- [ ] ✅ Fresh installation: Creates alias and shows success message
- [ ] ✅ Existing correct alias: Silent operation, no duplicate entries  
- [ ] ✅ Existing wrong alias: Updates to correct path
- [ ] ✅ Wrong shell: Clear error with instructions
- [ ] ✅ Permission denied: Error with manual fallback steps
- [ ] ✅ Repository move: Detects and updates alias path

### Integration Testing
- [ ] ✅ Main CLI continues normally after alias setup
- [ ] ✅ Alias works from any directory after creation
- [ ] ✅ Multiple terminal sessions can use alias
- [ ] ✅ README instructions allow non-technical users to succeed

### Performance Testing
- [ ] ✅ First-time setup completes within 30 seconds
- [ ] ✅ Subsequent runs complete within 5 seconds (alias already exists)
- [ ] ✅ File operations respect 60-second timeout

### Error Handling Testing
- [ ] ✅ No crashes on permission errors
- [ ] ✅ Clear error messages for all failure modes  
- [ ] ✅ Manual fallback instructions are accurate
- [ ] ✅ Main application continues if alias setup fails

## Deployment Readiness

### Code Review Points
1. **Constitution Compliance**: Atomic functions, Python best practices, automation focus
2. **Error Handling**: All edge cases covered with user-friendly messages
3. **Integration**: Minimal changes to existing codebase
4. **Testing**: Comprehensive unit and integration test coverage

### User Experience Validation
1. **Git Beginners**: Can successfully clone and set up using README
2. **Technical Users**: Transparent setup with clear confirmation messages
3. **Team Adoption**: Zero configuration required across different machines

### Production Considerations
1. **No External Dependencies**: Pure Python standard library only
2. **Cross-User Support**: Works regardless of repository location
3. **Idempotent Operations**: Safe to run multiple times
4. **Graceful Degradation**: Main functionality preserved if alias setup fails

**Estimated Total Implementation Time**: 4-6 hours
**Risk Level**: Low (well-defined requirements, standard library only)
**Team Impact**: High (significant user experience improvement)