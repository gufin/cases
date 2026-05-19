from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BillingUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    keycloak_sub: str = Field(alias="keycloakSub")
    plan: str
    cases_limit: int = Field(alias="casesLimit")
    subscription_ends_at: datetime | None = Field(default=None, alias="subscriptionEndsAt")
