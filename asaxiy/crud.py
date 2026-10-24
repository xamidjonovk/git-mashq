from sqlmodel import Session, select
from .models import Kategoriya, Mahsulot, Mijoz
from .schemas import KategoriyaKirish, MahsulotKirish, MahsulotYangilash, MijozKirish

def kategoriya_yaratish(session: Session, kirish: KategoriyaKirish) -> Kategoriya:
    kategoriya = Kategoriya(**kirish.model_dump())
    session.add(kategoriya)
    session.commit()
    session.refresh(kategoriya)
    return kategoriya

def mahsulot_yaratish(session: Session, kirish: MahsulotKirish) -> Mahsulot:
    if session.get(Kategoriya, kirish.kategoriya_id) is None:
        raise ValueError("Kategoriya topilmadi")
    mahsulot = Mahsulot(**kirish.model_dump())
    session.add(mahsulot)
    session.commit()
    session.refresh(mahsulot)
    return mahsulot

def mahsulot_olish(session: Session, mahsulot_id: int) -> Mahsulot:
    mahsulot = session.get(Mahsulot, mahsulot_id)
    if mahsulot is None:
        raise ValueError("Mahsulot topilmadi")
    return mahsulot

def mahsulotlar_royxati(session: Session, kategoriya_id: int | None = None):
    sorov = select(Mahsulot).order_by(Mahsulot.id)
    if kategoriya_id is not None:
        sorov = sorov.where(Mahsulot.kategoriya_id == kategoriya_id)
    return list(session.exec(sorov).all())

def mahsulot_yangilash(
    session: Session, mahsulot_id: int, kirish: MahsulotYangilash
) -> Mahsulot:
    mahsulot = mahsulot_olish(session, mahsulot_id)
    mahsulot.sqlmodel_update(kirish.model_dump(exclude_unset=True))
    session.add(mahsulot)
    session.commit()
    session.refresh(mahsulot)
    return mahsulot

def mahsulot_ochirish(session: Session, mahsulot_id: int) -> None:
    mahsulot = mahsulot_olish(session, mahsulot_id)
    session.delete(mahsulot)
    session.commit()

def mijoz_yaratish(session: Session, kirish: MijozKirish) -> Mijoz:
    mijoz = Mijoz(**kirish.model_dump())
    session.add(mijoz)
    session.commit()
    session.refresh(mijoz)
    return mijoz
