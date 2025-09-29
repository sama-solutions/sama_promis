#!/usr/bin/env python3
"""Install SAMA PROMIS in an Odoo database and run the validation test suite."""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_BINARIES = ('odoo-bin',)
DEFAULT_ADDONS_PATH = Path(__file__).resolve().parents[1]


def check_dependencies():
    """Ensure required executables and python packages are available."""
    missing = []
    for binary in REQUIRED_BINARIES:
        if not shutil.which(binary):
            missing.append(binary)
    if missing:
        raise RuntimeError(f"Missing executables: {', '.join(missing)}")

    try:
        import xmlrpc.client  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Python standard library module xmlrpc.client missing") from exc



def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--database', required=True, help='Target Odoo database name')
    parser.add_argument('-c', '--config', default=os.environ.get('ODOO_RC', '/etc/odoo/odoo.conf'),
                        help='Path to the odoo configuration file')
    parser.add_argument('--addons-path', default=os.environ.get('ODOO_ADDONS_PATH', ''),
                        help='ODoo addons path to include (comma separated)')
    parser.add_argument('--odoo-bin', default=os.environ.get('ODOO_BIN', 'odoo-bin'),
                        help='Binary used to launch Odoo')
    parser.add_argument('--test-tags', default='post_install',
                        help='Test tags to execute')
    parser.add_argument('--upgrade', action='store_true',
                        help='Force module upgrade before running tests')
    return parser.parse_args()


def build_addons_path(custom_path):
    paths = [str(DEFAULT_ADDONS_PATH)]
    if custom_path:
        paths.extend(custom_path.split(','))
    return ','.join(paths)


def run_odoo_command(args, extra_args):
    command = [args.odoo_bin, '-c', args.config, '-d', args.database]
    if args.addons_path or DEFAULT_ADDONS_PATH:
        command.extend(['--addons-path', build_addons_path(args.addons_path)])
    command.extend(extra_args)
    subprocess.check_call(command)


def main():
    args = parse_args()

    check_dependencies()

    if args.upgrade:
        run_odoo_command(args, ['-u', 'sama_promis'])

    run_odoo_command(args, ['--test-enable', '--test-tags', args.test_tags])


if __name__ == '__main__':
    main()
