from __future__ import annotations
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

from schemas.concept import ConceptResponse
from schemas.property import PropertyResponse


class PropertiesConceptsBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "concept_id": 1,
                    "property_id": 1,
                    "enabled": True,
                }
            ]
        },
    )

    concept_id: Annotated[
        int,
        Field(
            ge=1,
            description="Id of the concept that is being related to the property_id",
        ),
    ]
    property_id: Annotated[
        int,
        Field(
            ge=1,
            description="Id of the property that is being related to the concept_id",
        ),
    ]
    enabled: Annotated[
        bool,
        Field(
            description="True if the concept is currently being applicable to the property"
        ),
    ]


class CreatePropertiesConcepts(PropertiesConceptsBase):
    pass


class UpdatePropertiesConcepts(PropertiesConceptsBase):
    pass


class PropertiesConceptsResponse(PropertiesConceptsBase):
    id: Annotated[
        int, Field(ge=1, description="Unique identifier assigned by the system")
    ]
    concept: ConceptResponse | None
    property: PropertyResponse | None
