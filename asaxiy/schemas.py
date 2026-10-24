from pydantic import BaseModel, Field, model_validator

class KategoriyaKirish(BaseModel):
    nomi: str = Field(min_length=2)
    tavsifi: str | None = None

class MahsulotKirish(BaseModel):
    kategoriya_id: int = Field(gt=0)
    nomi: str = Field(min_length=2)
    tavsifi: str | None = None
    narxi: int = Field(gt=0)
    ombor_qoldigi: int = Field(ge=0)

class MahsulotYangilash(BaseModel):
    nomi: str | None = Field(default=None, min_length=2)
    tavsifi: str | None = None
    narxi: int | None = Field(default=None, gt=0)
    ombor_qoldigi: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def majburiy_ustunlar_bosh_bolmasin(self):
        for nom in ("nomi", "narxi", "ombor_qoldigi"):
            if nom in self.model_fields_set and getattr(self, nom) is None:
                raise ValueError(f"{nom} bo‘sh bo‘lishi mumkin emas")
        return self

class SavatQatori(BaseModel):
    mahsulot_id: int = Field(gt=0)
    soni: int = Field(gt=0)

class BuyurtmaSorovi(BaseModel):
    mijoz_id: int = Field(gt=0)
    qatorlar: list[SavatQatori] = Field(min_length=1)

class MijozKirish(BaseModel):
    ism: str = Field(min_length=2)
    familiya: str = Field(min_length=2)
    telefon: str = Field(min_length=7)
    manzil: str = Field(min_length=3)
