import copy
from typing import Any, List


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


def get_timestamps_for_sections(result_stt: Any, result_llm: Any) -> Any:
    word_details = get_word_details(result_stt=result_stt)

    # Configure indexes
    result_llm_index = 0
    result_llm_item = "start"

    # Configure current item
    result_llm_current_words = str(
        result_llm[result_llm_index].get(result_llm_item, None)
    ).split(sep=" ")

    # Configure result
    result = copy.deepcopy(result_llm)

    for i, item in enumerate(word_details):
        word_detail_display_text = item.get("displayText")

        if word_detail_display_text == result_llm_current_words[0]:
            identical = [
                word == word_details[i + j].get("displayText")
                for j, word in enumerate(result_llm_current_words)
            ]
            all_identical = all(identical)

            if all_identical:
                result[result_llm_index][f"{result_llm_item}_offset"] = (
                    word_details[i].get("offset")
                    if result_llm_item == "start"
                    else word_details[i + len(result_llm_current_words) - 1].get(
                        "offset"
                    )
                )

                # print(word_detail_display_text)
                # print(result[result_llm_index][f"{result_llm_item}_offset"])

                # Update index
                if result_llm_item == "start":
                    result_llm_item = "end"
                else:
                    result_llm_index += 1
                    result_llm_item = "start"

                # Update current item
                if result_llm_index < len(result_llm):
                    result_llm_current_words = str(
                        result_llm[result_llm_index].get(result_llm_item, None)
                    ).split(sep=" ")
                    # print(result_llm_current_words)
                else:
                    break

    return result
