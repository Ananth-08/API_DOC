def detect_crud_gaps(endpoints: list) -> list:
    """
    Extracts unique base resources from route paths and detects any missing 
    standard CRUD operations (GET/list, GET/detail, POST, PUT, DELETE) for them.

    Args:
        endpoints (list): A list of endpoint dictionaries, each having 
                          "method" and "route" keys.

    Returns:
        list: A list of missing CRUD endpoint dictionaries with "method", 
              "route", and "reason" keys.
    """
    # Set of common API prefixes to skip when identifying the base resource
    common_prefixes = {"api", "v1", "v2", "v3", "v4", "version"}

    # Dictionary to keep track of base resources: base_resource_route -> resource_name
    base_routes = {}

    # Set to store existing endpoints as (method, normalized_route)
    existing_endpoints = set()

    for ep in endpoints:
        method = ep.get("method", "").upper()
        route = ep.get("route", "").strip()
        if not route or not method:
            continue

        # Split the route by '/' to inspect segments
        parts = [p for p in route.split("/") if p]
        if not parts:
            continue

        # Find the index of the base resource by skipping common API prefixes
        resource_idx = 0
        while resource_idx < len(parts) - 1 and parts[resource_idx] in common_prefixes:
            resource_idx += 1

        resource_name = parts[resource_idx]
        base_route_parts = parts[:resource_idx + 1]
        base_route = "/" + "/".join(base_route_parts)
        base_routes[base_route] = resource_name

        # Normalize the route: replace any parameter segment after the base resource with '{id}'
        normalized_parts = list(base_route_parts)
        remaining_parts = parts[resource_idx + 1:]
        for part in remaining_parts:
            if part.startswith('{') and part.endswith('}'):
                normalized_parts.append('{id}')
            else:
                normalized_parts.append(part)

        normalized_route = "/" + "/".join(normalized_parts)
        existing_endpoints.add((method, normalized_route))

    missing_endpoints = []

    # Check for missing CRUD operations for each base resource route
    for base_route in sorted(base_routes.keys()):
        required_ops = [
            ("GET", base_route),                # List collection
            ("GET", f"{base_route}/{{id}}"),    # Get detail
            ("POST", base_route),               # Create
            ("PUT", f"{base_route}/{{id}}"),    # Update
            ("DELETE", f"{base_route}/{{id}}")  # Delete
        ]

        for method, route in required_ops:
            if (method, route) not in existing_endpoints:
                missing_endpoints.append({
                    "method": method,
                    "route": route,
                    "reason": "Missing CRUD operation"
                })

    return missing_endpoints


if __name__ == "__main__":
    # Example input endpoints
    sample_endpoints = [
        # Users resource has partial CRUD operations
        {"method": "GET", "route": "/users"},
        {"method": "POST", "route": "/users"},
        {"method": "GET", "route": "/users/{id}"},
        {"method": "DELETE", "route": "/users/{userId}"},  # Different parameter name, should normalize
        
        # Orders resource has only GET list and POST
        {"method": "GET", "route": "/api/v1/orders"},
        {"method": "POST", "route": "/api/v1/orders"},
        
        # Products resource has full CRUD operations
        {"method": "GET", "route": "/products"},
        {"method": "GET", "route": "/products/{id}"},
        {"method": "POST", "route": "/products"},
        {"method": "PUT", "route": "/products/{id}"},
        {"method": "DELETE", "route": "/products/{id}"},
    ]

    print("Analyzing endpoints for CRUD gaps...")
    gaps = detect_crud_gaps(sample_endpoints)
    
    print(f"\nFound {len(gaps)} missing CRUD operations:")
    for gap in gaps:
        print(f" - {gap['method']} {gap['route']} ({gap['reason']})")
