"""Telegram interfeysi uchun qisqa DB o‘qishlari va telefon yordamchilari."""

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..crud import mijoz_yaratish
from ..models import Kategoriya, Mahsulot, Mijoz
from ..schemas import MijozKirish


def telefonni_tozalash(raw: str) -> str:
    raqam = "".join(belgi for belgi in raw if belgi.isdigit())
    if len(raqam) < 7:
        raise ValueError("Telefon raqami juda qisqa")
    return f"+{raqam}"


def mijozni_telefon_bilan_topish(engine, telefon: str) -> int | None:
    with Session(engine) as session:
        mijoz = session.exec(select(Mijoz).where(Mijoz.telefon == telefon)).one_or_none()
        return mijoz.id if mijoz else None


def mijozni_qoshish(engine, kirish: MijozKirish) -> int:
    with Session(engine) as session:
        try:
            mijoz = mijoz_yaratish(session, kirish)
        except IntegrityError:
            session.rollback()
            mavjud = mijozni_telefon_bilan_topish(engine, kirish.telefon)
            if mavjud is None:
                raise
            return mavjud
        assert mijoz.id is not None
        return mijoz.id


def kategoriyalarni_olish(engine) -> list[tuple[int, str]]:
    with Session(engine) as session:
        kategoriyalar = session.exec(select(Kategoriya).order_by(Kategoriya.nomi)).all()
        return [(k.id, k.nomi) for k in kategoriyalar if k.id is not None]


def mahsulotlarni_olish(engine, kategoriya_id: int) -> list[tuple[int, str, int, int]]:
    with Session(engine) as session:
        mahsulotlar = session.exec(
            select(Mahsulot).where(Mahsulot.kategoriya_id == kategoriya_id).order_by(Mahsulot.id)
        ).all()
        return [(m.id, m.nomi, m.narxi, m.ombor_qoldigi) for m in mahsulotlar if m.id is not None]


def mahsulotni_olish(engine, mahsulot_id: int) -> tuple[str, int, int] | None:
    with Session(engine) as session:
        mahsulot = session.get(Mahsulot, mahsulot_id)
        if mahsulot is None:
            return None
        return mahsulot.nomi, mahsulot.narxi, mahsulot.ombor_qoldigi


def savat_mazmuni(engine, savat: dict[str, int]) -> tuple[list[str], int]:
    qatorlar: list[str] = []
    jami = 0
    for mahsulot_id, soni in savat.items():
        mahsulot = mahsulotni_olish(engine, int(mahsulot_id))
        if mahsulot is None:
            qatorlar.append(f"#{mahsulot_id}: mahsulot topilmadi")
            continue
        nomi, narxi, _ = mahsulot
        qatorlar.append(f"{nomi} — {soni} × {narxi:,} = {soni * narxi:,} so‘m")
        jami += soni * narxi
    return qatorlar, jami