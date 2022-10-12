#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import shutil
import sys
from argparse import ArgumentParser

from ucs_modifier.modifier.modifier import UcsModifier
from ucs_sweeper.support.file_ops import untar_file
from ucs_sweeper.support.file_ops import tar_file
from ucs_sweeper.support.file_ops import delete_temp_dir

log = logging.getLogger(__name__)


def get_args():
    parser = ArgumentParser(description='Sweeps the specified ucs file, removing any sensitive data')
    parser.add_argument('-u', '--ucs', required=True,
                        help='Ucs file to sweep')
    parser.add_argument('-o', '--output', help='Target output file name')
    parser.add_argument('-d', '--debug', help='Enable debug logging', action='store_true')
    return parser.parse_args()


def main():
    args = get_args()
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(levelname)s:\t%(message)s')
    ucs_dir = untar_file(args.ucs, dir='/tmp', prefix='sweep_ucs_')

    modifier = UcsModifier(extracted_ucs_dir=ucs_dir)
    modifier.sweep_ucs()
    new_ucs_fn = args.output or os.path.basename(args.ucs).replace('.ucs', '_swept.ucs')
    temp_ucs = tar_file(new_ucs_fn, ucs_dir)

    shutil.move(temp_ucs, new_ucs_fn)

    delete_temp_dir(ucs_dir)

    log.info('Sweeping complete.')
    log.info(new_ucs_fn)

    return 0


if __name__ == '__main__':
    sys.exit(main())
