from pathlib import Path


HOME_PATH = Path(__file__).parent
DATA_PATH = Path.joinpath(HOME_PATH, 'data')


print(DATA_PATH)