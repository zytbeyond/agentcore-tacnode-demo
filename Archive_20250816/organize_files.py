#!/usr/bin/env python3
"""
Organize files - keep essential working files, archive the rest
"""

import os
import shutil

def organize_files():
    """Move unnecessary files to Archive_20250816"""
    
    # Essential files to keep (current working setup)
    essential_files = {
        # Core working files
        'query_database.py',
        'tacnode_token.txt',
        'agentcore-cognito-config.json',
        'secure-lambda-tacnode-config.json',
        
        # Documentation
        'README.md',
        'FINAL_AGENTCORE_TACNODE_INTEGRATION_SUMMARY.md',
        
        # Git files
        '.git',
        '.gitignore',
        
        # Archive folder
        'Archive_20250816'
    }
    
    # Files to archive (move to Archive_20250816)
    files_to_archive = []
    
    # Get all files and directories
    for item in os.listdir('.'):
        if item not in essential_files and not item.startswith('.'):
            files_to_archive.append(item)
    
    print("🗂️ ORGANIZING FILES")
    print("=" * 50)
    print(f"📁 Keeping essential files:")
    for file in sorted(essential_files):
        if os.path.exists(file):
            print(f"   ✅ {file}")
    
    print(f"\n📦 Moving to Archive_20250816:")
    
    archive_count = 0
    for item in files_to_archive:
        try:
            if os.path.exists(item):
                dest_path = os.path.join('Archive_20250816', item)
                if os.path.isdir(item):
                    shutil.move(item, dest_path)
                    print(f"   📁 {item}/")
                else:
                    shutil.move(item, dest_path)
                    print(f"   📄 {item}")
                archive_count += 1
        except Exception as e:
            print(f"   ❌ Error moving {item}: {e}")
    
    print(f"\n✅ Organization complete!")
    print(f"   📁 Archived: {archive_count} items")
    print(f"   📁 Kept: {len([f for f in essential_files if os.path.exists(f)])} essential files")
    
    return True

if __name__ == "__main__":
    organize_files()
