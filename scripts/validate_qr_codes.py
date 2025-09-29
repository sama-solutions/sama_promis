#!/usr/bin/env python3
"""Validate QR code generation for SAMA PROMIS projects via XML-RPC."""

import argparse
import sys
import xmlrpc.client


REQUIRED_LIBRARIES = ('xmlrpc.client',)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://localhost:8069', help='Base URL of the Odoo server')
    parser.add_argument('-d', '--database', required=True, help='Database name to connect to')
    parser.add_argument('-u', '--username', default='admin', help='Odoo login user')
    parser.add_argument('-p', '--password', default='admin', help='Odoo user password')
    parser.add_argument('--limit', type=int, default=50, help='Limit number of projects to validate')
    parser.add_argument('--require-image', action='store_true',
                        help='Fail validation if qr_code_image is missing')
    return parser.parse_args()


def validate_dependencies():
    try:
        import qrcode  # noqa: F401  # pylint: disable=unused-import
    except ImportError:
        print('[WARN] python-qrcode library not available; image validation may fail.', file=sys.stderr)


def authenticate(args):
    common = xmlrpc.client.ServerProxy(f"{args.url}/xmlrpc/2/common")
    uid = common.authenticate(args.database, args.username, args.password, {})
    if not uid:
        raise RuntimeError('Authentication failed; check credentials')
    return uid


def fetch_projects(args, uid):
    models = xmlrpc.client.ServerProxy(f"{args.url}/xmlrpc/2/object")
    domain = [('qr_code_data', '!=', False)]
    fields = ['id', 'name', 'qr_code_data', 'qr_code_url', 'qr_code_image', 'state']
    return models.execute_kw(
        args.database,
        uid,
        args.password,
        'sama.promis.project',
        'search_read',
        [domain],
        {'fields': fields, 'limit': args.limit},
    )


def validate_records(records, require_image=False):
    missing_data = []
    for record in records:
        path_suffix = f"/promispublic/project/{record['id']}"
        if not record.get('qr_code_data') or path_suffix not in record['qr_code_data']:
            missing_data.append((record['id'], 'qr_code_data'))
        if record.get('qr_code_url') != record.get('qr_code_data'):
            missing_data.append((record['id'], 'qr_code_url'))
        if require_image and not record.get('qr_code_image'):
            missing_data.append((record['id'], 'qr_code_image'))
    return missing_data


def main():
    args = parse_args()
    validate_dependencies()

    uid = authenticate(args)
    records = fetch_projects(args, uid)

    if not records:
        print('[INFO] No projects found with QR data. Nothing to validate.')
        return 0

    failures = validate_records(records, require_image=args.require_image)
    if failures:
        for record_id, field_name in failures:
            print(f'[ERROR] Project {record_id} failed validation for {field_name}')
        return 1

    print(f"[OK] Validated {len(records)} project QR codes successfully.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
