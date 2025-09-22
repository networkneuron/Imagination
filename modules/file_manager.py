"""
File and Folder Management Module

Handles file operations, organization, and bulk file management with safety checks.
"""

import os
import shutil
import hashlib
import logging
import zipfile
import tarfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import mimetypes

class FileManager:
    """Handles file and folder operations with safety checks"""
    
    def __init__(self, safety_manager):
        self.safety_manager = safety_manager
        self.logger = logging.getLogger(__name__)
    
    def create_file(self, file_path: str, content: str = "", overwrite: bool = False) -> bool:
        """Create a new file with content"""
        try:
            path = Path(file_path)
            
            # Check if file exists and overwrite is not allowed
            if path.exists() and not overwrite:
                self.logger.warning(f"File already exists: {file_path}")
                return False
            
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Created file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating file {file_path}: {e}")
            return False
    
    def create_directory(self, dir_path: str, parents: bool = True) -> bool:
        """Create a directory"""
        try:
            path = Path(dir_path)
            path.mkdir(parents=parents, exist_ok=True)
            self.logger.info(f"Created directory: {dir_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating directory {dir_path}: {e}")
            return False
    
    def copy_file(self, src: str, dst: str, overwrite: bool = False) -> bool:
        """Copy a file from source to destination"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                self.logger.error(f"Source file does not exist: {src}")
                return False
            
            if dst_path.exists() and not overwrite:
                self.logger.warning(f"Destination file already exists: {dst}")
                return False
            
            # Create destination directory if it doesn't exist
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, dst_path)
            self.logger.info(f"Copied file: {src} -> {dst}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error copying file {src} to {dst}: {e}")
            return False
    
    def move_file(self, src: str, dst: str, overwrite: bool = False) -> bool:
        """Move a file from source to destination"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                self.logger.error(f"Source file does not exist: {src}")
                return False
            
            if dst_path.exists() and not overwrite:
                self.logger.warning(f"Destination file already exists: {dst}")
                return False
            
            # Create destination directory if it doesn't exist
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src_path), str(dst_path))
            self.logger.info(f"Moved file: {src} -> {dst}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error moving file {src} to {dst}: {e}")
            return False
    
    def delete_file(self, file_path: str, confirm: bool = True) -> bool:
        """Delete a file with optional confirmation"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                self.logger.warning(f"File does not exist: {file_path}")
                return False
            
            if confirm and not self.safety_manager.confirm_dangerous_action(f"Delete file: {file_path}"):
                return False
            
            if path.is_file():
                path.unlink()
                self.logger.info(f"Deleted file: {file_path}")
            else:
                self.logger.error(f"Path is not a file: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def delete_directory(self, dir_path: str, recursive: bool = False, confirm: bool = True) -> bool:
        """Delete a directory with optional confirmation"""
        try:
            path = Path(dir_path)
            
            if not path.exists():
                self.logger.warning(f"Directory does not exist: {dir_path}")
                return False
            
            if not path.is_dir():
                self.logger.error(f"Path is not a directory: {dir_path}")
                return False
            
            if confirm and not self.safety_manager.confirm_dangerous_action(f"Delete directory: {dir_path}"):
                return False
            
            if recursive:
                shutil.rmtree(path)
                self.logger.info(f"Deleted directory recursively: {dir_path}")
            else:
                path.rmdir()
                self.logger.info(f"Deleted directory: {dir_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting directory {dir_path}: {e}")
            return False
    
    def find_files(self, directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:
        """Find files matching a pattern in a directory"""
        try:
            path = Path(directory)
            
            if not path.exists():
                self.logger.error(f"Directory does not exist: {directory}")
                return []
            
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))
            
            # Filter to only files (not directories)
            file_paths = [str(f) for f in files if f.is_file()]
            
            self.logger.info(f"Found {len(file_paths)} files matching pattern '{pattern}' in {directory}")
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error finding files in {directory}: {e}")
            return []
    
    def find_duplicates(self, directory: str, recursive: bool = True) -> Dict[str, List[str]]:
        """Find duplicate files by content hash"""
        try:
            file_hashes = {}
            duplicates = {}
            
            files = self.find_files(directory, "*", recursive)
            
            for file_path in files:
                try:
                    file_hash = self.get_file_hash(file_path)
                    
                    if file_hash in file_hashes:
                        if file_hash not in duplicates:
                            duplicates[file_hash] = [file_hashes[file_hash]]
                        duplicates[file_hash].append(file_path)
                    else:
                        file_hashes[file_hash] = file_path
                        
                except Exception as e:
                    self.logger.warning(f"Error processing file {file_path}: {e}")
                    continue
            
            self.logger.info(f"Found {len(duplicates)} groups of duplicate files")
            return duplicates
            
        except Exception as e:
            self.logger.error(f"Error finding duplicates in {directory}: {e}")
            return {}
    
    def get_file_hash(self, file_path: str, algorithm: str = "md5") -> str:
        """Get hash of a file"""
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error getting hash of {file_path}: {e}")
            return ""
    
    def organize_files(self, directory: str, organize_by: str = "extension") -> bool:
        """Organize files in a directory by specified criteria"""
        try:
            path = Path(directory)
            
            if not path.exists() or not path.is_dir():
                self.logger.error(f"Directory does not exist: {directory}")
                return False
            
            files = [f for f in path.iterdir() if f.is_file()]
            
            for file_path in files:
                try:
                    if organize_by == "extension":
                        # Organize by file extension
                        ext = file_path.suffix.lower()
                        if not ext:
                            ext = "no_extension"
                        else:
                            ext = ext[1:]  # Remove the dot
                        
                        target_dir = path / ext
                        target_dir.mkdir(exist_ok=True)
                        
                        new_path = target_dir / file_path.name
                        shutil.move(str(file_path), str(new_path))
                        
                    elif organize_by == "date":
                        # Organize by creation date
                        creation_time = datetime.fromtimestamp(file_path.stat().st_ctime)
                        date_str = creation_time.strftime("%Y-%m-%d")
                        
                        target_dir = path / date_str
                        target_dir.mkdir(exist_ok=True)
                        
                        new_path = target_dir / file_path.name
                        shutil.move(str(file_path), str(new_path))
                        
                    elif organize_by == "type":
                        # Organize by MIME type
                        mime_type, _ = mimetypes.guess_type(str(file_path))
                        if mime_type:
                            type_dir = mime_type.split('/')[0]
                        else:
                            type_dir = "unknown"
                        
                        target_dir = path / type_dir
                        target_dir.mkdir(exist_ok=True)
                        
                        new_path = target_dir / file_path.name
                        shutil.move(str(file_path), str(new_path))
                
                except Exception as e:
                    self.logger.warning(f"Error organizing file {file_path}: {e}")
                    continue
            
            self.logger.info(f"Organized files in {directory} by {organize_by}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error organizing files in {directory}: {e}")
            return False
    
    def cleanup_old_files(self, directory: str, days_old: int = 30, confirm: bool = True) -> int:
        """Delete files older than specified days"""
        try:
            path = Path(directory)
            
            if not path.exists() or not path.is_dir():
                self.logger.error(f"Directory does not exist: {directory}")
                return 0
            
            cutoff_time = datetime.now() - timedelta(days=days_old)
            deleted_count = 0
            
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        
                        if file_time < cutoff_time:
                            if confirm and not self.safety_manager.confirm_dangerous_action(f"Delete old file: {file_path}"):
                                continue
                            
                            file_path.unlink()
                            deleted_count += 1
                            
                    except Exception as e:
                        self.logger.warning(f"Error processing file {file_path}: {e}")
                        continue
            
            self.logger.info(f"Deleted {deleted_count} files older than {days_old} days")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old files in {directory}: {e}")
            return 0
    
    def create_backup(self, source: str, backup_dir: str, compress: bool = True) -> bool:
        """Create a backup of files or directories"""
        try:
            source_path = Path(source)
            backup_path = Path(backup_dir)
            
            if not source_path.exists():
                self.logger.error(f"Source does not exist: {source}")
                return False
            
            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if compress:
                if source_path.is_file():
                    backup_file = backup_path / f"{source_path.stem}_{timestamp}.zip"
                    with zipfile.ZipFile(backup_file, 'w') as zipf:
                        zipf.write(source_path, source_path.name)
                else:
                    backup_file = backup_path / f"{source_path.name}_{timestamp}.tar.gz"
                    with tarfile.open(backup_file, 'w:gz') as tarf:
                        tarf.add(source_path, arcname=source_path.name)
            else:
                if source_path.is_file():
                    backup_file = backup_path / f"{source_path.stem}_{timestamp}{source_path.suffix}"
                    shutil.copy2(source_path, backup_file)
                else:
                    backup_dir = backup_path / f"{source_path.name}_{timestamp}"
                    shutil.copytree(source_path, backup_dir)
            
            self.logger.info(f"Created backup: {source} -> {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating backup of {source}: {e}")
            return False
    
    def get_directory_size(self, directory: str) -> int:
        """Get total size of a directory in bytes"""
        try:
            total_size = 0
            path = Path(directory)
            
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size
            
        except Exception as e:
            self.logger.error(f"Error getting directory size for {directory}: {e}")
            return 0
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed information about a file"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {}
            
            stat = path.stat()
            
            info = {
                "name": path.name,
                "path": str(path.absolute()),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "accessed": datetime.fromtimestamp(stat.st_atime),
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "extension": path.suffix,
                "parent": str(path.parent),
            }
            
            # Add MIME type if available
            mime_type, _ = mimetypes.guess_type(str(path))
            if mime_type:
                info["mime_type"] = mime_type
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {e}")
            return {}
