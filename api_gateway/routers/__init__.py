"""
API Gateway routers module.
Aggregates all service routers.
"""
from fastapi import APIRouter

from . import finance, hr, marketing, linkedin, crm, calls, social_x, superloop

# Main API router that aggregates all service routers
router = APIRouter()

# Include all service routers
router.include_router(finance.router)
router.include_router(hr.router)
router.include_router(marketing.router)
router.include_router(linkedin.router)
router.include_router(crm.router)
router.include_router(calls.router)
router.include_router(social_x.router)
router.include_router(superloop.router)
