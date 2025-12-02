from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import httpx

router = APIRouter(prefix="/hr", tags=["hr"])
HR_SERVICE_URL = os.getenv("HR_SERVICE_URL", "http://clio-hr-backend:3000")
client = httpx.AsyncClient(base_url=HR_SERVICE_URL, timeout=60.0)

class QuestionnairePayload(BaseModel):
    userId: str
    answers: dict

class TeamPayload(BaseModel):
    name: str
    memberIds: list[str]

class RiskPayload(BaseModel):
    teamId: str


@router.post("/questionnaire/submit")
async def submit_questionnaire(payload: QuestionnairePayload):
    resp = await client.post("/api/questionnaire/submit", json=payload.dict())
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@router.post("/teams/create")
async def create_team(payload: TeamPayload):
    resp = await client.post("/api/teams/create", json=payload.dict())
    if resp.status_code != 201:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@router.post("/risks/evaluate")
async def evaluate_risks(payload: RiskPayload):
    resp = await client.get(f"/api/risks/evaluate?teamId={payload.teamId}")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@router.get("/health")
async def hr_health():
    resp = await client.get("/health")
    if resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return resp.json()
