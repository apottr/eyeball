from parser_functions.parser_functions import get_data_from_job
import sys

def data_handler(job,date_range):
    d = get_data_from_job(job,date_range)
    for item in d:
        for jtem in item["entites"]:
            print(jtem)

if __name__ == "__main__":
    print(data_handler(sys.argv[1],[sys.argv[2],sys.argv[3]]))