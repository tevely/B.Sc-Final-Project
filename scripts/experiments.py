from typing import Iterator, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Session

from models import Experiment


class Experiments:
    def __init__(self, engine: sa.Engine):
        self.engine = engine
        Experiment.metadata.create_all(engine)

    def record_experiment(self, params, result) -> int:
        columns = params.copy()
        if "nmodes" in columns:
            del columns["nmodes"]
        if not columns.get("dy"):
            columns["dy"] = columns["dx"]
        if not columns.get("space_y"):
            columns["space_y"] = columns["space_x"]
        data = result.copy()
        while data:
            key, val = data.popitem()
            if key.startswith("neff"):
                columns[key + "_re"] = val.real
                columns[key + "_im"] = val.imag
            else:
                columns[key] = val

        with Session(self.engine) as session:
            experiment_id = session.execute(
                sa.insert(Experiment)
                .values(columns)
                .returning(Experiment.id)
            ).scalar()
            session.commit()
        return experiment_id

    def delete_experiment(self, experiment_id: int):
        self.engine.execute(
            sa.delete(Experiment)
            .where(Experiment.id == experiment_id)
        )


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///:memory:")
    db = Experiments(engine)
