from enum import IntEnum


class Status(IntEnum):
    IN_LAB = 1
    HOME = 2
    LECTURE = 3
    CAMPUS_M = 4
    CAMPUS_OTHER = 5

    @property
    def label(self) -> str:
        return _LABELS[self]

    @property
    def color(self) -> str:
        return _COLORS[self]


_LABELS = {
    Status.IN_LAB: "在室",
    Status.HOME: "帰宅",
    Status.LECTURE: "講義",
    Status.CAMPUS_M: "学内(M棟)",
    Status.CAMPUS_OTHER: "学内(その他)",
}

_COLORS = {
    Status.IN_LAB: "#4caf50",
    Status.HOME: "#9e9e9e",
    Status.LECTURE: "#2196f3",
    Status.CAMPUS_M: "#ff9800",
    Status.CAMPUS_OTHER: "#ffc107",
}
