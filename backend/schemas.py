from typing import List
from pydantic import BaseModel, Field

class Endpoint(BaseModel):
    """
    Represents an API endpoint.
    """
    method: str = Field(
        ..., 
        description="The HTTP method of the endpoint (e.g., GET, POST, PUT, DELETE, PATCH)"
    )
    route: str = Field(
        ..., 
        description="The URL route pattern of the endpoint (e.g., /users/{id})"
    )
    description: str = Field(
        ..., 
        description="A brief description of what the endpoint does"
    )
    auth_required: bool = Field(
        ..., 
        description="Indicates if authentication is required to access the endpoint"
    )

class GapResult(BaseModel):
    """
    Represents a identified gap in the API or system.
    """
    method: str = Field(
        ..., 
        description="The HTTP method associated with the gap"
    )
    route: str = Field(
        ..., 
        description="The route path associated with the gap"
    )
    reason: str = Field(
        ..., 
        description="The explanation of why this gap was identified"
    )

class ResourceRelationship(BaseModel):
    """
    Represents a relationship between two system resources.
    """
    parent: str = Field(
        ..., 
        description="The parent resource name"
    )
    child: str = Field(
        ..., 
        description="The child resource name"
    )
    relationship_type: str = Field(
        ..., 
        description="The type of relationship between parent and child"
    )

class Violation(BaseModel):
    """
    Represents a REST API design violation.
    """
    route: str = Field(..., description="The route associated with the violation")
    method: str = Field(..., description="The HTTP method associated with the violation")
    violation: str = Field(..., description="Description of the violation")
    suggestion: str = Field(..., description="How to fix the violation")

class PromptRequest(BaseModel):
    """
    The request payload containing the design prompt.
    """
    prompt: str = Field(..., min_length=1, description="The design description prompt")

class GenerateResponse(BaseModel):
    """
    The structured response wrapping endpoints, gaps, violations, relationships, and a summary.
    """
    endpoints: List[Endpoint] = Field(
        ..., 
        description="A list of defined API endpoints"
    )
    gaps: List[GapResult] = Field(
        ..., 
        description="A list of identified gaps"
    )
    violations: List[Violation] = Field(
        ...,
        description="A list of REST API convention violations"
    )
    relationships: List[ResourceRelationship] = Field(
        ..., 
        description="A list of relationships between resources"
    )
    summary: str = Field(
        ..., 
        description="A high-level summary of the generated schema/report"
    )

