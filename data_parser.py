from parser_functions import get_data_from_job
import sys


if __name__ == "__main__":
    print(get_data_from_job(sys.argv[1],[sys.argv[2],sys.argv[3]]))