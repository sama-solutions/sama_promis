#!/usr/bin/env python3
"""Drive workflow validation via Odoo CLI commands."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_ADDONS_PATH = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--database', required=True, help='Target Odoo database name')
    parser.add_argument('-c', '--config', default=os.environ.get('ODOO_RC', '/etc/odoo/odoo.conf'),
                        help='Path to the odoo configuration file')
    parser.add_argument('--odoo-bin', default=os.environ.get('ODOO_BIN', 'odoo-bin'),
                        help='Binary used to launch Odoo')
    parser.add_argument('--addons-path', default=os.environ.get('ODOO_ADDONS_PATH', ''),
                        help='ODoo addons path to include (comma separated)')
    parser.add_argument('--tags', default='post_install', help='Test tags to execute')
    parser.add_argument('--failfast', action='store_true', help='Stop on first test failure')
    return parser.parse_args()


def build_command(args):
    command = [args.odoo_bin, '-c', args.config, '-d', args.database]
    addons = [str(DEFAULT_ADDONS_PATH)]
    if args.addons_path:
        addons.extend(args.addons_path.split(','))
    command.extend(['--addons-path', ','.join(addons)])

    extra = ['--test-enable', '--test-tags', args.tags]
    if args.failfast:
        extra.append('--stop-after-init')
    command.extend(extra)
    return command


def main():
    args = parse_args()
    command = build_command(args)

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Workflow tests failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode
    return 0


if __name__ == '__main__':
    sys.exit(main())
