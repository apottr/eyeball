from pathlib import Path

directory = Path(__file__).parent.parent.resolve() #pylint: disable=no-member
sources_db = str(directory / "databases" / "sources.db")
projects_db = str(directory / "databases" / "projects.db")