from typing import List
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(primary_key=True)

    dn_track: Mapped[float]
    dn_halo: Mapped[float]
    track_w: Mapped[float]
    track_h: Mapped[float]
    gap: Mapped[float]

    wl_pump: Mapped[float]
    wl_idler: Mapped[float]
    wl_signal: Mapped[float]
    neff_signal_re: Mapped[float]
    neff_signal_im: Mapped[float]
    neff_idler_re: Mapped[float]
    neff_idler_im: Mapped[float]
    neff_pump_re: Mapped[float]
    neff_pump_im: Mapped[float]
    int_eff_area: Mapped[float]
    coupling_s: Mapped[float]
    coupling_i: Mapped[float]
    coupling_p: Mapped[float]

    dx: Mapped[float]
    dy: Mapped[float]
    space_x: Mapped[float]
    space_y: Mapped[float]
    npml: Mapped[int]

    start_time: Mapped[int]
    duration: Mapped[int]
    status: Mapped[str]

    record_created = sa.Column(
        sa.DateTime,
        nullable=False,
        server_default=sa.text("(CURRENT_TIMESTAMP)"),
    )
