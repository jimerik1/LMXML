# services/id_registry.py
class IDRegistry:
    """
    Service for generating and tracking IDs for XML entities.
    
    This registry maintains unique IDs across different entity types and tracks
    relationships between entities to ensure referential integrity in the XML.
    """
    
    def __init__(self):
        self.id_map = {}  # Maps entity types to lists of IDs
        self.relationship_map = {}  # Maps parent-child relationships
        self.entity_data = {}  # Stores additional data for each entity
    
    def generate_id(self, entity_type, length=6, prefix=None):
        """
        Generate a unique ID for an entity type with optional prefix.
        
        Args:
            entity_type (str): Type of entity (e.g., 'ASSEMBLY', 'COMPONENT')
            length (int): Length of the random part of the ID
            prefix (str, optional): Optional prefix for the ID
            
        Returns:
            str: A unique ID
        """
        import random
        import string
        
        # Create a unique random ID
        chars = string.ascii_letters + string.digits
        random_part = ''.join(random.choice(chars) for _ in range(length))
        
        # Add prefix if provided
        new_id = f"{prefix}{random_part}" if prefix else random_part
        
        # Ensure uniqueness
        while self._id_exists(new_id):
            random_part = ''.join(random.choice(chars) for _ in range(length))
            new_id = f"{prefix}{random_part}" if prefix else random_part
        
        # Register the ID
        if entity_type not in self.id_map:
            self.id_map[entity_type] = []
        self.id_map[entity_type].append(new_id)
        
        return new_id
    
    def register_entity(self, entity_type, entity_id, data=None):
        """
        Register an entity with optional additional data.
        
        Args:
            entity_type (str): Type of entity
            entity_id (str): ID of the entity
            data (dict, optional): Additional data for the entity
        """
        if entity_type not in self.id_map:
            self.id_map[entity_type] = []
        
        if entity_id not in self.id_map[entity_type]:
            self.id_map[entity_type].append(entity_id)
        
        if data:
            self.entity_data[(entity_type, entity_id)] = data
    
    def get_entity_data(self, entity_type, entity_id):
        """
        Get the data associated with an entity.
        
        Args:
            entity_type (str): Type of entity
            entity_id (str): ID of the entity
            
        Returns:
            dict: Data associated with the entity or None
        """
        return self.entity_data.get((entity_type, entity_id))
    
    def _id_exists(self, id_to_check):
        """
        Check if an ID already exists in any entity type.
        
        Args:
            id_to_check (str): ID to check
            
        Returns:
            bool: True if the ID exists, False otherwise
        """
        for ids in self.id_map.values():
            if id_to_check in ids:
                return True
        return False
    
    def register_relationship(self, parent_type, parent_id, child_type, child_id):
        """
        Register a relationship between two entities.
        
        Args:
            parent_type (str): Type of parent entity
            parent_id (str): ID of parent entity
            child_type (str): Type of child entity
            child_id (str): ID of child entity
        """
        key = (parent_type, parent_id, child_type)
        if key not in self.relationship_map:
            self.relationship_map[key] = []
        self.relationship_map[key].append(child_id)
    
    def get_children(self, parent_type, parent_id, child_type):
        """
        Get all children of a specific type for a parent.
        
        Args:
            parent_type (str): Type of parent entity
            parent_id (str): ID of parent entity
            child_type (str): Type of child entity
            
        Returns:
            list: List of child IDs
        """
        key = (parent_type, parent_id, child_type)
        return self.relationship_map.get(key, [])
    
    def validate_references(self):
        """
        Validate all entity references to ensure referential integrity.
        
        Returns:
            list: List of validation errors, if any
        """
        errors = []
        
        # Check that all referenced IDs exist
        for (parent_type, parent_id, child_type), child_ids in self.relationship_map.items():
            # Verify parent exists
            if parent_id not in self.id_map.get(parent_type, []):
                errors.append(f"Referenced parent entity {parent_type}:{parent_id} does not exist")
            
            # Verify children exist
            for child_id in child_ids:
                if child_id not in self.id_map.get(child_type, []):
                    errors.append(f"Referenced child entity {child_type}:{child_id} does not exist")
        
        return errors