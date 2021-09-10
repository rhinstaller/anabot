import fnmatch
import math

from anabot.runtime.default import default_handler
from anabot.runtime.functions import getnode, getnodes, get_attr, getsibling
from anabot.runtime.functions import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.asserts import assertLabelEquals as ale
from anabot.runtime.installation.common import done_handler

from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check

_local_path = '/installation/hub/connect_to_redhat/registration/subscriptions'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)

PASS = Pass()

@handle_act('')
def base_handler(element, app_node, local_node):
    local_node = getnode(local_node, "scroll pane")
    return default_handler(element, app_node, local_node)

@handle_chck('')
def base_check(element, app_node, local_node):
    min_amount = get_attr(element, 'minAmount')
    max_amount = get_attr(element, 'maxAmount')
    amount = get_attr(element, 'amount', '-1' if min_amount or max_amount else None )
    if amount is None:
        amount = len(element.xpathEval('./subscription'))
    else:
        amount = int(amount)
    local_node = getnode(local_node, "scroll pane")
    try:
        subscription_items = getnodes(local_node, "list item")
    except TimeoutError:
        subscription_items = []
    subscription_count = math.ceil(len(subscription_items)/2)
    if amount != -1 and subscription_count != amount:
        return Fail("Number of subscriptions displayed (%d) doesn't match expectance (%d)" % (subscription_count, amount))
    if min_amount is not None and subscription_count < int(min_amount):
        return Fail("Number of subscriptions displayed (%d) is lower than minAmount (%d)" % (subscription_count, min_amount))
    if max_amount is not None and subscription_count > int(max_amount):
        return Fail("Number of subscriptions displayed (%d) is higher than manAmount (%d)" % (subscription_count, max_amount))
    subscriptions_label = getsibling(local_node, -1, "label")
    if subscription_count == 0:
        expected_text = "No subscriptions are attached to the system"
    elif subscription_count == 1:
        expected_text = "1 subscription attached to the system"
    else:
        expected_text = "%d subscriptions attached to the system" % subscription_count
    return ale(subscriptions_label, expected_text, "Amount of subscriptions")

def find_subscription(local_node, pattern):
    try:
        subscriptions = getnodes(local_node, "list item")
    except TimeoutError:
        return None
    for list_item in subscriptions:
        if fnmatch.fnmatchcase(getnode(list_item, "label").name, pattern):
            return list_item
    return None

@handle_act('/subscription')
def subscription_handler(element, app_node, local_node):
    name = get_attr(element, "name")
    list_item = find_subscription(local_node, name)
    if list_item is None:
        return NotFound(name, where="subscriptions list")
    return default_handler(element, app_node, list_item)

@handle_chck('/subscription')
def subscription_check(element, app_node, local_node):
    name = get_attr(element, "name")
    list_item = find_subscription(local_node, name)
    if list_item is None:
        return NotFound(name, where="subscriptions list")
    return PASS

handle_act('/subscription/service_level', default_handler)
@handle_chck('/subscription/service_level')
def service_level_check(element, app_node, local_node):
    value = get_attr(element, "value")
    # UGLY HACK
    label = getnodes(local_node, "label")[5]
    return ale(label, value, "Service level")

handle_act('/subscription/sku', default_handler)
@handle_chck('/subscription/sku')
def sku_check(element, app_node, local_node):
    value = get_attr(element, "value")
    # UGLY HACK
    label = getnodes(local_node, "label")[3]
    return ale(label, value, "SKU")

handle_act('/subscription/contract', default_handler)
@handle_chck('/subscription/contract')
def contract_check(element, app_node, local_node):
    value = get_attr(element, "value")
    # UGLY HACK
    label = getnodes(local_node, "label")[1]
    return ale(label, value, "Contract")

handle_act('/subscription/start_date', default_handler)
@handle_chck('/subscription/start_date')
def start_date_check(element, app_node, local_node):
    value = get_attr(element, "value")
    # UGLY HACK
    label = getnodes(local_node, "label")[11]
    return ale(label, value, "Start date")

handle_act('/subscription/end_date', default_handler)
@handle_chck('/subscription/end_date')
def end_date_check(element, app_node, local_node):
    value = get_attr(element, "value")
    # UGLY HACK
    label = getnodes(local_node, "label")[9]
    return ale(label, value, "End date")

handle_act('/subscription/entitlements_consumed', default_handler)
@handle_chck('/subscription/entitlements_consumed')
def entitlements_consumed_check(element, app_node, local_node):
    value = get_attr(element, "value")
    # UGLY HACK
    label = getnodes(local_node, "label")[7]
    return ale(label, ("%s consumed" % value), "Entitlements consumed")

