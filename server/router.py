from fastapi import APIRouter
from .models import Challenge

router = APIRouter()


@router.post("/challenge")
async def challenge(challenge: Challenge):
    return {'Challenge received OK'}
