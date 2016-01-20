import logging

logger = logging.getLogger('anabot.preprocessor')

from .decorators import replace

@replace(None)
def unimplemented_replace(element):
    logger.warn('Unimplemented replace for: %s', element.nodePath())
    delete_element(element)

def delete_element(element):
    element.unlinkNode()
    element.freeNode()
