from typing import List, Union, NamedTuple

class VerbItem(NamedTuple):
    base: str
    f2: str
    f3: str
    translation: str

class WordPairItem(NamedTuple):
    eng: str
    rus: str

VerbList = List[VerbItem]
WordPairList = List[WordPairItem]
AnyWordList = Union[VerbList, WordPairList]

VERBS: VerbList = [
    VerbItem(base="be", f2="was/were", f3="been", translation="быть"),
    VerbItem(base="go", f2="went", f3="gone", translation="идти"),
    VerbItem(base="have", f2="had", f3="had", translation="иметь"),
    VerbItem(base="make", f2="made", f3="made", translation="делать"),
    VerbItem(base="see", f2="saw", f3="seen", translation="видеть"),
]

WORDS: WordPairList = [
    WordPairItem(eng="hello", rus="привет"),
    WordPairItem(eng="world", rus="мир"),
    WordPairItem(eng="developer", rus="разработчик"),
]

ADJECTIVES: WordPairList = [
    WordPairItem(eng="happy", rus="счастливый"),
    WordPairItem(eng="sad", rus="грустный"),
    WordPairItem(eng="brave", rus="смелый"),
]

DICTIONARIES: dict[str, AnyWordList] = {
    "Глаголы": VERBS,
    "Слова": WORDS,
    "Прилагательные": ADJECTIVES
}

def get_list_type(data_list: AnyWordList) -> str:
    if not data_list:
        return "unknown"
    if isinstance(data_list[0], VerbItem):
        return "verb"
    elif isinstance(data_list[0], WordPairItem):
        return "word_pair"
    else:
        return "unknown"