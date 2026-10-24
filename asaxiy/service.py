from sqlmodel import Session, select

from .models import Buyurtma, BuyurtmaQatori, Mahsulot, Mijoz
from .schemas import BuyurtmaSorovi

def buyurtma_ber(engine, sorov: BuyurtmaSorovi) -> Buyurtma:
    with Session(engine, expire_on_commit=False) as session:
        with session.begin():
            if session.get(Mijoz, sorov.mijoz_id) is None:
                raise ValueError("Mijoz topilmadi")

            sonlar = {q.mahsulot_id: q.soni for q in sorov.qatorlar}
            mahsulotlar: list[Mahsulot] = []
            for mahsulot_id in sorted(sonlar):
                mahsulot = session.exec(
                    select(Mahsulot).where(Mahsulot.id == mahsulot_id).with_for_update()
                ).one_or_none()
                if mahsulot is None:
                    raise ValueError(f"Mahsulot topilmadi: {mahsulot_id}")
                if mahsulot.ombor_qoldigi < sonlar[mahsulot_id]:
                    raise ValueError(f"Omborda yetarli emas: {mahsulot.nomi}")
                mahsulotlar.append(mahsulot)

            buyurtma = Buyurtma(mijoz_id=sorov.mijoz_id, umumiy_summa=0, holati="yangi")
            session.add(buyurtma)
            session.flush()
            assert buyurtma.id is not None
            for mahsulot in mahsulotlar:
                assert mahsulot.id is not None
                soni = sonlar[mahsulot.id]
                mahsulot.ombor_qoldigi -= soni
                buyurtma.umumiy_summa += mahsulot.narxi * soni
                session.add(
                    BuyurtmaQatori(
                        buyurtma_id=buyurtma.id,
                        mahsulot_id=mahsulot.id,
                        soni=soni,
                        narxi=mahsulot.narxi,
                    )
                )
            session.flush()
        return buyurtma