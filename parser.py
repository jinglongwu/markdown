import sys
from element import Element
from paragraph import TextParagraph
from block import TextBlock


class AbstractParser(object):
    def __init__(self):
        self._parsers = set()

    def register_parser(self, parser):
        '''
        Register a paragraph parser to self._parsers
        '''
        self._parsers.add(parser)

    def unregister_parser(self, parser):
        '''
        Remove a registered parser
        '''
        if parser in self._parsers:
            self._parsers.remove(parser)

    def parse(self, content):
        raise NotImplementedError("AbstractParser is not implemented.")


class ParagraphParser(AbstractParser):
    def __init__(self):
        super().__init__()
        self._paragraphs = []

    def parse(self, content):
        '''
        Invoke all parsers in self._parsers to try to parse the content.
        Return unparsed part.
        '''
        start_index = len(content)
        end_index = len(content)
        final_element = TextParagraph(content)
        for parser in self._parsers:
            begin, end, element = parser(content)
            if begin != 0 and begin < start_index:
                start_index, end_index, final_element = begin, end, element
        if start_index != 0 and start_index != len(content):
            self._paragraphs.append(TextParagraph(content[0, start_index]))
        self._paragraphs.append(final_element)
        return content[end:]


def link_parent_and_child(parent, child):
    child.set_parent(parent)
    parent.add_child(child)

class BlockParser(AbstractParser):
    def __init__(self):
        super().__init__()

    def _invoke_parsers(self, parent, content):
        start_index = len(content)
        end_index = len(content)
        final_element = TextBlock(content)
        for parser in self._parsers:
            begin, end, element = parser(content)
            if begin != 0 and begin < start_index:
                start_index, end_index, final_element = begin, end, element
        if start_index != 0 and start_index != len(content):
            child = TextBlock(content[0, start_index])
            link_parent_and_child(parent, child)
        link_parent_and_child(parent, final_element)
        return content[end:]

    def parse(self, content, root=None):
        '''
        Invoke all parsers in self._parsers to try to parse the content.
        Return unparsed part.
        '''
        if root is None:
            root = Element(content)
        cur_content = content
        while len(cur_content) > 0:
            cur_content = self._invoke_parsers(root, cur_content)

        for child in root.children():
            if not isinstance(child, TextBlock):
                self.parse(child.content(), child)
