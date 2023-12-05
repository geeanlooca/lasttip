"""Thanks to John Rutledge: https://stackoverflow.com/a/6859596"""


def get_bigrams(string):
    """
    Take a string and return a list of bigrams.
    """
    s = string.lower()
    return [s[i : i + 2] for i in list(range(len(s) - 1))]


def string_similarity(str1, str2):
    """
    Perform bigram comparison between two strings
    and return a percentage match in decimal form.
    """

    if len(str1) < 2 or len(str2) < 2:
        return 0 if str1[:1] != str2[:1] else 1

    pairs1 = get_bigrams(str1)
    pairs2 = get_bigrams(str2)
    union = len(pairs1) + len(pairs2)
    hit_count = 0
    for x in pairs1:
        for y in pairs2:
            if x == y:
                hit_count += 1
                break
    return (2.0 * hit_count) / union
