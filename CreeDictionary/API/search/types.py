from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from typing import Union, NewType, Iterable, Tuple, Optional

from typing_extensions import Protocol

from API.models import Wordform
from API.schema import SerializedLinguisticTag
from utils.fst_analysis_parser import LABELS
from utils.types import FSTTag

# it's a str when the preverb does not exist in the database
Preverb = Union[Wordform, str]
Lemma = NewType("Lemma", Wordform)
MatchedEnglish = NewType("MatchedEnglish", str)
InternalForm = NewType("InternalForm", str)


class LinguisticTag(Protocol):
    """
    A linguistic feature/tag pair.
    """

    @property
    def value(self) -> FSTTag:
        ...

    # TODO: linguistic feature

    @property
    def in_plain_english(self) -> str:
        ...

    def serialize(self) -> SerializedLinguisticTag:
        return SerializedLinguisticTag(
            value=self.value,
            in_plain_english=self.in_plain_english,
        )


class SimpleLinguisticTag(LinguisticTag):
    """
    A linguistic feature/tag pair.
    """

    def __init__(self, value: FSTTag):
        self._value = value

    @property
    def value(self) -> FSTTag:
        return self._value

    @property
    def in_plain_english(self) -> str:
        return LABELS.english.get(self.value) or "???"


class CompoundLinguisticTag(LinguisticTag):
    def __init__(self, tags: Iterable[FSTTag]) -> None:
        self._fst_tags = tuple(tags)

    @property
    def value(self):
        return "".join(self._fst_tags)

    @property
    def in_plain_english(self):
        return LABELS.english.get_longest(self._fst_tags)


def linguistic_tag_from_fst_tags(tags: Tuple[FSTTag, ...]) -> LinguisticTag:
    """
    Returns the appropriate LinguisticTag, no matter how many tags you chuck at it!
    """
    assert len(tags) > 0
    if len(tags) == 1:
        return SimpleLinguisticTag(tags[0])
    else:
        return CompoundLinguisticTag(tags)


class Language(Enum):
    SOURCE = "Source"
    TARGET = "Target"


def wordforms_match(w1: Wordform, w2: Wordform) -> bool:
    """Return whether two wordform objects represent the same wordform

    Either they both have IDs which match, or the text and analysis match.
    """
    if w1.id is not None or w2.id is not None:
        return w1.id == w2.id
    return w1.text == w2.text and w1.analysis == w2.analysis


@dataclass
class Result:
    """
    A target-language wordform and the features that link it to a query.

    The features—is it an exact source-language match for the query? Is the edit
    distance low? &c.—that make this a candidate result for a search query are
    required to rank different results before showing them to the user.

    Search methods may generate candidate results that are ultimately not sent
    to users, so any user-friendly tagging/relabelling is instead done in
    PresentationResult class.
    """

    def __post_init__(self):
        if all(
            getattr(self, field.name) == None
            for field in dataclasses.fields(Result)
            if field.init and field.name != "wordform"
        ):
            raise Exception("No features were provided for why this is a result.")

        self.is_lemma = self.wordform.is_lemma
        self.lemma_wordform = self.wordform.lemma

    def add_features_from(self, other: Result):
        """Add the features from `other` into this object

        Good results can match for many different reasons. This method merges
        features from a different result object for the same wordform into the
        current object.
        """
        assert wordforms_match(self.wordform, other.wordform)

        for field in dataclasses.fields(Result):
            if field.init and field.name != "wordform":
                other_value = getattr(other, field.name)
                if other_value is not None:
                    setattr(self, field.name, other_value)

    wordform: Wordform
    lemma_wordform: Lemma = field(init=False)
    is_lemma: bool = field(init=False)

    #: What, if any, was the matching string?
    source_language_match: Optional[str] = None

    source_language_affix_match: Optional[bool] = None
    target_language_affix_match: Optional[bool] = None

    target_language_keyword_match: Optional[str] = None
    pronoun_as_is_match: Optional[bool] = None

    analyzable_inflection_match: Optional[bool] = None

    is_preverb_match: Optional[bool] = None

    is_cw_as_is_wordform: Optional[bool] = None

    #: Was anything in the query a target-language match for this result?
    did_match_target_language: Optional[bool] = None

    #: Was anything in the query a source-language match for this result?
    @property
    def did_match_source_language(self) -> bool:
        return self.source_language_match is not None

    def __str__(self):
        return f"Result<wordform={self.wordform}>"
