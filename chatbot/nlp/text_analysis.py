from textblob import TextBlob, Word
import enchant
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# import string
import wikipedia


class AnalyzeText(object):

    def __init__(self):
        self.sentence = str().replace('&nbsp;', ' ')
        self.spell = enchant.Dict("en_US")

    def analyze_sentiment(self):
        """
        Performs sentiment analysis of a sentence and
        returns polarity, subjectivity
        """
        return TextBlob(self.sentence).sentiment

    def spellcheck(self):
        """
        Checks spelling of each word. If percent of
        wrong words is more than 60,
        return False else True.
        Second condition is
        """
        # Alternate solution without tokenizing would be to split the sentence.
        # length = len(words.split())
        # self.sentence = self.sentence

        # words = self.remove_stop_words()
        length = len(self.sentence.split())
        if length == 0:
            length = 1
        count = 0
        for x in self.sentence.split():
            if self.spell.check(x) == False:
                if Word(x).spellcheck()[0][1] < 0.8:
                    if len(x) >= 4:
                        if not wikipedia.search(x):
                            return False, x
                        count -= 1
                    count += 1
        if float(count)/length >= 0.55:
            return False, None
        return True, None

    def auto_correct_sentence(self):
        return TextBlob(self.sentence).correct()

    def auto_suggest_words(self, word):
        """
        Returns a list of suggestions of the entered `word`
        """
        return self.spell.suggest(word)

    def get_tags(self):
        """
        Returns a list of tuples. The tuple has words
        and their corresponding tags.
        """
        return TextBlob(self.sentence).tags

    def extract_noun_phrases(self, sentence):
        """
        Extract a list of nouns from the sentences.
        """
        return TextBlob(self.sentence).noun_phrases

    def count_frequency(self, word):
        """
        Returns the numeric value of the word in the sentence.
        Performs case-insensitive search.
        """
        return TextBlob(self.sentence).word_counts(word)

    def perform_sentence_tokenization(self):
        """
        Returns a list of sentences with tokens removed.
        """
        return TextBlob(self.sentence).sentences

    def get_word_definition(self, word):
        """
        Returns the multiple available definitions of the word in a list.
        """
        return Word(word).definitions

    def lemmatize_words(self, word):
        pass

    def tokenize_words(self):
        """
        Removes punctuations and tokenize words list.
        """
        # sent = sentence.translate(None, string.punctuation)
        word_tokens = word_tokenize(self.sentence)
        return word_tokens

    def remove_stop_words(self):
        """
        Removes stop words from the sentence, words which don't add any meaning
        to the sentence.
        """
        stop_words = set(stopwords.words('english'))
        word_tokens = self.tokenize_words()
        filtered_sentence = [w for w in word_tokens if not w in stop_words]
        filtered_sentence = " ".join(filtered_sentence)
        return filtered_sentence
