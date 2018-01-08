import enum


class State(enum.Enum):
    URL_STORED = 0
    CRAWLED = 1
    RESUMING = 2
    NOT_EXISTED = 3
    NOT_FOUND = 4
    HTML_STORED = 5
    URL_DUPLICATED = 6
