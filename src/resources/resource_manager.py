"""
iHelper Tech Resource Library Manager
Version: 1.0
"""

import os
import json
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('resources.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ResourceLibrary')

class ResourceManager:
    def __init__(self):
        self.resources_root = "resources"
        self.categories = {
            "templates": {
                "path": "templates",
                "description": "Business document templates",
                "formats": [".docx", ".xlsx", ".pdf"]
            },
            "guides": {
                "path": "guides",
                "description": "How-to guides and documentation",
                "formats": [".pdf", ".md"]
            },
            "tools": {
                "path": "tools",
                "description": "Business automation tools",
                "formats": [".py", ".exe", ".bat"]
            },
            "policies": {
                "path": "policies",
                "description": "Standard policies and procedures",
                "formats": [".pdf", ".docx"]
            }
        }
        self._initialize_structure()

    def _initialize_structure(self):
        """Initialize the resource library structure."""
        try:
            # Create main directory
            os.makedirs(self.resources_root, exist_ok=True)
            
            # Create category directories
            for category in self.categories.values():
                os.makedirs(
                    os.path.join(self.resources_root, category["path"]),
                    exist_ok=True
                )
            
            # Create index file
            self._update_index()
            
            logger.info("Resource library structure initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize structure: {str(e)}")
            raise

    def add_resource(self, category: str, name: str, 
                    file_path: str, metadata: dict) -> dict:
        """Add a new resource to the library."""
        try:
            if category not in self.categories:
                return {
                    "status": "error",
                    "message": f"Invalid category: {category}"
                }

            # Validate file format
            _, ext = os.path.splitext(file_path)
            if ext not in self.categories[category]["formats"]:
                return {
                    "status": "error",
                    "message": f"Invalid format {ext} for category {category}"
                }

            # Create destination path
            dest_path = os.path.join(
                self.resources_root,
                self.categories[category]["path"],
                name + ext
            )

            # Copy file
            shutil.copy2(file_path, dest_path)

            # Add metadata
            self._add_metadata(category, name + ext, metadata)

            # Update index
            self._update_index()

            logger.info(f"Added resource: {name} to {category}")
            return {
                "status": "success",
                "path": dest_path
            }

        except Exception as e:
            logger.error(f"Failed to add resource: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def remove_resource(self, category: str, name: str) -> dict:
        """Remove a resource from the library."""
        try:
            if category not in self.categories:
                return {
                    "status": "error",
                    "message": f"Invalid category: {category}"
                }

            # Find resource
            category_path = os.path.join(
                self.resources_root,
                self.categories[category]["path"]
            )
            
            resource_path = None
            for ext in self.categories[category]["formats"]:
                test_path = os.path.join(category_path, name + ext)
                if os.path.exists(test_path):
                    resource_path = test_path
                    break

            if not resource_path:
                return {
                    "status": "error",
                    "message": f"Resource not found: {name}"
                }

            # Remove file
            os.remove(resource_path)

            # Remove metadata
            self._remove_metadata(category, os.path.basename(resource_path))

            # Update index
            self._update_index()

            logger.info(f"Removed resource: {name} from {category}")
            return {
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Failed to remove resource: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def get_resource(self, category: str, name: str) -> dict:
        """Get information about a specific resource."""
        try:
            if category not in self.categories:
                return {
                    "status": "error",
                    "message": f"Invalid category: {category}"
                }

            # Find resource
            category_path = os.path.join(
                self.resources_root,
                self.categories[category]["path"]
            )
            
            resource_path = None
            for ext in self.categories[category]["formats"]:
                test_path = os.path.join(category_path, name + ext)
                if os.path.exists(test_path):
                    resource_path = test_path
                    break

            if not resource_path:
                return {
                    "status": "error",
                    "message": f"Resource not found: {name}"
                }

            # Get metadata
            metadata = self._get_metadata(category, os.path.basename(resource_path))

            return {
                "status": "success",
                "path": resource_path,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Failed to get resource: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def list_resources(self, category: str = None) -> dict:
        """List resources in the library."""
        try:
            resources = {}
            
            if category:
                if category not in self.categories:
                    return {
                        "status": "error",
                        "message": f"Invalid category: {category}"
                    }
                categories = {category: self.categories[category]}
            else:
                categories = self.categories

            for cat_name, cat_info in categories.items():
                cat_path = os.path.join(self.resources_root, cat_info["path"])
                resources[cat_name] = []
                
                if os.path.exists(cat_path):
                    for file in os.listdir(cat_path):
                        name, ext = os.path.splitext(file)
                        if ext in cat_info["formats"]:
                            metadata = self._get_metadata(cat_name, file)
                            resources[cat_name].append({
                                "name": name,
                                "format": ext,
                                "metadata": metadata
                            })

            return {
                "status": "success",
                "resources": resources
            }

        except Exception as e:
            logger.error(f"Failed to list resources: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _add_metadata(self, category: str, filename: str, metadata: dict):
        """Add metadata for a resource."""
        try:
            metadata_path = os.path.join(
                self.resources_root,
                "metadata.json"
            )
            
            current_metadata = {}
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    current_metadata = json.load(f)

            if category not in current_metadata:
                current_metadata[category] = {}

            current_metadata[category][filename] = {
                "added": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                **metadata
            }

            with open(metadata_path, 'w') as f:
                json.dump(current_metadata, f, indent=4)

        except Exception as e:
            logger.error(f"Failed to add metadata: {str(e)}")
            raise

    def _remove_metadata(self, category: str, filename: str):
        """Remove metadata for a resource."""
        try:
            metadata_path = os.path.join(
                self.resources_root,
                "metadata.json"
            )
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    current_metadata = json.load(f)

                if category in current_metadata:
                    if filename in current_metadata[category]:
                        del current_metadata[category][filename]

                with open(metadata_path, 'w') as f:
                    json.dump(current_metadata, f, indent=4)

        except Exception as e:
            logger.error(f"Failed to remove metadata: {str(e)}")
            raise

    def _get_metadata(self, category: str, filename: str) -> dict:
        """Get metadata for a resource."""
        try:
            metadata_path = os.path.join(
                self.resources_root,
                "metadata.json"
            )
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    current_metadata = json.load(f)

                if category in current_metadata:
                    if filename in current_metadata[category]:
                        return current_metadata[category][filename]

            return {}

        except Exception as e:
            logger.error(f"Failed to get metadata: {str(e)}")
            return {}

    def _update_index(self):
        """Update the resource library index."""
        try:
            index = {
                "last_updated": datetime.now().isoformat(),
                "categories": {}
            }

            for cat_name, cat_info in self.categories.items():
                cat_path = os.path.join(self.resources_root, cat_info["path"])
                index["categories"][cat_name] = {
                    "description": cat_info["description"],
                    "formats": cat_info["formats"],
                    "resources": []
                }

                if os.path.exists(cat_path):
                    for file in os.listdir(cat_path):
                        name, ext = os.path.splitext(file)
                        if ext in cat_info["formats"]:
                            metadata = self._get_metadata(cat_name, file)
                            index["categories"][cat_name]["resources"].append({
                                "name": name,
                                "format": ext,
                                "metadata": metadata
                            })

            index_path = os.path.join(self.resources_root, "index.json")
            with open(index_path, 'w') as f:
                json.dump(index, f, indent=4)

        except Exception as e:
            logger.error(f"Failed to update index: {str(e)}")
            raise

# Example usage:
if __name__ == "__main__":
    # Initialize resource manager
    manager = ResourceManager()

    # Add a test resource
    metadata = {
        "description": "Sample business plan template",
        "version": "1.0",
        "author": "iHelper Tech"
    }
    
    result = manager.add_resource(
        "templates",
        "business_plan",
        "path/to/template.docx",
        metadata
    )
