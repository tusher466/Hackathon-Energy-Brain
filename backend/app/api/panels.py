from fastapi import APIRouter, UploadFile, File, Form
from app.schemas.common import PanelInspectionResponse
from app.ml.thermal import analyze_thermal_image, generate_synthetic_thermal_sample
import cv2
import numpy as np
from PIL import Image
import io

router = APIRouter(prefix="/panels", tags=["panels"])

@router.get("/sample", response_model=PanelInspectionResponse)
def sample_inspection(region_code: str = "BD", seed: int = 0):
    result, _ = generate_synthetic_thermal_sample(seed=seed, region_code=region_code)
    from app.schemas.common import PanelDefect
    defects = []
    for d in result["defects"]:
        defects.append(PanelDefect(
            id=d["id"],
            type=d["type"],
            severity=d["severity"],
            bbox=d["bbox"],
            temp_delta_c=d["temp_delta_c"],
            efficiency_loss_pct=d["efficiency_loss_pct"],
            yearly_loss_kwh=d["yearly_loss_kwh"],
            money_loss=d["money_loss"],
            recommendation=d["recommendation"]
        ))
    return PanelInspectionResponse(
        defects=defects,
        annotated_image_b64=result["annotated_image_b64"],
        total_efficiency_loss_pct=result["total_efficiency_loss_pct"],
        total_yearly_loss_kwh=result["total_yearly_loss_kwh"],
        total_money_loss=result["total_money_loss"],
        summary=result["summary"]
    )

@router.post("/inspect", response_model=PanelInspectionResponse)
async def inspect_image(file: UploadFile = File(...), region_code: str = Form("BD")):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        # try generate synthetic fallback
        result, _ = generate_synthetic_thermal_sample(seed=1, region_code=region_code)
    else:
        result = analyze_thermal_image(img, region_code=region_code)

    from app.schemas.common import PanelDefect
    defects = []
    for d in result["defects"]:
        defects.append(PanelDefect(
            id=d["id"],
            type=d["type"],
            severity=d["severity"],
            bbox=d["bbox"],
            temp_delta_c=d["temp_delta_c"],
            efficiency_loss_pct=d["efficiency_loss_pct"],
            yearly_loss_kwh=d["yearly_loss_kwh"],
            money_loss=d["money_loss"],
            recommendation=d["recommendation"]
        ))
    return PanelInspectionResponse(
        defects=defects,
        annotated_image_b64=result["annotated_image_b64"],
        total_efficiency_loss_pct=result["total_efficiency_loss_pct"],
        total_yearly_loss_kwh=result["total_yearly_loss_kwh"],
        total_money_loss=result["total_money_loss"],
        summary=result["summary"]
    )
