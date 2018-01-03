from PIL import Image
import glob
from pyzbar.pyzbar import decode
import os
import re
import attr
import json

files = sorted(glob.glob("*.png"))


@attr.s
class Page:
    """A scanned page."""
    filename = attr.ib()
    level = attr.ib()
    barcodes = attr.ib(default=attr.Factory(list))
    data = attr.ib(default=attr.Factory(list))

    def read_metadata(self):
        self.data = [json.loads(barcode.data) for barcode in self.barcodes]

    def sync(self):
        """Syncronize metadata."""
        raise NotImplementedError


@attr.s
class Node:
    children = attr.ib(default=attr.Factory(list))
    data = attr.ib(default=attr.Factory(list))

    def sync(self):
        raise NotImplementedError


def sort_numerically(files):
    filenames = []

    for filename in files:
        basename = os.path.basename(filename)
        root, _ = os.path.splitext(basename)
        matches = re.findall(r'[0-9]+', root)
        if matches:
            num = int(matches[-1])
        else:
            num = -1
        filenames.append((num, filename))

    return [fn for (_, fn) in sorted(filenames)]


def read_pages(files=files):
    level = 0
    pages = []
    for f in sort_numerically(files):
        barcodes = decode(Image.open(f))
        if len(barcodes) == 0:
            level += 1
            pages.append(Page(filename=f, level=level, barcodes=barcodes))
        else:
            level = 0
            pages.append(Page(filename=f, level=level, barcodes=barcodes))

    return pages


def create_nodes(pages):
    nodes = []
    for page in pages:
        if page.level == 0:
            nodes.append(Node(children=[page]))
        else:
            nodes[-1].children.append(page)

    return nodes
