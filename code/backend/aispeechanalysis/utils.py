import copy
import logging
import string
from datetime import datetime, timedelta
from typing import Any, List, Tuple


def remove_punctuation(text: str) -> str:
    """Removes punctuation from text.

    text (str): Specifies the text that should be altered.
    RETURNS (str): The altered text.
    """
    return text.translate(str.maketrans("", "", f"{string.punctuation}¿¡"))


def get_normalized_text(text: str) -> str:
    """Normalizes text by removing punctuation and lowering all characters.

    text (str): Specifies the text that should be altered.
    RETURNS (str): The altered text.
    """
    # Replace punctuation with dot
    text_removed_punctuation = remove_punctuation(text=text)

    # Lower text
    return text_removed_punctuation.lower()


def get_transcript(result_stt: Any) -> str:
    """Creates and returns a transcript based on the content from Azure AI Speech STT batch transcription.

    result_stt (Any): Specifies the JSON content from Azure AI Speech STT batch transcription.
    RETURNS (str): The transcript extracted from the JSON file.
    """
    result_stt_combined_recognized_phrases = result_stt.get(
        "combinedRecognizedPhrases", [{"display": None}]
    )
    return result_stt_combined_recognized_phrases[0].get("display")


def get_locale(result_stt: Any) -> str:
    """Returns the locale from the content from Azure AI Speech STT batch transcription.

    result_stt (Any): Specifies the JSON content from Azure AI Speech STT batch transcription.
    RETURNS (str): The locale extracted from the JSON file. Returns 'Unknown' if the property cannot be found in the JSON transcript.
    """
    result_stt_recognized_phrases = result_stt.get(
        "recognizedPhrases", [{"locale": "Unknown"}]
    )[0]
    return result_stt_recognized_phrases.get("locale", "Unknown")


def get_word_details(result_stt: Any, normalize_text: bool) -> List[Any]:
    """Returns all word details from a speech to text batch analysis process.

    result_stt (Any): Specifies the JSON content from Azure AI Speech STT batch transcription.
    normalize_text (bool): Specifies whether the text should be normalized.
    RETURNS (str): The altered text.
    """
    word_details = []
    recognized_phrases = result_stt.get("recognizedPhrases", [])

    for recognized_phrase in recognized_phrases:
        recognized_phrase_best = recognized_phrase.get("nBest", [])[0]
        recognized_phrase_best_display_words = recognized_phrase_best.get(
            "displayWords", []
        )

        if normalize_text:
            for display_word in recognized_phrase_best_display_words:
                display_word["displayText"] = get_normalized_text(
                    text=display_word["displayText"]
                )
                word_details.append(display_word)
        else:
            # Append word details
            word_details.extend(recognized_phrase_best_display_words)

    return word_details


def offset_and_duration_to_timedelta(timedelta_str: str) -> Tuple[str, timedelta]:
    """Parses offset and duration notations to a timedelta object.

    timedelta_str (Any): Specifies the string notation of the offset or duration (e.g. 'PT24.01S', 'PT1M38.32S').
    RETURNS (Tuple[str, timedelta]): The transcript extracted from the JSON file and the format string.
    """
    # Initialize
    format_options = [
        "PT%S.%fS",
        "PT%SS",
        "PT%MM%S.%fS",
        "PT%MM%SS",
        "PT%HH%MM%S.%fS",
        "PT%HH%MM%SS",
    ]
    td = None
    format = None

    # Parse timdelta
    for format_option in format_options:
        try:
            t = datetime.strptime(timedelta_str, format_option)
            td = timedelta(
                hours=t.hour,
                minutes=t.minute,
                seconds=t.second,
                microseconds=t.microsecond,
            )
            format = format_option
            break
        except ValueError as e:
            logging.warning(
                f"Parsing offset unsuccesful with string format '{format_option}'.",
            )

    if td is None:
        message = f"Unable to parse offset '{timedelta_str}' with format options '{format_options}'"
        logging.error(message)
        raise ValueError(message)
    return (format, td)


def get_timestamps_for_sections(result_stt: Any, result_llm: Any) -> Any:
    """Calculates and adds timestamps to the llm result.

    result_stt (Any): Specifies the JSON content from Azure AI Speech STT batch transcription.
    result_llm (Any): Specifies the JSON content from Azure Open AI analysis.
    RETURNS (Any): The JSON content from Azure Open AI analysis with added timestamps for start and end.
    """
    # Get word details from stt result
    word_details = get_word_details(result_stt=result_stt, normalize_text=True)

    # Prepare result
    result = copy.deepcopy(result_llm.get("sections", []))

    for index_llm, item_llm in enumerate(result_llm.get("sections", [])):
        # Configure current item
        item_llm_current = "start"

        # Get llm item words
        item_llm_words = str(
            get_normalized_text(item_llm.get(item_llm_current, ""))
        ).split(sep=" ")

        for index_word, item_word in enumerate(word_details):
            # Get display text of current word item
            item_word_display_text = item_word.get("displayText")

            # Check if first word matches
            if item_word_display_text and item_word_display_text == item_llm_words[0]:
                # Check if following words also match
                identical = [
                    item_llm_word
                    == word_details[index_word + index_llm_word].get("displayText")
                    for index_llm_word, item_llm_word in enumerate(item_llm_words)
                ]
                all_identical = all(identical)

                # If all are identical then update the timestamps
                if all_identical:
                    # Calculate timestamp based on start or end item
                    if item_llm_current == "start":
                        _, td_offset = offset_and_duration_to_timedelta(
                            timedelta_str=item_word.get("offset")
                        )
                        td_sum = td_offset
                    else:
                        _, td_offset = offset_and_duration_to_timedelta(
                            timedelta_str=word_details[
                                index_word + len(item_llm_words) - 1
                            ].get("offset")
                        )
                        _, td_duration = offset_and_duration_to_timedelta(
                            timedelta_str=word_details[
                                index_word + len(item_llm_words) - 1
                            ].get("duration")
                        )
                        td_sum = td_offset + td_duration
                    result[index_llm][f"{item_llm_current}_time"] = str(td_sum)

                    # Update start or end item
                    if item_llm_current == "start":
                        # Configure new current item
                        item_llm_current = "end"

                        # Get new llm item words
                        item_llm_words = str(
                            get_normalized_text(item_llm.get(item_llm_current, ""))
                        ).split(sep=" ")
                    else:
                        break

    # Return result
    return {
        "sections": result,
    }
