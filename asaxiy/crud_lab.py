from sqlmodel import Session
from .database import make_engine
from .crud import (
    kategoriya_yaratish, mahsulot_yaratish, mahsulot_olish,
    mahsulot_yangilash, mahsulot_ochirish, mahsulotlar_royxati,
)
from .schemas import KategoriyaKirish, MahsulotKirish, MahsulotYangilash

engine = make_engine()
with Session(engine) as session:
    kategoriya = kategoriya_yaratish(
        session, KategoriyaKirish(nomi="13-dars kitoblari")
    )
    mahsulot = mahsulot_yaratish(session, MahsulotKirish(
        kategoriya_id=kategoriya.id,
        nomi="13-dars Python kitobi",
        narxi=120000,
        ombor_qoldigi=5,
    ))
    print("CREATE:", mahsulot.id, mahsulot.narxi)
    print("READ:", mahsulot_olish(session, mahsulot.id).nomi)
    print("LIST:", len(mahsulotlar_royxati(session, kategoriya.id)))
    yangisi = mahsulot_yangilash(
        session, mahsulot.id, MahsulotYangilash(narxi=135000)
    )
    print("UPDATE:", yangisi.narxi)
    mahsulot_ochirish(session, mahsulot.id)
    print("DELETE:", len(mahsulotlar_royxati(session, kategoriya.id)))
engine.dispose()