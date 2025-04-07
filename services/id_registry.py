# ID management service
import random
import string

class IDRegistry:
    """Service for generating and tracking IDs for XML entities."""
    
    def __init__(self):
        self.id_map = {}  # Tracks IDs by entity type
        self.relationship_map = {}  # Tracks parent-child relationships
    
    def generate_id(self, entity_type, length=6):
        """Generate a unique ID for an entity type."""
        # Create a unique random ID
        chars = string.ascii_letters + string.digits
        new_id = ''.join(random.choice(chars) for _ in range(length))
        
        # Ensure uniqueness
        while self._id_exists(new_id):
            new_id = ''.join(random.choice(chars) for _ in range(length))
        
        # Register the ID
        if entity_type not in self.id_map:
            self.id_map[entity_type] = []
        self.id_map[entity_type].append(new_id)
        
        return new_id
    
    def _id_exists(self, id_to_check):
        """Check if an ID already exists in any entity type."""
        for ids in self.id_map.values():
            if id_to_check in ids:
                return True
        return False
    
    def register_relationship(self, parent_type, parent_id, child_type, child_id):
        """Register a relationship between two entities."""
        key = (parent_type, parent_id, child_type)
        if key not in self.relationship_map:
            self.relationship_map[key] = []
        self.relationship_map[key].append(child_id)
    
    def get_children(self, parent_type, parent_id, child_type):
        """Get all children of a specific type for a parent."""
        key = (parent_type, parent_id, child_type)
        return self.relationship_map.get(key, [])
    
    def validate_references(self):
        """Validate all entity references."""
        # Implementation would check each relationship against registered IDs
        # Returns list of validation errors, if any
        pass