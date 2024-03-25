def recursive_lookup(searched_key, dictionary):
    if searched_key in dictionary: return dictionary[searched_key]
    for value in dictionary.values():
        if isinstance(value, dict):
            result = recursive_lookup(searched_key, value)
            if result is not None: return result
    return None
