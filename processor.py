import nltk
from pathlib import Path

directory = Path(__file__).parent.resolve() #pylint: disable=no-member

def nltk_setup(depends):
    d = directory / "nltk_data_storage"

    for item in depends:
        nltk.download(info_or_id=item,download_dir=str(directory / "nltk_data_storage"))
    nltk.data.path.append(str(directory / "nltk_data_storage"))
    gi = d / ".gitignore"
    if not gi.is_file():
        gi.touch()
        with gi.open("r+") as f:
            f.write("*\n*/\n!.gitignore")

def test(sentence):
    tokenized = nltk.word_tokenize(sentence)
    print(nltk.pos_tag(tokenized))


if __name__ == "__main__":
    nltk_setup(["punkt","averaged_perceptron_tagger"])
    test("The quick brown fox jumped over the lazy dog")