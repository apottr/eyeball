from pathlib import Path

directory = Path(__file__).parent.parent.resolve() #pylint: disable=no-member
dbname = str(directory / "databases" / "sources.db")