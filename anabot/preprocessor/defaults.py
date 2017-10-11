import logging

logger = logging.getLogger('anabot.preprocessor')

from .decorators import replace
from .sub import sub_element

@replace(None)
def unimplemented_replace(element):
    if element.name == 'sub':
        return sub_element(element)
    logger.warn('Unimplemented replace for: %s', element.nodePath())
    delete_element(element)

def delete_element(element):
    element.unlinkNode()
    element.freeNode()
