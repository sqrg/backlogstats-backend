from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.import_legacy import ParsedLegacyRow
from app.services.legacy_import import parse_legacy_xlsx

router = APIRouter(prefix="/import/legacy", tags=["import"])

_MAX_BYTES = 10 * 1024 * 1024  # 10 MB cap; the real file is ~150 KB


@router.post("/parse", response_model=list[ParsedLegacyRow])
async def parse_legacy_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> list[ParsedLegacyRow]:
    raw = await file.read()
    if len(raw) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        rows = parse_legacy_xlsx(raw)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse xlsx: {exc}",
        )

    return [ParsedLegacyRow(**row) for row in rows]
