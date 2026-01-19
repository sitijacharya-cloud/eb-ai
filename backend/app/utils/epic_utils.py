"""Utility functions for epic processing."""


def is_similar_epic_name(name1: str, name2: str) -> bool:
    """
    Check if two epic names are semantically similar to avoid duplicates.
    
    Examples:
    
    - "User Profile" and "Profile Management" -> Similar
    - "Payment" and "Payment Gateway" -> Similar
    - "Authentication" and "MT - Authentication" -> Similar
    - "MT - Database Design" and "Database Design" -> Similar
    
    Args:
        name1: First epic name
        name2: Second epic name
        
    Returns:
        True if epics are semantically similar, False otherwise
    """
    # Normalize names: lowercase, remove common words and prefixes
    common_words = {"and", "the", "a", "an", "my", "mt"}
    common_prefixes = ["mt -", "mt-", "mt ", "ma -", "ma-", "ma "]
    
    def normalize(name: str) -> set:
        # Convert to lowercase
        name_lower = name.lower().strip()
        
        # Remove common prefixes (MT -, MA -, etc.)
        for prefix in common_prefixes:
            if name_lower.startswith(prefix):
                name_lower = name_lower[len(prefix):].strip()
                break
        
        # Split into words
        words = set(name_lower.replace("-", " ").replace("  ", " ").split())
        
        # Remove common words but keep the core terms
        core_words = words - common_words
        return core_words if core_words else words  # Keep original if all words are common
    
    words1 = normalize(name1)
    words2 = normalize(name2)
    
    # Check for significant overlap
    if not words1 or not words2:
        return False
    
    intersection = words1 & words2
    smaller_set = min(len(words1), len(words2))
    
    # If 50% or more words overlap, consider them similar
    overlap_ratio = len(intersection) / smaller_set if smaller_set > 0 else 0
    
    return overlap_ratio >= 0.8
