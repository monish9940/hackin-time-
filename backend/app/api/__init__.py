from fastapi import APIRouter

from .auth import router as auth_router
from .patients import router as patients_router
from .documents import router as documents_router
from .ai import router as ai_router
from .timeline import router as timeline_router
from .medications import router as medications_router
from .notes import router as notes_router
from .audit import router as audit_router
from .export import router as export_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(timeline_router, prefix="/patients/timeline", tags=["timeline"])
api_router.include_router(medications_router, prefix="/patients/medications", tags=["medications"])
api_router.include_router(notes_router, prefix="/patients/notes", tags=["notes"])
api_router.include_router(patients_router, prefix="/patients", tags=["patients"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(audit_router, prefix="/audit", tags=["audit"])
api_router.include_router(export_router, prefix="/export", tags=["export"])

