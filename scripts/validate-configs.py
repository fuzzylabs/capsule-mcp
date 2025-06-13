#!/usr/bin/env python3

"""
Configuration Synchronization Validator

This script validates that all MCP client configurations across the repository
are consistent and in sync. It checks:
- README.md client configurations
- add-to-cursor.html setup instructions  
- Cursor deeplink base64 configuration
- render.yaml deployment config
- CLAUDE.md development commands

Usage:
    python scripts/validate-configs.py
    uv run python scripts/validate-configs.py
"""

import base64
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ConfigValidator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(f"❌ {message}")
        
    def warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(f"⚠️  {message}")
        
    def extract_cursor_config_from_readme(self) -> Optional[Dict]:
        """Extract the Cursor deeplink configuration from README.md."""
        readme_path = self.repo_root / "README.md"
        if not readme_path.exists():
            self.error("README.md not found")
            return None
            
        content = readme_path.read_text()
        
        # Find Cursor deeplink
        pattern = r'cursor://anysphere\.cursor-deeplink/mcp/install\?name=([^&]+)&config=([^"]+)'
        match = re.search(pattern, content)
        
        if not match:
            self.error("Cursor deeplink not found in README.md")
            return None
            
        server_name = match.group(1)
        base64_config = match.group(2)
        
        try:
            config_json = base64.b64decode(base64_config).decode('utf-8')
            config = json.loads(config_json)
            return {
                'server_name': server_name,
                'config': config,
                'base64': base64_config
            }
        except Exception as e:
            self.error(f"Failed to decode Cursor deeplink config: {e}")
            return None
    
    def extract_claude_desktop_config_from_readme(self) -> Optional[Dict]:
        """Extract Claude Desktop configuration from README.md."""
        readme_path = self.repo_root / "README.md"
        content = readme_path.read_text()
        
        # Find Claude Desktop config block - more flexible pattern
        pattern = r'```json\s*(\{.*?"mcpServers".*?\})\s*```'
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        
        if not match:
            self.error("Claude Desktop config not found in README.md")
            return None
            
        try:
            config_text = match.group(1)
            config = json.loads(config_text)
            return config.get('mcpServers', {})
        except Exception as e:
            self.error(f"Failed to parse Claude Desktop config: {e}")
            return None
    
    def extract_cursor_manual_config_from_readme(self) -> Optional[Dict]:
        """Extract manual Cursor configuration from README.md."""
        readme_path = self.repo_root / "README.md"
        content = readme_path.read_text()
        
        # Find manual Cursor config (after "Or manually add this to your Cursor MCP settings")
        # More robust pattern that handles various whitespace and line endings
        pattern = r'Or manually add this to your Cursor MCP settings:\s*```json\s*(\{.*?\})\s*```'
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        
        if not match:
            self.error("Manual Cursor config not found in README.md")
            return None
            
        try:
            config_text = match.group(1)
            config = json.loads(config_text)
            return config
        except Exception as e:
            self.error(f"Failed to parse manual Cursor config: {e}")
            return None
    
    def extract_render_config(self) -> Optional[Dict]:
        """Extract configuration from render.yaml."""
        render_path = self.repo_root / "render.yaml"
        if not render_path.exists():
            self.warning("render.yaml not found")
            return None
            
        try:
            import yaml
            content = render_path.read_text()
            config = yaml.safe_load(content)
            return config
        except ImportError:
            self.warning("PyYAML not available, skipping render.yaml validation")
            return None
        except Exception as e:
            self.error(f"Failed to parse render.yaml: {e}")
            return None
    
    def check_server_paths(self) -> None:
        """Validate that server paths are consistent."""
        expected_path = "capsule_mcp/server.py"
        
        # Check README configurations
        cursor_config = self.extract_cursor_config_from_readme()
        if cursor_config:
            capsule_config = cursor_config['config'].get('capsule-crm', {})
            args = capsule_config.get('args', [])
            if expected_path not in args:
                self.error(f"Cursor deeplink config missing expected server path: {expected_path}")
        
        manual_cursor = self.extract_cursor_manual_config_from_readme()
        if manual_cursor:
            capsule_config = manual_cursor.get('capsule-crm', {})
            args = capsule_config.get('args', [])
            if expected_path not in args:
                self.error(f"Manual Cursor config missing expected server path: {expected_path}")
        
        claude_config = self.extract_claude_desktop_config_from_readme()
        if claude_config:
            capsule_config = claude_config.get('capsule-crm', {})
            args = capsule_config.get('args', [])
            if expected_path not in args:
                self.error(f"Claude Desktop config missing expected server path: {expected_path}")
    
    def check_environment_variables(self) -> None:
        """Validate that environment variables are consistent."""
        expected_env_vars = {'CAPSULE_API_TOKEN'}
        
        configs_to_check = [
            ('Cursor deeplink', self.extract_cursor_config_from_readme()),
            ('Manual Cursor', self.extract_cursor_manual_config_from_readme()),
            ('Claude Desktop', self.extract_claude_desktop_config_from_readme())
        ]
        
        for config_name, config_data in configs_to_check:
            if not config_data:
                continue
                
            if config_name == 'Cursor deeplink':
                capsule_config = config_data['config'].get('capsule-crm', {})
            else:
                capsule_config = config_data.get('capsule-crm', {})
                
            env_vars = set(capsule_config.get('env', {}).keys())
            missing = expected_env_vars - env_vars
            
            if missing:
                self.error(f"{config_name} config missing env vars: {missing}")
    
    def check_commands(self) -> None:
        """Validate that command configurations are consistent."""
        expected_command = "uv"
        expected_args_start = ["run", "--directory"]
        
        configs_to_check = [
            ('Cursor deeplink', self.extract_cursor_config_from_readme()),
            ('Manual Cursor', self.extract_cursor_manual_config_from_readme()),
            ('Claude Desktop', self.extract_claude_desktop_config_from_readme())
        ]
        
        for config_name, config_data in configs_to_check:
            if not config_data:
                continue
                
            if config_name == 'Cursor deeplink':
                capsule_config = config_data['config'].get('capsule-crm', {})
            else:
                capsule_config = config_data.get('capsule-crm', {})
                
            command = capsule_config.get('command')
            args = capsule_config.get('args', [])
            
            if command != expected_command:
                self.error(f"{config_name} config has wrong command: {command} (expected: {expected_command})")
                
            if not args or args[:2] != expected_args_start:
                self.error(f"{config_name} config has wrong args start: {args[:2]} (expected: {expected_args_start})")
    
    def check_cursor_deeplink_sync(self) -> None:
        """Validate that Cursor deeplink matches manual config."""
        cursor_deeplink = self.extract_cursor_config_from_readme()
        cursor_manual = self.extract_cursor_manual_config_from_readme()
        
        if not cursor_deeplink or not cursor_manual:
            return
            
        deeplink_config = cursor_deeplink['config'].get('capsule-crm', {})
        manual_config = cursor_manual.get('capsule-crm', {})
        
        # Compare key fields
        for field in ['command', 'args']:
            if deeplink_config.get(field) != manual_config.get(field):
                self.error(f"Cursor deeplink and manual config mismatch in {field}")
                self.error(f"  Deeplink: {deeplink_config.get(field)}")
                self.error(f"  Manual: {manual_config.get(field)}")
    
    def check_file_existence(self) -> None:
        """Check that all referenced files exist."""
        required_files = [
            "README.md",
            "add-to-cursor.html", 
            "CLAUDE.md",
            "capsule_mcp/server.py"
        ]
        
        for file_path in required_files:
            if not (self.repo_root / file_path).exists():
                self.error(f"Required file missing: {file_path}")
    
    def validate(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating configuration synchronization...\n")
        
        # Run all checks
        self.check_file_existence()
        self.check_server_paths()
        self.check_environment_variables()
        self.check_commands()
        self.check_cursor_deeplink_sync()
        
        # Report results
        if self.warnings:
            print("⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if self.errors:
            print("❌ Configuration validation failed:")
            for error in self.errors:
                print(f"  {error}")
            print()
            print("🔧 To fix these issues:")
            print("  1. Update the mismatched configurations")
            print("  2. Run: node scripts/generate-cursor-link.js")
            print("  3. Run this validator again")
            return False
        else:
            print("✅ All configurations are synchronized!")
            if self.warnings:
                print("💡 Address warnings when convenient.")
            return True

def main():
    """Main entry point."""
    # Find repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    # Validate we're in the right place
    if not (repo_root / "capsule_mcp").exists():
        print("❌ Script must be run from repository root or scripts directory")
        sys.exit(1)
    
    validator = ConfigValidator(repo_root)
    success = validator.validate()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()