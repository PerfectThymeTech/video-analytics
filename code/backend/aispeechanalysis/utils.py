import copy
import logging
from datetime import datetime, timedelta
from typing import Any, List, Tuple


def get_transcript(ai_speech_blob_json: Any) -> str:
    """Creates and returns a transcript based on the content from Azure AI Speech STT batch transcription.

    ai_speech_blob_json (Any): JSON content from Azure AI Speech STT batch transcription.
    RETURNS (str): The transcript extracted from the JSON file.
    """
    ai_speech_blob_json_combined_recognized_phrases = ai_speech_blob_json.get(
        "combinedRecognizedPhrases", [{"display": None}]
    )
    return ai_speech_blob_json_combined_recognized_phrases[0].get("display")


def get_word_details(result_stt: Any) -> List[Any]:
    word_details = []
    recognized_phrases = result_stt.get("recognizedPhrases", [])

    for recognized_phrase in recognized_phrases:
        recognized_phrase_best = recognized_phrase.get("nBest", [])[0]
        recognized_phrase_best_display_words = recognized_phrase_best.get(
            "displayWords", []
        )

        # Append word details
        word_details.extend(recognized_phrase_best_display_words)

    return word_details


def offset_and_duration_to_timedelta(timedelta: str) -> Tuple[str, timedelta]:
    """Parses offset and duration notations to a timedelta object.

    timedelta (Any): Specifies the string notation of the offset or duration (e.g. 'PT24.01S', 'PT1M38.32S').
    RETURNS (Tuple[str, timedelta]): The transcript extracted from the JSON file and the format string.
    """
    # Initialize
    format_options = [
        "PT%S.%fS",
        "PT%MM%S.%fS",
        "PT%HH%MM%S.%fS",
    ]
    td = None
    format = None

    # Parse timdelta
    for format_option in format_options:
        try:
            t = datetime.strptime(timedelta, format_option)
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
                f"Parsing offset unsuccesful with string format '{format_option}'.", e
            )

    if td is None:
        message = f"Unable to parse offset '{timedelta}' with format options '{format_options}'"
        logging.error(message)
        raise ValueError(message)
    return (format, td)


def get_timestamps_for_sections(result_stt: Any, result_llm: Any) -> Any:
    # Get word details from stt result
    word_details = get_word_details(result_stt=result_stt)

    # Prepare result
    result = copy.deepcopy(result_llm.get("sections", []))

    for index_llm, item_llm in enumerate(result_llm.get("sections", [])):
        # Configure current item
        item_llm_current = "start"

        # Get llm item words
        item_llm_words = str(item_llm.get(item_llm_current, "")).split(sep=" ")

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
                            timedelta=item_word.get("offset")
                        )
                        td_sum = td_offset
                    else:
                        _, td_offset = offset_and_duration_to_timedelta(
                            timedelta=word_details[
                                index_word + len(item_llm_words) - 1
                            ].get("offset")
                        )
                        _, td_duration = offset_and_duration_to_timedelta(
                            timedelta=word_details[
                                index_word + len(item_llm_words) - 1
                            ].get("duration")
                        )
                        td_sum = td_offset + td_duration
                    result[index_llm][f"{item_llm_current}_time"] = str(td_sum)

                    # Update start or end item
                    if item_llm_current == "start":
                        item_llm_current = "end"
                    else:
                        break

    # Return result
    return {
        "sections": result,
    }


# def get_timestamps_for_sections(result_stt: Any, result_llm: Any) -> Any:
#     word_details = get_word_details(result_stt=result_stt)

#     # Configure indexes
#     result_llm_index = 0
#     result_llm_item = "start"

#     # Configure current item
#     result_llm_current_words = str(
#         result_llm[result_llm_index].get(result_llm_item, None)
#     ).split(sep=" ")

#     # Configure result
#     result = copy.deepcopy(result_llm)

#     for k, item in enumerate(result_llm):
#         # Configure current item
#         result_llm_current_words = str(
#             result_llm[result_llm_index].get(result_llm_item, None)
#         ).split(sep=" ")

#         for i, item in enumerate(word_details):
#             word_detail_display_text = item.get("displayText")

#             if word_detail_display_text == result_llm_current_words[0]:
#                 identical = [
#                     word == word_details[i + j].get("displayText")
#                     for j, word in enumerate(result_llm_current_words)
#                 ]
#                 all_identical = all(identical)

#                 if all_identical:
#                     result[result_llm_index][f"{result_llm_item}_offset"] = (
#                         word_details[i].get("offset")
#                         if result_llm_item == "start"
#                         else word_details[i + len(result_llm_current_words) - 1].get(
#                             "offset"
#                         )
#                     )

#                     # print(word_detail_display_text)
#                     # print(result[result_llm_index][f"{result_llm_item}_offset"])

#                     # Update index
#                     if result_llm_item == "start":
#                         result_llm_item = "end"
#                     else:
#                         result_llm_index += 1
#                         result_llm_item = "start"

#                     # Update current item
#                     if result_llm_index < len(result_llm):
#                         result_llm_current_words = str(
#                             result_llm[result_llm_index].get(result_llm_item, None)
#                         ).split(sep=" ")
#                         # print(result_llm_current_words)
#                     else:
#                         break

#     return result
