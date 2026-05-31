import re
from typing import List, Set

# Standard English stop words
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's",
    "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll",
    "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's",
    "the", "their", "theirs", "them", "themselves", "then", "there", "there's",
    "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when",
    "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why",
    "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves"
}

class Tokenizer:
    def __init__(self):
        # Regex to keep alphanumeric words
        self.word_pattern = re.compile(r'\b\w+\b')

    def tokenize(self, text: str) -> List[str]:
        """Convert text to lowercase and extract words."""
        text = text.lower()
        return self.word_pattern.findall(text)

class Stemmer:
    """
    A lightweight, rule-based stemmer.
    Reduces words to their root (e.g., 'running' -> 'run', 'dogs' -> 'dog').
    While not a full Porter Stemmer, it implements core suffix stripping algorithms
    to demonstrate the concept effectively.
    """
    def stem(self, word: str) -> str:
        if len(word) <= 2:
            return word
            
        # Common plural and active endings
        if word.endswith('sses'):
            word = word[:-2]
        elif word.endswith('ies'):
            word = word[:-3] + 'y'
        elif word.endswith('ss'):
            pass
        elif word.endswith('es') and not word.endswith('ces') and not word.endswith('tes'):
             word = word[:-2]
        elif word.endswith('s') and not word.endswith('us') and not word.endswith('ss'):
            word = word[:-1]
            
        # Common verb endings
        if word.endswith('ing'):
            if len(word) > 4 and word[-4] == word[-5] and word[-4] not in 'lsz': 
                # e.g., running -> run (handle double consonant)
                return word[:-4]
            return word[:-3]
        elif word.endswith('ed'):
            if len(word) > 3 and word[-3] == word[-4] and word[-3] not in 'lsz':
                # e.g., stopped -> stop
                return word[:-3]
            return word[:-2]
            
        # Adverb/Adjective endings
        if word.endswith('ly'):
            return word[:-2]
        elif word.endswith('tional'):
            return word[:-6] + 'tion'
        elif word.endswith('ment'):
            return word[:-4]
            
        return word

class Analyzer:
    """
    Text processing pipeline that combines tokenization, stop-word removal, and stemming.
    """
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.stemmer = Stemmer()
        self.stop_words = STOP_WORDS

    def analyze(self, text: str) -> List[str]:
        """
        The full analysis pipeline:
        1. Tokenize (lowercase + punctuation removal)
        2. Stop-word removal
        3. Stemming
        """
        tokens = self.tokenizer.tokenize(text)
        filtered_tokens = [t for t in tokens if t not in self.stop_words]
        stemmed_tokens = [self.stemmer.stem(t) for t in filtered_tokens]
        return stemmed_tokens
