#!/usr/bin/env python3
"""
Project Configuration Manager
Allows easy configuration of primary webpage and keyword for SEO analysis
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.append('/app')


class ProjectConfigManager:
    """Manages project configuration for SEO analysis"""
    
    def __init__(self, project_name: str = "500rockets"):
        self.project_name = project_name
        self.project_dir = Path(f"/app/projects/{project_name}")
        self.config_file = self.project_dir / "00_config" / "project_config.json"
        
        # Create project if it doesn't exist
        if not self.project_dir.exists():
            self.create_new_project()
    
    def create_new_project(self):
        """Create a new project structure"""
        self.project_dir.mkdir(parents=True, exist_ok=True)
        (self.project_dir / "00_config").mkdir(exist_ok=True)
        
        # Create initial config
        config = {
            "project_name": self.project_name,
            "query": "marketing agency services",
            "target_url": "https://500rockets.io",
            "created_at": datetime.now().isoformat(),
            "status": "initialized",
            "steps_completed": [],
            "current_step": "00_config"
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def update_config(self, target_url: str = None, query: str = None):
        """Update project configuration"""
        # Load existing config
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Update values
        if target_url:
            config["target_url"] = target_url
        if query:
            config["query"] = query
        
        config["last_updated"] = datetime.now().isoformat()
        
        # Save updated config
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return config
    
    def get_config(self):
        """Get current project configuration"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def show_config(self):
        """Display current configuration"""
        config = self.get_config()
        
        print("=" * 60)
        print("  PROJECT CONFIGURATION")
        print("=" * 60)
        print(f"Project Name: {config['project_name']}")
        print(f"Target URL: {config['target_url']}")
        print(f"Search Query: {config['query']}")
        print(f"Status: {config['status']}")
        print(f"Current Step: {config.get('current_step', 'N/A')}")
        print(f"Created: {config['created_at']}")
        if 'last_updated' in config:
            print(f"Last Updated: {config['last_updated']}")
        print("=" * 60)
        print()


def main():
    """Main configuration interface"""
    print("🔧 SEO Mining Project Configuration")
    print()
    
    # Get project name
    project_name = input("Enter project name (default: 500rockets): ").strip()
    if not project_name:
        project_name = "500rockets"
    
    manager = ProjectConfigManager(project_name)
    
    # Show current config
    manager.show_config()
    
    # Ask if user wants to update
    update = input("Do you want to update the configuration? (y/n): ").strip().lower()
    
    if update == 'y':
        print()
        print("Enter new values (press Enter to keep current value):")
        
        # Get current config
        current_config = manager.get_config()
        
        # Get target URL
        new_target = input(f"Target URL [{current_config['target_url']}]: ").strip()
        if not new_target:
            new_target = None
        
        # Get query
        new_query = input(f"Search Query [{current_config['query']}]: ").strip()
        if not new_query:
            new_query = None
        
        # Update config
        if new_target or new_query:
            updated_config = manager.update_config(new_target, new_query)
            print()
            print("✅ Configuration updated!")
            print()
            manager.show_config()
        else:
            print("No changes made.")
    
    print()
    print("📁 Configuration file location:")
    print(f"   {manager.config_file}")
    print()
    print("🚀 To run analysis with this configuration:")
    print(f"   docker exec seo-mining-backend python /app/app/enhanced_workflow_runner.py")
    print()


if __name__ == "__main__":
    main()
