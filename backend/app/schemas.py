from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field



class DependencyEdgeIn(BaseModel):
    downstream_bot_name: str = Field(min_length=1, max_length=120)
    data_field: str = Field(min_length=1, max_length=120)
    criticality: str = Field(pattern="^(hard|soft)$")




class BotRegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=10, max_length=4000)




class BotOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    patient_impact_level: int
    patient_impact_score: float
    pis_reasoning: str | None
    automation_debt_score: float
    last_tested_at: datetime | None
    last_test_result: str | None
    registered_at: datetime



class FleetOut(BaseModel):
    hospital: str
    bot_count: int
    bots: list[BotOut]




class TestRunOut(BaseModel):
    id: UUID
    bot_id: UUID
    status: str
    uipath_execution_id: str | None
    detail: str | None
    started_at: datetime
    finished_at: datetime | None


class WsTicketOut(BaseModel):
    ticket: str
    expires_in: int




class BlastNode(BaseModel):
    id: UUID
    name: str
    level: int
    pis: float
    depth: int
    volume: int



class BlastEdge(BaseModel):
    src: UUID
    dst: UUID
    field: str
    criticality: str


class BlastSummary(BaseModel):
    affected_bots: int
    aggregate_pis: float
    patient_volume_24h: int
    max_depth: int


class BlastRadiusOut(BaseModel):
    origin: BlastNode
    nodes: list[BlastNode]
    edges: list[BlastEdge]
    summary: BlastSummary
    generated_at: str