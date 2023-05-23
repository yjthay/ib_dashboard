from datetime import datetime
from sqlalchemy import create_engine, func, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from sqlalchemy.types import DateTime, Integer, String, Float
from pathlib import Path


class Base(DeclarativeBase):
    pass


class Asset(Base):
    __tablename__: str = "Assets"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, nullable=False)
    asset_name: Mapped[str] = mapped_column(String(20), nullable=False)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False)
    option = relationship("Option", back_populates="asset")

    def __repr__(self) -> str:
        return (
            f"Asset(id={self.id!r}, "
            f"asset_name={self.asset_name!r}, "
            f"ticker={self.ticker!r})"
        )


class Option(Base):
    __tablename__: str = "Options"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("Assets.id"))
    asset = relationship("Asset", back_populates="option")

    current_date: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    expiry_date: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    multiplier: Mapped[int] = mapped_column(Integer(), nullable=False)
    day_count: Mapped[Float] = mapped_column(Float(), nullable=False)
    delta: Mapped[Float] = mapped_column(Float(), nullable=False)
    gamma: Mapped[Float] = mapped_column(Float(), nullable=False)
    theta: Mapped[Float] = mapped_column(Float(), nullable=False)
    vega: Mapped[Float] = mapped_column(Float(), nullable=False)
    present_value: Mapped[Float] = mapped_column(Float(), nullable=False)

    def __repr__(self) -> str:
        return (
            f"Option(id={self.id!r}, "
            f"asset_name={self.asset!r}, "
            f"current_date={self.current_date!r})"
            f"expiry_date={self.expiry_date!r})"
            f"present_value={self.present_value!r})"
        )


def main() -> None:
    number_of_top_assets = int(
        input("How many top assets do you want to query? ")
    )

    db_path = Path("database/sample_database.db").absolute()
    engine = create_engine(rf"sqlite:///{db_path}")
    session = Session(engine)
    stmt = (
        select(
            Asset.id,
            Asset.asset_name,
            Asset.ticker,
            func.sum(Option.present_value).label("present_value"),
        )
        .join(Option, Asset.id == Option.asset_id)
        .group_by(Asset.id, Asset.asset_name, Asset.ticker)
        .order_by(func.sum(Option.present_value).label("present_value").desc())
        .limit(number_of_top_assets)
    )

    for portfolio in session.execute(stmt):
        print(portfolio)


if __name__ == "__main__":
    main()
