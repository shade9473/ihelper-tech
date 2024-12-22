"""
iHelper Tech Client Onboarding System
Version: 1.0
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Optional
from ..integration.system_integrator import SystemIntegrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('onboarding.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('Onboarding')

class ClientOnboarding:
    def __init__(self):
        self.integrator = SystemIntegrator()
        self.clients = {}
        self.onboarding_steps = {
            'initial_contact': {
                'order': 1,
                'required': True,
                'description': 'Initial client contact and information gathering'
            },
            'system_assessment': {
                'order': 2,
                'required': True,
                'description': 'Assessment of client systems and requirements'
            },
            'service_agreement': {
                'order': 3,
                'required': True,
                'description': 'Service agreement review and signing'
            },
            'system_setup': {
                'order': 4,
                'required': True,
                'description': 'Initial system setup and configuration'
            },
            'monitoring_setup': {
                'order': 5,
                'required': True,
                'description': 'PrecisionWatch monitoring setup'
            },
            'backup_setup': {
                'order': 6,
                'required': True,
                'description': 'EASY_SECURE backup configuration'
            },
            'resource_access': {
                'order': 7,
                'required': False,
                'description': 'Resource library access setup'
            },
            'final_verification': {
                'order': 8,
                'required': True,
                'description': 'Final system verification and documentation'
            }
        }

    def start_onboarding(self, client_info: dict) -> dict:
        """Start the onboarding process for a new client."""
        try:
            client_id = client_info.get('business_name').lower().replace(' ', '_')
            
            if client_id in self.clients:
                return {
                    'status': 'error',
                    'message': 'Client already exists'
                }

            # Initialize client record
            self.clients[client_id] = {
                'info': client_info,
                'status': 'onboarding',
                'start_date': datetime.now().isoformat(),
                'current_step': 'initial_contact',
                'completed_steps': {},
                'pending_steps': list(self.onboarding_steps.keys()),
                'notes': []
            }

            # Create client directory
            self._create_client_directory(client_id)

            logger.info(f"Started onboarding for {client_id}")
            return {
                'status': 'success',
                'client_id': client_id,
                'next_step': 'initial_contact'
            }

        except Exception as e:
            logger.error(f"Failed to start onboarding: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def complete_step(self, client_id: str, step: str, data: dict) -> dict:
        """Mark an onboarding step as complete."""
        try:
            if client_id not in self.clients:
                return {
                    'status': 'error',
                    'message': 'Client not found'
                }

            if step not in self.onboarding_steps:
                return {
                    'status': 'error',
                    'message': 'Invalid step'
                }

            client = self.clients[client_id]
            
            # Complete the step
            client['completed_steps'][step] = {
                'completion_date': datetime.now().isoformat(),
                'data': data
            }
            
            # Remove from pending
            if step in client['pending_steps']:
                client['pending_steps'].remove(step)

            # Update current step
            if client['pending_steps']:
                next_step = min(
                    client['pending_steps'],
                    key=lambda x: self.onboarding_steps[x]['order']
                )
                client['current_step'] = next_step
            else:
                # All steps completed
                self._finalize_onboarding(client_id)

            # Save progress
            self._save_client_progress(client_id)

            logger.info(f"Completed step {step} for {client_id}")
            return {
                'status': 'success',
                'next_step': client['current_step']
            }

        except Exception as e:
            logger.error(f"Failed to complete step: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _finalize_onboarding(self, client_id: str):
        """Complete the onboarding process."""
        try:
            client = self.clients[client_id]
            
            # Get system configuration from completed steps
            system_config = {
                'backup_path': client['completed_steps']['backup_setup']['data']['backup_path'],
                'backup_schedule': client['completed_steps']['backup_setup']['data']['schedule'],
                'monitoring_config': client['completed_steps']['monitoring_setup']['data']
            }

            # Add client to integrated systems
            self.integrator.add_client(client_id, system_config)

            # Update client status
            client['status'] = 'active'
            client['completion_date'] = datetime.now().isoformat()

            # Generate final documentation
            self._generate_final_documentation(client_id)

            logger.info(f"Finalized onboarding for {client_id}")

        except Exception as e:
            logger.error(f"Failed to finalize onboarding: {str(e)}")
            raise

    def _create_client_directory(self, client_id: str):
        """Create directory structure for client files."""
        try:
            base_dir = f"clients/{client_id}"
            subdirs = ['docs', 'config', 'backups', 'monitoring']
            
            for subdir in subdirs:
                os.makedirs(f"{base_dir}/{subdir}", exist_ok=True)

        except Exception as e:
            logger.error(f"Failed to create client directory: {str(e)}")
            raise

    def _save_client_progress(self, client_id: str):
        """Save client onboarding progress."""
        try:
            client = self.clients[client_id]
            filename = f"clients/{client_id}/config/onboarding_progress.json"
            
            with open(filename, 'w') as f:
                json.dump(client, f, indent=4)

        except Exception as e:
            logger.error(f"Failed to save progress: {str(e)}")
            raise

    def _generate_final_documentation(self, client_id: str):
        """Generate final onboarding documentation."""
        try:
            client = self.clients[client_id]
            docs = {
                'client_info': client['info'],
                'system_config': {
                    'monitoring': client['completed_steps']['monitoring_setup']['data'],
                    'backup': client['completed_steps']['backup_setup']['data']
                },
                'completion_date': client['completion_date'],
                'service_agreement': client['completed_steps']['service_agreement']['data']
            }

            filename = f"clients/{client_id}/docs/final_setup.json"
            with open(filename, 'w') as f:
                json.dump(docs, f, indent=4)

        except Exception as e:
            logger.error(f"Failed to generate documentation: {str(e)}")
            raise

    def get_client_status(self, client_id: str) -> Optional[dict]:
        """Get current onboarding status for a client."""
        try:
            if client_id in self.clients:
                client = self.clients[client_id]
                return {
                    'status': client['status'],
                    'current_step': client['current_step'],
                    'completed_steps': list(client['completed_steps'].keys()),
                    'pending_steps': client['pending_steps']
                }
            return None

        except Exception as e:
            logger.error(f"Failed to get client status: {str(e)}")
            return None

    def add_note(self, client_id: str, note: str) -> bool:
        """Add a note to client onboarding record."""
        try:
            if client_id in self.clients:
                self.clients[client_id]['notes'].append({
                    'timestamp': datetime.now().isoformat(),
                    'note': note
                })
                self._save_client_progress(client_id)
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to add note: {str(e)}")
            return False

# Example usage:
if __name__ == "__main__":
    # Initialize onboarding system
    onboarding = ClientOnboarding()

    # Start onboarding for a test client
    client_info = {
        'business_name': 'Test Business',
        'contact_name': 'John Doe',
        'email': 'john@test.com',
        'phone': '555-0123'
    }
    
    result = onboarding.start_onboarding(client_info)
    
    if result['status'] == 'success':
        # Complete initial contact step
        onboarding.complete_step(
            result['client_id'],
            'initial_contact',
            {
                'meeting_date': '2024-12-22',
                'notes': 'Initial consultation completed'
            }
        )
