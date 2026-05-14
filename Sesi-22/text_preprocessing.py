"""
Spam Email Preprocessing Pipeline
===================================
sklearn-compatible pipeline untuk preprocessing teks spam email.

Urutan steps:
    1. MaskURL          – ganti URL shortener → shorturltoken, URL biasa → urltoken
    2. MaskCurrency     – ganti nominal Rp/USD → nominaltoken, angka besar → numbertoken
    3. NormalizeElongation – normalisasi karakter berulang (fireeee → firee)
    4. RemovePunctuation   – hapus punctuation, pertahankan token masking
    5. Casefold & Strip    – lowercase + trim spasi
    6. Lemmatize           – lemmatisasi dengan POS-aware WordNetLemmatizer
    7. RemoveStopwords     – buang stopwords English, jaga mask tokens

Usage:
    from spam_preprocessing_pipeline import build_pipeline

    pipeline = build_pipeline()
    df['clean_text'] = pipeline.fit_transform(df['text'])
"""

import re
import time
import logging
import functools
import nltk
import pandas as pd
from nltk.corpus import words as nltk_words
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),                          # terminal
        logging.FileHandler('preprocessing.log'),         # file
    ]
)
logger = logging.getLogger(__name__)

def log_transform(fn):
    """Decorator: catat nama transformer, jumlah row, dan waktu eksekusi."""
    @functools.wraps(fn)
    def wrapper(self, X, **kwargs):
        start  = time.time()
        result = fn(self, X, **kwargs)
        n_rows = X.shape[0] if hasattr(X, 'shape') else len(X)
        logger.info(f"{self.__class__.__name__:<22} | {n_rows:>6} rows | {time.time() - start:.3f}s")
        return result
    return wrapper

# Variable global
MASK_TOKENS   = frozenset({'urltoken', 'shorturltoken', 'nominaltoken', 'numbertoken'})
ENGLISH_WORDS = set(nltk_words.words())
BASE_STOPWORDS = set(stopwords.words('english'))

# 1. URL Masking
class URLMasker(BaseEstimator, TransformerMixin):
    """
    Ganti URL shortener (bit.ly, tinyurl, dst.) → 'shorturltoken'
    dan URL biasa + naked domain → 'urltoken'.
    """

    _SHORTENER_PAT = re.compile(
        r'https?://\S*(?:bit\.ly|tinyurl|goo\.gl|t\.co|shorturl)\S*',
        flags=re.IGNORECASE
    )
    _URL_PAT    = re.compile(r'https?://\S+')
    _DOMAIN_PAT = re.compile(r'\b(?:www\.)\S+\.\S+')

    def fit(self, X, y=None):
        return self

    @log_transform
    def transform(self, X):
        return pd.Series(X).apply(self._mask).values

    def _mask(self, text: str) -> str:
        text = self._SHORTENER_PAT.sub(' shorturltoken ', text)
        text = self._URL_PAT.sub(' urltoken ', text)
        text = self._DOMAIN_PAT.sub(' urltoken ', text)
        return text


# 2. Currency & Number Masking
class CurrencyMasker(BaseEstimator, TransformerMixin):
    """
    Ganti nominal Rp/IDR → 'nominaltoken',
    nominal USD/$  → 'nominaltoken',
    angka besar standalone (≥4 digit) → 'numbertoken'.
    """

    _RP_PAT  = re.compile(
        r'Rp\.?\s?[\d.,]+(?:\s?(?:ribu|juta|miliar|rb|jt|M))?',
        flags=re.IGNORECASE
    )
    _USD_PAT = re.compile(
        r'\$\s?[\d.,]+(?:\s?(?:thousand|million|billion))?',
        flags=re.IGNORECASE
    )
    _NUM_PAT = re.compile(r'\b\d{4,}(?:[.,]\d+)*\b')

    def fit(self, X, y=None):
        return self

    @log_transform
    def transform(self, X):
        return pd.Series(X).apply(self._mask).values

    def _mask(self, text: str) -> str:
        text = self._RP_PAT.sub(' nominaltoken ', text)
        text = self._USD_PAT.sub(' nominaltoken ', text)
        text = self._NUM_PAT.sub(' numbertoken ', text)
        return text


# 3. Elongation Normalizer
class ElongationNormalizer(BaseEstimator, TransformerMixin):
    """
    Normalisasi karakter yang diulang berlebihan.
        fireeee   → firee   (max_repeat=2)
        gratiisss → gratiss

    Parameters
    ----------
    max_repeat : int
        Maksimum karakter berulang yang diizinkan (default=2).
    smart : bool
        Jika True, coba cocokkan ke kamus English sebelum fallback ke max_repeat.
        Berguna untuk teks campuran English-Indonesia (default=False).
    """

    def __init__(self, max_repeat: int = 2, smart: bool = False):
        self.max_repeat = max_repeat
        self.smart      = smart

    def fit(self, X, y=None):
        self._pattern = re.compile(rf'(.)\1{{{self.max_repeat},}}')
        return self

    @log_transform
    def transform(self, X):
        fn = self._smart_normalize if self.smart else self._normalize
        return pd.Series(X).apply(fn).values

    def _normalize(self, text: str) -> str:
        return self._pattern.sub(r'\1' * self.max_repeat, text)

    def _smart_normalize(self, text: str) -> str:
        return ' '.join(self._fix_word(w) for w in text.split())

    def _fix_word(self, word: str) -> str:
        reduced = re.sub(r'(.)\1{2,}', r'\1\1', word)
        for n in range(len(reduced), 0, -1):
            candidate = re.sub(
                r'(.)\1+',
                lambda m: m.group(1) * min(len(m.group()), n),
                reduced
            )
            if candidate.lower() in ENGLISH_WORDS:
                return candidate
        return reduced


# 4. Punctuation Remover
class PunctuationRemover(BaseEstimator, TransformerMixin):
    """
    Hapus semua karakter selain huruf, angka, dan spasi.
    Mask token (urltoken, nominaltoken, dst.) tetap aman karena hanya alfanumerik.
    """

    _PUNCT_PAT  = re.compile(r'[^\w\s]')
    _SPACE_PAT  = re.compile(r'\s+')
    _EMOJI_PAT  = re.compile(
        r'[:;=]-?[\)\(\|DPp]|[\U0001F300-\U0001FFFF]'
    )
    _NEWLINE_PAT = re.compile(r'\n')

    def fit(self, X, y=None):
        return self

    @log_transform
    def transform(self, X):
        return pd.Series(X).apply(self._clean).values

    def _clean(self, text: str) -> str:
        text = self._NEWLINE_PAT.sub(' ', text)
        text = self._EMOJI_PAT.sub('', text)
        text = self._PUNCT_PAT.sub('', text)
        text = self._SPACE_PAT.sub(' ', text)
        return text.strip()


# 5. Casefold
class Casefolding(BaseEstimator, TransformerMixin):
    """Lowercase semua teks."""

    def fit(self, X, y=None):
        return self

    @log_transform
    def transform(self, X):
        return pd.Series(X).str.lower().str.strip().values


# 6. Lemmatizer (POS-aware)
class POSLemmatizer(BaseEstimator, TransformerMixin):
    """
    Lemmatisasi dengan WordNetLemmatizer menggunakan POS tag yang tepat.
    Mask token dilewati tanpa dimodifikasi.
    """

    _TAG_MAP = {'J': wordnet.ADJ, 'V': wordnet.VERB, 'N': wordnet.NOUN, 'R': wordnet.ADV}

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def fit(self, X, y=None):
        return self

    @log_transform
    def transform(self, X):
        return pd.Series(X).apply(self._lemmatize).values

    def _get_pos(self, word: str):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        return self._TAG_MAP.get(tag, wordnet.NOUN)

    def _lemmatize(self, text: str) -> str:
        return ' '.join(
            word if word in MASK_TOKENS
            else self.lemmatizer.lemmatize(word, self._get_pos(word))
            for word in text.split()
        )


# 7. Stopword Remover
class StopwordRemover(BaseEstimator, TransformerMixin):
    """
    Hapus stopwords English.
    Mask token (urltoken, nominaltoken, dst.) selalu dipertahankan.

    Parameters
    ----------
    extra_stopwords : set | None
        Tambahan kata yang ingin dihapus (opsional).
    """

    def __init__(self, extra_stopwords: set = None):
        self.extra_stopwords = extra_stopwords or set()

    def fit(self, X, y=None):
        self._sw = BASE_STOPWORDS | self.extra_stopwords
        return self

    @log_transform
    def transform(self, X):
        return pd.Series(X).apply(self._remove).values

    def _remove(self, text: str) -> str:
        return ' '.join(
            word for word in text.split()
            if word in MASK_TOKENS or word not in self._sw
        )


# Factory: build_pipeline()
def build_pipeline(
    elongation_max_repeat: int = 2,
    elongation_smart: bool = False,
    extra_stopwords: set = None
) -> Pipeline:
    """
    Buat preprocessing pipeline siap pakai.

    Parameters
    ----------
    elongation_max_repeat : int
        Maksimum karakter berulang (default=2).
    elongation_smart : bool
        Gunakan dictionary-lookup saat normalisasi elongation (default=False).
    extra_stopwords : set | None
        Tambahan stopwords kustom.

    Returns
    -------
    sklearn.pipeline.Pipeline

    Examples
    --------
    >>> pipeline = build_pipeline()
    >>> df['clean_text'] = pipeline.fit_transform(df['text'])

    >>> # Dengan custom stopwords
    >>> pipeline = build_pipeline(extra_stopwords={'click', 'free', 'win'})
    >>> df['clean_text'] = pipeline.fit_transform(df['text'])
    """
    return Pipeline(steps=[
        ('mask_url', URLMasker()),
        ('mask_currency', CurrencyMasker()),
        ('elongation', ElongationNormalizer(
                        max_repeat = elongation_max_repeat,
                        smart = elongation_smart
                    )),
        ('punctuation', PunctuationRemover()),
        ('casefold', Casefolding()),
        ('lemmatize', POSLemmatizer()),
        ('stopwords', StopwordRemover(extra_stopwords = extra_stopwords)),
    ])


# Demo / Smoke test
if __name__ == '__main__':
    sample = pd.DataFrame({
        'text': [
            "GRATIS!!! Klik http://bit.ly/abc123 sekarang & menangkan Rp500.000!!!",
            "Dear user, your account has been SELECTED!! Visit www.promo-win.com to claimmm your $1000 reward.",
            "Hello, please find attached the invoice for Rp 2.500.000 as discussed.\n\nRegards.",
            "Congratulationsss!!! You've wonnnn a brand new iPhone 😱🎉 – reply NOW!!!"
        ]
    })

    pipeline = build_pipeline(elongation_smart = False)
    sample['clean_text'] = pipeline.fit_transform(sample['text'])

    pd.set_option('display.max_colwidth', 80)
    print(sample[['text', 'clean_text']].to_string(index=False))
