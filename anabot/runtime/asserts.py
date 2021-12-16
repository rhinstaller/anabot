from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail

def assertLabelEquals(node, expected_text, label_name, message_format="%s label text (%s) is different than expected (%s)."):
    label_text = node.name
    if label_text != expected_text:
        return Fail(message_format % (label_name, label_text, expected_text))
    return Pass()

def assertLabelIn(node, expected_texts, label_name, message_format="%s label text (%s) is neither of expected texts (%s)."):
    label_text = node.name
    if label_text not in expected_texts:
        return Fail(message_format % (label_name, label_text, expected_texts))
    return Pass()

def assertTextInputEquals(node, expected_text, input_name, message_format="%s input text (%s) is different than expected (%s)."):
    input_text = node.text
    if input_text != expected_text:
        return Fail(message_format % (input_name, input_text, expected_text))
    return Pass()

def assertTextInputIn(node, expected_texts, input_name, message_format="%s input text (%s) is neither of expected texts (%s)."):
    input_text = node.text
    if input_text not in expected_texts:
        return Fail(message_format % (input_name, input_text, expected_texts))
    return Pass()

BLACK_CIRCLE = u'\u25cf'
def assertPasswordTextInputEquals(node, expected_text, input_name, message_format="%s password input text (%s) is different than expected (%s).", trippled=False):
    password_text = node.text
    expected_text = BLACK_CIRCLE*len(expected_text)
    if trippled:
        expected_text *= 3
    try:
        if expected_text != password_text.decode('utf8'):
            return Fail(message_format % (input_name, password_text, expected_text))
    except (UnicodeDecodeError, AttributeError):
        if expected_text != password_text:
            return Fail(message_format % (input_name, password_text, expected_text))
    return Pass()

def assertCheckboxEquals(node, expected_checked, checkbox_name, message_format="%s checkbox state (%s) is different than expected (%s)."):
    checked = node.checked
    if checked == expected_checked:
        return Pass()
    else:
        checked_status = "checked" if checked else "unchecked"
        expected_checked_status = "checked" if expected_checked else "unchecked"
        return Fail(message_format % (checkbox_name, checked_status, expected_checked_status))

def assertComboBoxEquals(node, expected_text, combo_name, message_format="%s combo box text (%s) is different than expected (%s)."):
    combo_text = node.name
    if combo_text == expected_text:
        return Pass()
    else:
        return Fail(message_format % (combo_name, combo_text, expected_text))

def assertComboBoxIn(node, expected_texts, combo_name, message_format="%s combo box text (%s) is neither of expected texts (%s)."):
    combo_text = node.name
    if combo_text in expected_texts:
        return Pass()
    else:
        return Fail(message_format % (combo_name, combo_text, expected_texts))
