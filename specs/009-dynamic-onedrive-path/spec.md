# Feature Specification: Dynamic OneDrive Path Configuration

**Feature Branch**: `009-dynamic-onedrive-path`  
**Created**: 2025-10-28  
**Status**: Draft  
**Input**: User description: "Dynamic OneDrive path configuration for cross-user deployment compatibility"

## Clarifications

### Session 2025-10-28

- Q: Configuration Storage Location → A: Store in user home directory as hidden file (e.g., ~/.dtt-pricing-tool-populator-config)
- Q: Setup Wizard Interaction Method → A: Interactive command-line prompts (text input in terminal)
- Q: Path Validation Timing → A: Validate only when path access fails (lazy validation, faster startup)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-Time Path Setup (Priority: P1)

When a new user runs the pricing tool for the first time on their machine, the system detects that OneDrive paths are not configured and guides them through a one-time setup to locate their specific OneDrive folder structure.

**Why this priority**: This is the core blocker preventing deployment across different user machines. Without this, the tool fails completely for users with different OneDrive mappings.

**Independent Test**: Can be fully tested by running the tool on a fresh machine without any path configuration and verifying the setup wizard completes successfully and saves the correct paths.

**Acceptance Scenarios**:

1. **Given** a user runs the pricing tool for the first time, **When** the system detects no OneDrive path configuration exists, **Then** the system displays interactive command-line prompts asking for the PricingToolAccel folder path
2. **Given** a user provides a valid PricingToolAccel folder path during setup, **When** the system validates the path contains the expected subdirectories (00-CONSTANTS, 10-LATEST-PRICING-TOOLS, 20-OUTPUT), **Then** the system saves the configuration and proceeds with normal operation
3. **Given** a user provides an invalid path during setup, **When** the system cannot find the expected subdirectories, **Then** the system displays an error message and prompts the user to provide the correct path

---

### User Story 2 - Automatic Path Validation (Priority: P2)

When the pricing tool starts with existing path configuration, the system validates that the configured paths are still accessible and displays helpful error messages if OneDrive sync issues or path changes have occurred.

**Why this priority**: Prevents confusing errors when OneDrive paths become inaccessible due to sync issues or organizational changes.

**Independent Test**: Can be tested by modifying saved path configuration to point to non-existent directories and verifying appropriate error handling.

**Acceptance Scenarios**:

1. **Given** the user has previously configured OneDrive paths, **When** the system starts and the paths are accessible, **Then** the system proceeds with normal operation without prompting
2. **Given** the user has previously configured OneDrive paths, **When** the system starts and the paths are not accessible, **Then** the system displays a clear error message explaining the issue and offers to reconfigure paths
3. **Given** OneDrive is not synced or offline, **When** the user attempts to run the tool, **Then** the system provides guidance on checking OneDrive sync status

---

### User Story 3 - Path Reconfiguration (Priority: P3)

Users can manually reconfigure their OneDrive paths when their organizational structure changes or they need to point to different shared libraries.

**Why this priority**: Provides flexibility for organizational changes but not critical for initial deployment.

**Independent Test**: Can be tested by running a reconfiguration command and verifying paths are updated correctly.

**Acceptance Scenarios**:

1. **Given** the user wants to change their OneDrive path configuration, **When** they run a reconfiguration command, **Then** the system guides them through the same setup process as first-time users
2. **Given** the user reconfigures paths to a new valid location, **When** the configuration is saved, **Then** subsequent tool runs use the new paths correctly

---

### Edge Cases

- What happens when user provides a path that exists but doesn't contain the required subdirectories?
- How does system handle paths with special characters or spaces?
- What occurs when OneDrive is temporarily offline during path validation?
- How does system behave when user lacks permissions to access provided path?

## Requirements *(mandatory)*

### Functional Requirements

**FR-001**: System MUST detect if OneDrive path configuration exists on first run
**FR-002**: System MUST prompt users to provide the full path to their PricingToolAccel folder during initial setup
**FR-003**: System MUST validate that provided paths contain required subdirectories (00-CONSTANTS, 10-LATEST-PRICING-TOOLS, 20-OUTPUT)
**FR-004**: System MUST save path configuration persistently in user home directory as hidden file. It should be named as per the repo name. 
**FR-005**: System MUST construct full directory paths by appending standard subdirectory names to the user-provided base path
**FR-006**: System MUST validate path accessibility only when path access fails (lazy validation)
**FR-007**: System MUST provide clear error messages when configured paths are inaccessible
**FR-008**: System MUST offer path reconfiguration when validation fails
**FR-009**: System MUST handle network connectivity issues gracefully with appropriate messaging
**FR-010**: System MUST provide a simple command or flag to reconfigure paths manually
**FR-011**: System MUST display current path configuration when requested
**FR-012**: System MUST complete initial setup in under 2 minutes for typical users

### Key Entities

**PathConfiguration**: Represents user-specific OneDrive path settings including base path to PricingToolAccel folder, derived paths to subdirectories, validation status, and last successful validation timestamp

**SetupWizard**: Manages the initial configuration process including user input collection, path validation, error handling, and configuration persistence

## Success Criteria *(mandatory)*

### Measurable Outcomes

**SC-001**: 100% of users with different OneDrive mappings can successfully complete initial setup
**SC-002**: Tool startup time remains under 5 seconds after initial configuration
**SC-003**: Path validation catches 95% of common OneDrive accessibility issues
**SC-004**: Users can reconfigure paths in under 30 seconds
**SC-005**: Setup wizard has less than 5% error rate for valid OneDrive structures
**SC-006**: Zero hard-coded OneDrive paths remain in the codebase after implementation
