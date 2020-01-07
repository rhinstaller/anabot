from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail

def assertLabelEquals(node, expected_text, label_name, message_format="%s label text (%s) is different then expected (%s)."):
    label_text = node.name
    if label_text != expected_text:
        return Fail(message_format % (label_name, label_text, expected_text))
    return Pass()

def assertTextInputEquals(node, expected_text, input_name, message_format="%s input text (%s) is different then expected (%s)."):
    input_text = node.text
    if input_text != expected_text:
        return Fail(message_format % (input_name, input_text, expected_text))
    return Pass()
