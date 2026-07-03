def lint_endpoints(endpoints: list) -> list:
    """
    Checks each endpoint against standard REST design rules.

    Rules:
    1. Routes must use plural nouns (e.g., /users not /user)
    2. No verbs in routes (e.g., /users not /getUsers or /fetchUsers)
    3. GET requests must never have "create/update/delete" in description
    4. PUT/PATCH must have {id} in route
    5. DELETE must have {id} in route
    6. Routes must start with '/'
    7. Methods must be uppercase

    Args:
        endpoints (list): List of endpoint dictionaries containing:
                          - "method" (str)
                          - "route" (str)
                          - "description" (str, optional)

    Returns:
        list: List of violation dictionaries with keys:
              "route", "method", "violation", "suggestion".
    """
    violations = []
    
    # Common API prefixes and words that are accepted as plurals/uncountables
    common_prefixes = {"api", "v1", "v2", "v3", "v4", "version"}
    uncountables = {"data", "media", "info", "information", "health", "metrics", "meta", "metadata", "status"}
    
    # Verbs commonly found in anti-pattern routes
    verbs = {
        "get", "post", "put", "delete", "patch", "create", 
        "add", "update", "remove", "fetch", "list", "show", 
        "find", "search", "insert", "clear"
    }

    def is_plural(word: str) -> bool:
        w = word.lower()
        if w in uncountables:
            return True
        # Ends with 's' but not 'ss' (like address, class, status)
        if w.endswith('s') and not w.endswith('ss'):
            return True
        return False

    def pluralize(word: str) -> str:
        w = word.lower()
        if w.endswith('y') and not w.endswith(('ay', 'ey', 'iy', 'oy', 'uy')):
            return word[:-1] + 'ies'
        elif w.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return word + 'es'
        else:
            return word + 's'

    def get_verb_in_segment(segment: str) -> str:
        # Normalize and split segment to check for embedded verbs
        # Handle snake_case, kebab-case, and camelCase
        s_lower = segment.lower()
        parts = s_lower.replace('-', '_').split('_')
        
        # Convert camelCase to snake_case equivalent in parts list
        camel_parts = []
        for i, char in enumerate(segment):
            if char.isupper() and i > 0:
                camel_parts.append('_' + char.lower())
            else:
                camel_parts.append(char.lower())
        camel_str = "".join(camel_parts)
        parts.extend(camel_str.replace('-', '_').split('_'))
        
        for p in parts:
            if p in verbs:
                return p
        return ""

    for ep in endpoints:
        original_route = ep.get("route", "")
        original_method = ep.get("method", "")
        description = ep.get("description", "") or ""
        
        route = original_route.strip()
        method = original_method.strip()

        # Rule 6: Routes must start with /
        if not route.startswith('/'):
            violations.append({
                "route": original_route,
                "method": original_method,
                "violation": "Route does not start with a forward slash '/'",
                "suggestion": f"Prepend '/' to the route path (e.g., '/{route}')"
            })

        # Rule 7: Methods must be uppercase
        if method != method.upper() or not method:
            violations.append({
                "route": original_route,
                "method": original_method,
                "violation": f"HTTP method '{original_method}' is not uppercase",
                "suggestion": f"Change HTTP method to uppercase '{method.upper()}'"
            })

        # Standardize method for checks
        method_upper = method.upper()

        # Rule 3: GET requests must never have "create/update/delete" in description
        if method_upper == "GET" and description:
            desc_lower = description.lower()
            for action in ["create", "update", "delete"]:
                if action in desc_lower:
                    violations.append({
                        "route": original_route,
                        "method": original_method,
                        "violation": f"GET request description contains action-oriented word '{action}'",
                        "suggestion": f"Remove '{action}' from description or change HTTP method to POST/PUT/DELETE if it modifies data"
                    })

        # Rule 4: PUT/PATCH must have {id} in route
        if method_upper in ("PUT", "PATCH"):
            if "{id}" not in route.lower():
                violations.append({
                    "route": original_route,
                    "method": original_method,
                    "violation": f"{method_upper} request route is missing the '{{id}}' identifier parameter segment",
                    "suggestion": f"Add '{{id}}' parameter to the end of the route or replace current identifier (e.g., '{route}/{{id}}')"
                })

        # Rule 5: DELETE must have {id} in route
        if method_upper == "DELETE":
            if "{id}" not in route.lower():
                violations.append({
                    "route": original_route,
                    "method": original_method,
                    "violation": "DELETE request route is missing the '{id}' identifier parameter segment",
                    "suggestion": f"Add '{{id}}' parameter to the end of the route or replace current identifier (e.g., '{route}/{{id}}')"
                })

        # Inspect route segments for plural nouns and verb checks
        segments = [s for s in route.split('/') if s]
        for seg in segments:
            # Skip placeholders/parameters
            if seg.startswith('{') and seg.endswith('}'):
                continue
            # Skip common API prefixes
            if seg.lower() in common_prefixes:
                continue

            # Rule 1: Routes must use plural nouns
            if not is_plural(seg):
                violations.append({
                    "route": original_route,
                    "method": original_method,
                    "violation": f"Route segment '{seg}' is a singular noun",
                    "suggestion": f"Pluralize the segment to '{pluralize(seg)}'"
                })

            # Rule 2: No verbs in routes
            verb_found = get_verb_in_segment(seg)
            if verb_found:
                violations.append({
                    "route": original_route,
                    "method": original_method,
                    "violation": f"Route segment '{seg}' contains verb '{verb_found}'",
                    "suggestion": f"Remove the action verb '{verb_found}' from the route path and use HTTP methods to imply action"
                })

    return violations


if __name__ == "__main__":
    # Test cases representing various violations
    sample_endpoints = [
        {
            "method": "get", 
            "route": "users", 
            "description": "Get users list"
        },  # Violations: No leading slash, lowercase method
        {
            "method": "GET", 
            "route": "/user", 
            "description": "Get a single user"
        },  # Violation: Singular noun '/user'
        {
            "method": "GET", 
            "route": "/users/fetchActive", 
            "description": "Fetch active users"
        },  # Violation: Verb 'fetch' in route
        {
            "method": "GET", 
            "route": "/users", 
            "description": "Create a new user"
        },  # Violation: GET description contains 'create'
        {
            "method": "PUT", 
            "route": "/users", 
            "description": "Update user"
        },  # Violation: PUT missing '{id}' in route
        {
            "method": "DELETE", 
            "route": "/users/{userId}", 
            "description": "Delete user"
        },  # Violation: DELETE missing '{id}' literal parameter in route
        {
            "method": "GET", 
            "route": "/api/v1/users/{id}", 
            "description": "Get user by ID"
        }   # Valid endpoint
    ]
    
    print("Running REST Linter verification...")
    violations = lint_endpoints(sample_endpoints)
    print(f"\nFound {len(violations)} REST API violations:")
    for i, v in enumerate(violations, 1):
        print(f"\nViolation #{i}:")
        print(f"  Endpoint:   {v['method']} {v['route']}")
        print(f"  Violation:  {v['violation']}")
        print(f"  Suggestion: {v['suggestion']}")
