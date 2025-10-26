# Feature Specification: Shell Alias Auto-Setup for Easy Access

**Feature Branch**: `008-implement-shell-alias`  
**Created**: 2025-10-26  
**Status**: Draft  
**Input**: User description: "can we do one more change - i want to create an wrapper useage helper that ultimately creates an alias in a users ~/.zshrc file called 'priceup'. this creation logic should only be run the first time the main pricing_tool_accelerator.py is run (e.g. once the alias exists, there is no need to create it new each time). this should assume a user has just git cloned the repo into their desired location. e.g. for me - my code directory is: /Users/keharris/_K/_CODE/DEV/ so when i git clone i will get a new dtt-pricing-tools-populator directory there... and therefore my alias should be: alias priceup='python3 /Users/keharris/_K/_CODE/DEV/dtt-pricing-tools-populator/pricing_tool_accelerator.py' (but noting thats just me - your code should be able to handle wherever that user first downloads the repo to). please ensure the README.md includes usage instructions... both first time (the harder one).... and then subsequent times (the easier path)"

## Clarifications

### Session 2025-10-26

- Q: What level of user feedback should be provided during alias creation setup? → A: Informational messages only during setup (success/failure notifications)
- Q: How should the system handle different shell environments (zsh, bash, fish, etc.)? → A: Hard requirement for zsh only - fail if not detected
- Q: How should the alias entry be formatted and managed within ~/.zshrc? → A: Add file markers (comments) around alias entry for safe identification and removal
- Q: What timeout should be applied to alias creation operations? → A: 60 seconds - reasonable time for file operations and path resolution
- Q: How should the system handle permission errors when writing to ~/.zshrc? → A: Show clear error with fallback instructions for manual alias creation

## User Scenarios & Testing

### User Story 1 - First-Time Setup with Automatic Alias Creation (Priority: P1)

A developer clones the DTT Pricing Tool repository to their local machine and runs the application for the first time. The system automatically detects this is the initial run and creates a convenient shell alias called 'priceup' that points to the application, regardless of where they cloned the repository.

**Why this priority**: Core value proposition - transforms a complex path-based invocation into a simple, memorable command that works from anywhere in the terminal.

**Independent Test**: Can be fully tested by cloning the repo to any directory, running the application once, and verifying the 'priceup' alias works from any location.

**Acceptance Scenarios**:

1. **Given** a user has cloned the repository to any directory and no 'priceup' alias exists in ~/.zshrc, **When** they run the pricing tool for the first time, **Then** the system automatically adds the correct alias to ~/.zshrc and notifies the user of the setup
2. **Given** the alias has been created, **When** the user opens a new terminal session, **Then** they can type 'priceup' from any directory and launch the pricing tool
3. **Given** the user runs the application from a different working directory, **When** they invoke 'priceup', **Then** the application runs correctly with the same functionality

---

### User Story 2 - Subsequent Usage with Existing Alias (Priority: P1)

A user who has already set up the alias wants to use the pricing tool. They simply type 'priceup' from anywhere in their terminal and the application launches without any setup overhead or path concerns.

**Why this priority**: Primary user experience - once set up, this becomes the standard way users access the tool.

**Independent Test**: Can be tested by ensuring an existing alias works correctly and doesn't trigger setup logic on subsequent runs.

**Acceptance Scenarios**:

1. **Given** the 'priceup' alias already exists in ~/.zshrc, **When** the user runs the pricing tool, **Then** no setup messages are shown and the application launches immediately
2. **Given** the user is in any directory in their terminal, **When** they type 'priceup', **Then** the pricing tool launches with full functionality
3. **Given** multiple terminal sessions are open, **When** 'priceup' is invoked in any session, **Then** it works consistently across all sessions

---

### User Story 3 - Cross-Team Repository Location Flexibility (Priority: P2)

Different team members clone the repository to different locations based on their personal directory preferences. The alias setup automatically adapts to each user's chosen location without requiring manual path configuration.

**Why this priority**: Enables team adoption without configuration overhead - essential for team rollout success.

**Independent Test**: Can be tested by cloning to various directory paths and verifying the generated alias uses the correct absolute path for each location.

**Acceptance Scenarios**:

1. **Given** user A clones to /Users/alice/projects/ and user B clones to /home/bob/code/, **When** each runs the application for the first time, **Then** each gets a correctly configured alias pointing to their respective installation location
2. **Given** a user moves their repository to a new location, **When** they run the application again, **Then** the system detects the path change and updates the alias accordingly
3. **Given** the repository path contains spaces or special characters, **When** the alias is created, **Then** the path is properly escaped in the shell alias

---

### User Story 4 - Git-Unfamiliar User First-Time Setup (Priority: P1)

A business user or non-technical team member needs to use the DTT Pricing Tool but is not familiar with git commands or terminal operations. They need step-by-step instructions that guide them from repository download through first successful tool usage.

**Why this priority**: Enables business user adoption without requiring technical expertise - critical for broader team adoption and tool accessibility.

**Independent Test**: Can be tested by following README instructions from a fresh machine without any development tools pre-installed.

**Acceptance Scenarios**:

1. **Given** a user has never used git before and only has basic computer skills, **When** they follow the README.md first-time setup instructions, **Then** they can successfully download and run the pricing tool
2. **Given** the user follows the git clone instructions, **When** they navigate to the downloaded folder and run the initial setup, **Then** the alias is created and they receive clear next-step instructions
3. **Given** the user completes first-time setup, **When** they open a new terminal session, **Then** they can use the simple 'priceup' command from anywhere

### Edge Cases

- What happens when ~/.zshrc doesn't exist (new user setup)?
- How does system handle when ~/.zshrc is not writable (permission issues)? → Show clear error with fallback instructions for manual alias creation
- What happens if the alias already exists but points to a different location?
- How does the system behave with shell environments other than zsh (bash, fish, etc.)? → System fails with clear error message for non-zsh shells
- What happens when the current working directory is different from the repository location?
- What happens when git is not installed on the user's machine?
- How does the system handle when a user downloads the repository as a ZIP file instead of using git clone?
- What happens when the user clones to a directory that requires sudo/administrator privileges?
- How does the system behave when the git repository URL changes or becomes unavailable?

## Requirements

### Functional Requirements

- **FR-001**: System MUST detect on first run whether the 'priceup' alias exists in the user's ~/.zshrc file and MUST verify zsh shell environment (fail if zsh not detected)
- **FR-002**: System MUST automatically determine the absolute path to the current pricing_tool_accelerator.py script location
- **FR-003**: System MUST create a 'priceup' alias entry in ~/.zshrc that points to the correct absolute path of the pricing tool with file markers (comments) for safe identification
- **FR-004**: System MUST create ~/.zshrc file if it doesn't exist before adding the alias, with clear error and fallback instructions if permission denied
- **FR-005**: System MUST notify the user when the alias is successfully created and provide usage instructions with informational messages only (no interactive prompts)
- **FR-006**: System MUST skip alias creation on subsequent runs when the alias already exists and is correct (silent operation for existing aliases)
- **FR-007**: System MUST handle repository paths containing spaces, special characters, or unicode characters
- **FR-008**: System MUST update the alias if it exists but points to an incorrect or outdated path
- **FR-009**: System MUST provide clear instructions in README.md for both first-time and subsequent usage
- **FR-010**: System MUST work regardless of the user's current working directory when the script is executed
- **FR-011**: README.md MUST include step-by-step git clone instructions suitable for users unfamiliar with git
- **FR-012**: README.md MUST explain what git is and why it's needed for non-technical users
- **FR-013**: README.md MUST provide alternative download methods for users who cannot or will not use git

### Key Entities

- **Shell Alias**: A command shortcut ('priceup') that maps to the full python3 execution command with absolute path
- **User Shell Configuration**: The ~/.zshrc file where the alias is stored and loaded by the shell
- **Repository Path**: The absolute filesystem location where the user has cloned the dtt-pricing-tools-populator repository

## Success Criteria

### Measurable Outcomes

- **SC-001**: First-time users can complete initial setup and alias creation in under 30 seconds (with 60-second timeout for file operations)
- **SC-002**: 100% of users can successfully use the `priceup` command after initial setup
- **SC-003**: System correctly handles repository paths in 100% of common directory structures (with/without spaces, various depths)
- **SC-004**: Zero manual configuration steps required for team members to get a working `priceup` command
- **SC-005**: Alias creation process is idempotent - running multiple times doesn't create duplicate entries
- **SC-006**: Users can move their repository location and system automatically corrects the alias path
- **SC-007**: Git-unfamiliar users can successfully download and set up the tool following README instructions in under 5 minutes
- **SC-008**: 90% of non-technical users can complete repository download without requiring additional support
- **SC-009**: README instructions are clear enough that users don't need to understand what git is to use it successfully

## Technical Analysis

### Recommended Approach

- **Technology choice**: Pure Python standard library (os.path, pathlib) for maximum compatibility and no external dependencies
- **Architecture pattern**: Startup check function that runs before main CLI logic, with optional alias management
- **Integration points**: Minimal modification to existing pricing_tool_accelerator.py main() function with pre-execution hook

### Alternative Approaches Considered

- **Approach A**: Separate shell script installer - Pros: Clean separation, Cons: Additional file complexity, installation steps
- **Approach B**: Package-time installation hooks - Pros: One-time setup, Cons: Doesn't handle repository moves, over-engineering  
- **Approach C**: Manual installation instructions only - Pros: Simple documentation, Cons: Poor user experience, setup friction

## Implementation Dependencies

- **Blocking dependencies**: None (can be implemented immediately using existing codebase)
- **Related features**: Should coordinate with CLI interface improvements and user onboarding documentation
- **External dependencies**: None (pure Python standard library implementation)

---

## Specification Quality

### Spec Quality Checklist

- [x] **Problem statement** clearly describes the user problem
- [x] **User stories** represent actual user value (not just technical tasks)  
- [x] **Requirements** are specific, testable, and implementation-agnostic
- [x] **Success criteria** are measurable outcomes (not activities)
- [x] **Edge cases** cover boundary conditions and error scenarios
- [x] **No implementation details** in problem statement or requirements
- [x] **Dependencies** are clearly identified
- [x] **Spec is reviewable** by non-technical stakeholders
