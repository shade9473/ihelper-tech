"""
iHelper Tech Resource Library Structure
Version: 1.0
"""

import os
import json
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('resource_structure.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ResourceStructure')

class ResourceStructure:
    def __init__(self):
        self.base_path = "resources"
        self.structure = {
            "01_Business_Protection": {
                "description": "Core business protection resources",
                "categories": [
                    "System_Security",
                    "Data_Backup",
                    "Monitoring",
                    "Recovery_Plans"
                ]
            },
            "02_Documentation": {
                "description": "System and process documentation",
                "categories": [
                    "User_Guides",
                    "Technical_Docs",
                    "Best_Practices",
                    "Tutorials"
                ]
            },
            "03_Templates": {
                "description": "Business document templates",
                "categories": [
                    "Security_Policies",
                    "Backup_Plans",
                    "Monitoring_Config",
                    "Recovery_Docs"
                ]
            },
            "04_Guides": {
                "description": "Step-by-step implementation guides",
                "categories": [
                    "Setup_Guides",
                    "Configuration",
                    "Maintenance",
                    "Troubleshooting"
                ]
            },
            "05_Tools": {
                "description": "Business protection tools",
                "categories": [
                    "Security_Tools",
                    "Backup_Utils",
                    "Monitoring_Tools",
                    "Recovery_Tools"
                ]
            },
            "06_Policies": {
                "description": "Standard business policies",
                "categories": [
                    "Security_Policies",
                    "Backup_Policies",
                    "Monitoring_Policies",
                    "Recovery_Policies"
                ]
            },
            "07_Training": {
                "description": "Training materials",
                "categories": [
                    "Security_Training",
                    "Backup_Training",
                    "Monitoring_Training",
                    "Recovery_Training"
                ]
            },
            "08_Support": {
                "description": "Support resources",
                "categories": [
                    "FAQs",
                    "Troubleshooting",
                    "Contact_Info",
                    "Help_Guides"
                ]
            }
        }

    def create_structure(self) -> dict:
        """Create the resource library directory structure."""
        try:
            # Create base directory
            os.makedirs(self.base_path, exist_ok=True)
            
            # Create category directories
            for category, info in self.structure.items():
                category_path = os.path.join(self.base_path, category)
                os.makedirs(category_path, exist_ok=True)
                
                # Create README for category
                self._create_category_readme(category_path, info["description"])
                
                # Create subcategories
                for subcategory in info["categories"]:
                    subcategory_path = os.path.join(category_path, subcategory)
                    os.makedirs(subcategory_path, exist_ok=True)
                    
                    # Create README for subcategory
                    self._create_subcategory_readme(
                        subcategory_path,
                        subcategory,
                        category
                    )

            logger.info("Resource structure created successfully")
            return {"status": "success", "message": "Structure created"}

        except Exception as e:
            logger.error(f"Failed to create structure: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _create_category_readme(self, path: str, description: str):
        """Create README file for a category."""
        try:
            readme_path = os.path.join(path, "README.md")
            category_name = os.path.basename(path)
            
            content = f"""# {category_name.replace('_', ' ')}
Version: 1.0
Last Updated: {datetime.now().strftime('%Y-%m-%d')}

## Description
{description}

## Contents
This directory contains the following resources:

"""
            # Add subcategories
            for subcat in self.structure[category_name]["categories"]:
                content += f"- {subcat.replace('_', ' ')}\n"

            with open(readme_path, 'w') as f:
                f.write(content)

        except Exception as e:
            logger.error(f"Failed to create category README: {str(e)}")
            raise

    def _create_subcategory_readme(self, path: str, subcategory: str, 
                                 parent_category: str):
        """Create README file for a subcategory."""
        try:
            readme_path = os.path.join(path, "README.md")
            
            content = f"""# {subcategory.replace('_', ' ')}
Parent: {parent_category.replace('_', ' ')}
Version: 1.0
Last Updated: {datetime.now().strftime('%Y-%m-%d')}

## Purpose
This directory contains {subcategory.replace('_', ' ').lower()} resources.

## Contents
- Documents
- Templates
- Guides
- Examples

## Usage
1. Browse the available resources
2. Select the appropriate template or guide
3. Follow the implementation instructions
4. Contact support if assistance is needed
"""
            with open(readme_path, 'w') as f:
                f.write(content)

        except Exception as e:
            logger.error(f"Failed to create subcategory README: {str(e)}")
            raise

    def verify_structure(self) -> dict:
        """Verify the resource library structure."""
        try:
            missing = []
            
            # Check base directory
            if not os.path.exists(self.base_path):
                missing.append(self.base_path)
                return {
                    "status": "error",
                    "message": "Base directory missing",
                    "missing": missing
                }
            
            # Check categories
            for category in self.structure.keys():
                category_path = os.path.join(self.base_path, category)
                if not os.path.exists(category_path):
                    missing.append(category_path)
                    continue
                
                # Check README
                readme_path = os.path.join(category_path, "README.md")
                if not os.path.exists(readme_path):
                    missing.append(readme_path)
                
                # Check subcategories
                for subcategory in self.structure[category]["categories"]:
                    subcategory_path = os.path.join(category_path, subcategory)
                    if not os.path.exists(subcategory_path):
                        missing.append(subcategory_path)
                        continue
                    
                    # Check README
                    readme_path = os.path.join(subcategory_path, "README.md")
                    if not os.path.exists(readme_path):
                        missing.append(readme_path)

            if missing:
                return {
                    "status": "incomplete",
                    "message": "Structure incomplete",
                    "missing": missing
                }

            return {
                "status": "success",
                "message": "Structure verified"
            }

        except Exception as e:
            logger.error(f"Failed to verify structure: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def get_structure(self) -> dict:
        """Get the current resource library structure."""
        try:
            current_structure = {
                "last_updated": datetime.now().isoformat(),
                "categories": {}
            }
            
            # Base directory must exist
            if not os.path.exists(self.base_path):
                return {
                    "status": "error",
                    "message": "Base directory missing"
                }
            
            # Get categories
            for category in self.structure.keys():
                category_path = os.path.join(self.base_path, category)
                if not os.path.exists(category_path):
                    continue
                
                current_structure["categories"][category] = {
                    "description": self.structure[category]["description"],
                    "subcategories": {}
                }
                
                # Get subcategories
                for subcategory in self.structure[category]["categories"]:
                    subcategory_path = os.path.join(category_path, subcategory)
                    if not os.path.exists(subcategory_path):
                        continue
                    
                    # Count files
                    files = [f for f in os.listdir(subcategory_path) 
                            if os.path.isfile(os.path.join(subcategory_path, f))]
                    
                    current_structure["categories"][category]\
                        ["subcategories"][subcategory] = {
                        "path": subcategory_path,
                        "file_count": len(files)
                    }

            return {
                "status": "success",
                "structure": current_structure
            }

        except Exception as e:
            logger.error(f"Failed to get structure: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

# Example usage:
if __name__ == "__main__":
    # Initialize structure
    structure = ResourceStructure()
    
    # Create structure
    result = structure.create_structure()
    if result["status"] == "success":
        # Verify structure
        verify_result = structure.verify_structure()
        if verify_result["status"] == "success":
            # Get current structure
            current = structure.get_structure()
            print(json.dumps(current, indent=2))
