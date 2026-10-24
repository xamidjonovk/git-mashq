from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Identity, Text, func, CheckConstraint, ForeignKey, UniqueConstraint
from sqlmodel import Field, SQLModel, Relationship  # ORM


class Kategoriya(SQLModel, table=True):
    __tablename__ = "kategoriyalar"

    id: int | None = Field(
        default=None, sa_column=Column(BigInteger, Identity(), primary_key=True)
    )
    nomi: str = Field(sa_column=Column(Text, nullable=False, unique=True))
    tavsifi: str | None = Field(default=None, sa_column=Column(Text))
    yaratilgan_sana: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )


class Mahsulot(SQLModel, table=True):
    __tablename__ = "mahsulotlar"
    __table_args__ = (
        CheckConstraint("narxi > 0"),
        CheckConstraint("ombor_qoldigi >= 0"),
    )

    id: int | None = Field(
        default=None, sa_column=Column(BigInteger, Identity(), primary_key=True)
    )
    kategoriya_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("kategoriyalar.id"), nullable=False)
    )
    nomi: str = Field(sa_column=Column(Text, nullable=False))
    tavsifi: str | None = Field(default=None, sa_column=Column(Text))
    narxi: int = Field(sa_column=Column(BigInteger, nullable=False))
    ombor_qoldigi: int = Field(
        default=0, sa_column=Column(BigInteger, nullable=False, server_default="0")
    )
    yaratilgan_sana: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )

    buyurtma_qatorlari: list["BuyurtmaQatori"] = Relationship(back_populates="mahsulot")


class Mijoz(SQLModel, table=True):
    __tablename__ = "mijozlar"

    id: int | None = Field(default=None, sa_column=Column(BigInteger, Identity(), primary_key=True))
    ism: str = Field(sa_column=Column(Text, nullable=False))
    familiya: str = Field(sa_column=Column(Text, nullable=False))
    telefon: str = Field(sa_column=Column(Text, nullable=False, unique=True))
    manzil: str = Field(sa_column=Column(Text, nullable=False))
    royxatdan_otgan_sana: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )
    buyurtmalar: list["Buyurtma"] = Relationship(back_populates="mijoz")


class Buyurtma(SQLModel, table=True):
    __tablename__ = "buyurtmalar"
    __table_args__ = (CheckConstraint("umumiy_summa >= 0"),)

    id: int | None = Field(default=None, sa_column=Column(BigInteger, Identity(), primary_key=True))
    mijoz_id: int = Field(sa_column=Column(BigInteger, ForeignKey("mijozlar.id"), nullable=False))
    umumiy_summa: int = Field(
        default=0, sa_column=Column(BigInteger, nullable=False, server_default="0")
    )
    holati: str = Field(
        default="yangi", sa_column=Column(Text, nullable=False, server_default="yangi")
    )
    buyurtma_sanasi: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )
    mijoz: Mijoz | None = Relationship(back_populates="buyurtmalar")
    qatorlar: list["BuyurtmaQatori"] = Relationship(back_populates="buyurtma")


class BuyurtmaQatori(SQLModel, table=True):
    __tablename__ = "buyurtma_tarkibi"
    __table_args__ = (
        CheckConstraint("soni > 0"),
        CheckConstraint("narxi > 0"),
        UniqueConstraint("buyurtma_id", "mahsulot_id"),
    )

    id: int | None = Field(default=None, sa_column=Column(BigInteger, Identity(), primary_key=True))
    buyurtma_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("buyurtmalar.id"), nullable=False)
    )
    mahsulot_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("mahsulotlar.id"), nullable=False)
    )
    soni: int = Field(sa_column=Column(BigInteger, nullable=False))
    narxi: int = Field(sa_column=Column(BigInteger, nullable=False))
    buyurtma: Buyurtma | None = Relationship(back_populates="qatorlar")
    mahsulot: Mahsulot | None = Relationship(back_populates="buyurtma_qatorlari")