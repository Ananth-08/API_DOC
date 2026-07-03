def detect_relationships(endpoints: list) -> list:
    """
    Analyzes a list of endpoint configurations to discover relationships 
    between different resources using route structure and parameter names.

    Discovers two types of patterns:
    1. Nested routes (e.g., /users/{id}/orders -> User has many Orders)
    2. Foreign key parameters (e.g., /orders/{userId} -> User has many Orders)

    Args:
        endpoints (list): List of endpoint dictionaries containing "route".

    Returns:
        list: List of relationship dictionaries with keys:
              "parent", "child", "relationship_type".
    """
    relationships = set()
    common_prefixes = {"api", "v1", "v2", "v3", "v4", "version"}

    def pluralize(word: str) -> str:
        w = word.lower()
        uncountables = {"data", "media", "info", "information", "health", "metrics", "meta", "metadata", "status"}
        if w in uncountables:
            return w
        if w.endswith('y') and not w.endswith(('ay', 'ey', 'iy', 'oy', 'uy')):
            return word[:-1] + 'ies'
        elif w.endswith(('s', 'sh', 'ch', 'x', 'z')):
            if w.endswith('ss'):
                return word + 'es'
            return word
        else:
            return word + 's'

    def get_base_resource(route: str) -> str:
        parts = [p for p in route.split('/') if p]
        if not parts:
            return ""
        idx = 0
        while idx < len(parts) - 1 and parts[idx] in common_prefixes:
            idx += 1
        segment = parts[idx]
        if segment.startswith('{') and segment.endswith('}'):
            return ""
        return segment

    for ep in endpoints:
        route = ep.get("route", "").strip()
        if not route:
            continue
            
        parts = [p for p in route.split('/') if p]
        if not parts:
            continue

        # Pattern 1: Nested routes (e.g. /users/{id}/orders)
        for i in range(1, len(parts) - 1):
            seg = parts[i]
            if seg.startswith('{') and seg.endswith('}'):
                parent_candidate = parts[i-1]
                child_candidate = parts[i+1]
                
                # Skip if either candidate is a parameter placeholder or prefix
                if (parent_candidate.startswith('{') or 
                    parent_candidate.lower() in common_prefixes or
                    child_candidate.startswith('{') or 
                    child_candidate.lower() in common_prefixes):
                    continue
                    
                parent = pluralize(parent_candidate)
                child = pluralize(child_candidate)
                
                if parent != child:
                    relationships.add((parent, child, "one-to-many"))

        # Pattern 2: Foreign key parameters in route structure (e.g. /orders/{userId})
        current_resource_candidate = get_base_resource(route)
        if current_resource_candidate:
            child = pluralize(current_resource_candidate)
            
            for seg in parts:
                if seg.startswith('{') and seg.endswith('}'):
                    param_name = seg[1:-1].strip()
                    var_name = param_name.lower()
                    
                    # Extract the referenced parent resource name by stripping ID suffixes
                    if var_name.endswith('_id'):
                        ref_resource = var_name[:-3]
                    elif var_name.endswith('-id'):
                        ref_resource = var_name[:-3]
                    elif var_name.endswith('id') and len(var_name) > 2:
                        ref_resource = var_name[:-2]
                    else:
                        ref_resource = var_name
                        
                    if ref_resource and ref_resource != "id":
                        parent = pluralize(ref_resource)
                        if parent != child:
                            relationships.add((parent, child, "one-to-many"))

    # Sort the relationships for deterministic output
    sorted_relations = sorted(list(relationships))
    return [
        {"parent": parent, "child": child, "relationship_type": rel_type}
        for parent, child, rel_type in sorted_relations
    ]


if __name__ == "__main__":
    # Test cases representing nested routes and foreign keys
    sample_endpoints = [
        # Nested route pattern
        {"route": "/users/{id}/orders"},
        {"route": "/api/v1/users/{userId}/posts"},
        
        # Foreign key pattern
        {"route": "/orders/{userId}"},
        {"route": "/comments/{post_id}"},
        
        # Standard endpoints (should not generate false relationships)
        {"route": "/users/{id}"},
        {"route": "/orders/{id}"},
        {"route": "/products/{productId}"}
    ]

    print("Detecting resource relationships from routes...")
    relations = detect_relationships(sample_endpoints)
    print(f"\nDiscovered {len(relations)} relationships:")
    for r in relations:
        print(f" - {r['parent']} -> {r['child']} ({r['relationship_type']})")
