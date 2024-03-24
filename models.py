from pydantic import BaseModel

# 각 항목별 모델 정의
class AttractivePowerItem(BaseModel):
    element1: str
    element2: int
    element3: float
    element4: bool
    element5: str

class DensityItem(BaseModel):
    element1: str
    element2: int
    element3: float
    element4: bool
    element5: str

class GrowthPotentialItem(BaseModel):
    element1: str
    element2: int
    element3: float
    element4: bool
    element5: str

class PurchasingPowerItem(BaseModel):
    element1: str
    element2: int
    element3: float
    element4: bool
    element5: str

class StabilityItem(BaseModel):
    element1: str
    element2: int
    element3: float
    element4: bool
    element5: str

# 상위 모델 정의
class EvaluationData(BaseModel):
    business_id: int
    attractive_power: AttractivePowerItem
    density: DensityItem
    growth_potential: GrowthPotentialItem
    purchasing_power: PurchasingPowerItem
    stability: StabilityItem