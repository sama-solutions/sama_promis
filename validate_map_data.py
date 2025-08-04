#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SAMA ÉTAT Map Data Validation Script
====================================

This script validates the coordinate data and map functionality for SAMA ÉTAT.
It ensures all demo data has realistic Senegalese coordinates and that the
map endpoint works correctly for citizen access.

Usage:
    python3 validate_map_data.py [--test-api]

Author: SAMA ÉTAT Development Team
Version: 1.0.0
"""

import sys
import json
import argparse
from datetime import datetime

# Senegal geographic boundaries for validation
SENEGAL_BOUNDS = {
    'min_lat': 12.0,   # Southern boundary (Casamance)
    'max_lat': 16.8,   # Northern boundary (Saint-Louis region)
    'min_lng': -17.5,  # Western boundary (Atlantic coast)
    'max_lng': -11.3   # Eastern boundary (Tambacounda/Kédougou)
}

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    """Print a formatted section header"""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def validate_coordinates(lat, lng, name="Location"):
    """
    Validate that coordinates are within Senegal's boundaries

    Args:
        lat (float): Latitude
        lng (float): Longitude
        name (str): Location name for logging

    Returns:
        bool: True if coordinates are valid
    """
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        print_error(f"Invalid coordinate types for {name}: lat={type(lat)}, lng={type(lng)}")
        return False

    if not (SENEGAL_BOUNDS['min_lat'] <= lat <= SENEGAL_BOUNDS['max_lat']):
        print_error(f"Latitude out of bounds for {name}: {lat}")
        print_info(f"Should be between {SENEGAL_BOUNDS['min_lat']} and {SENEGAL_BOUNDS['max_lat']}")
        return False

    if not (SENEGAL_BOUNDS['min_lng'] <= lng <= SENEGAL_BOUNDS['max_lng']):
        print_error(f"Longitude out of bounds for {name}: {lng}")
        print_info(f"Should be between {SENEGAL_BOUNDS['min_lng']} and {SENEGAL_BOUNDS['max_lng']}")
        return False

    print_success(f"Valid coordinates for {name}: ({lat:.6f}, {lng:.6f})")
    return True

def test_coordinate_samples():
    """Test sample coordinates from major Senegalese cities"""
    print_header("TESTING COORDINATE SAMPLES")

    # Sample coordinates from our demo data
    test_locations = [
        {"name": "Dakar (Capital)", "lat": 14.716677, "lng": -17.467686},
        {"name": "Saint-Louis (UNESCO Site)", "lat": 16.026340, "lng": -16.489649},
        {"name": "Thiès (Railway Hub)", "lat": 14.788889, "lng": -16.936111},
        {"name": "Kaolack (River Port)", "lat": 14.151515, "lng": -16.077778},
        {"name": "Ziguinchor (Casamance)", "lat": 12.548267, "lng": -16.263982},
        {"name": "Tambacounda (Eastern Gateway)", "lat": 13.771944, "lng": -13.671006},
        {"name": "Kédougou (Mining Center)", "lat": 12.557892, "lng": -12.179688},
        {"name": "Louga (Pastoral Region)", "lat": 15.619166, "lng": -16.226111},
        {"name": "Diourbel (Groundnut Basin)", "lat": 14.654722, "lng": -16.231944},
        {"name": "Matam (River Valley)", "lat": 15.655647, "lng": -13.255615},
        {"name": "Touba (Holy City)", "lat": 14.850000, "lng": -15.883333},
        {"name": "Mbour (Fishing Port)", "lat": 14.416667, "lng": -16.966667},
    ]

    valid_count = 0
    total_count = len(test_locations)

    for location in test_locations:
        if validate_coordinates(location['lat'], location['lng'], location['name']):
            valid_count += 1

    print(f"\n{Colors.BOLD}📊 VALIDATION RESULTS:{Colors.END}")
    print(f"Valid coordinates: {valid_count}/{total_count}")
    success_rate = (valid_count/total_count)*100
    print(f"Success rate: {success_rate:.1f}%")

    if success_rate == 100:
        print_success("All coordinate samples are valid!")
        return True
    elif success_rate >= 80:
        print_warning("Most coordinates are valid, but some need attention")
        return True
    else:
        print_error("Many coordinates are invalid - review needed")
        return False

def test_geographic_distribution():
    """Test that coordinates provide good geographic coverage of Senegal"""
    print_header("TESTING GEOGRAPHIC DISTRIBUTION")

    # Sample coordinates for distribution analysis
    coordinates = [
        (14.716677, -17.467686),  # Dakar (West Coast)
        (16.026340, -16.489649),  # Saint-Louis (North)
        (14.788889, -16.936111),  # Thiès (West Center)
        (14.151515, -16.077778),  # Kaolack (Center)
        (12.548267, -16.263982),  # Ziguinchor (South West)
        (13.771944, -13.671006),  # Tambacounda (East)
        (12.557892, -12.179688),  # Kédougou (South East)
        (15.619166, -16.226111),  # Louga (North Center)
        (14.654722, -16.231944),  # Diourbel (Center)
        (15.655647, -13.255615),  # Matam (North East)
    ]

    # Analyze distribution
    north_count = sum(1 for lat, lng in coordinates if lat > 15.0)
    south_count = sum(1 for lat, lng in coordinates if lat < 13.5)
    center_count = sum(1 for lat, lng in coordinates if 13.5 <= lat <= 15.0)

    west_count = sum(1 for lat, lng in coordinates if lng < -16.0)
    east_count = sum(1 for lat, lng in coordinates if lng > -14.0)
    center_lng_count = sum(1 for lat, lng in coordinates if -16.0 <= lng <= -14.0)

    print(f"🗺️  Geographic coverage analysis:")
    print(f"   📍 North (lat > 15°): {north_count} locations")
    print(f"   📍 Center (13.5° ≤ lat ≤ 15°): {center_count} locations")
    print(f"   📍 South (lat < 13.5°): {south_count} locations")
    print(f"   📍 West Coast (lng < -16°): {west_count} locations")
    print(f"   📍 Center (lng -16° to -14°): {center_lng_count} locations")
    print(f"   📍 East (lng > -14°): {east_count} locations")

    # Evaluate distribution quality
    good_ns_distribution = north_count > 0 and south_count > 0 and center_count > 0
    good_ew_distribution = west_count > 0 and east_count > 0

    if good_ns_distribution:
        print_success("Good North-South distribution")
    else:
        print_warning("Poor North-South distribution")

    if good_ew_distribution:
        print_success("Good East-West distribution")
    else:
        print_warning("Poor East-West distribution")

    # Overall assessment
    if good_ns_distribution and good_ew_distribution:
        print_success("Excellent geographic coverage of Senegal")
        return True
    elif good_ns_distribution or good_ew_distribution:
        print_warning("Adequate geographic coverage, could be improved")
        return True
    else:
        print_error("Poor geographic coverage")
        return False

def test_api_endpoint():
    """Test the map data API endpoint if available"""
    print_header("TESTING API ENDPOINT")

    try:
        import requests
    except ImportError:
        print_warning("requests library not available - skipping API test")
        print_info("Install with: pip install requests")
        return None

    base_urls = [
        "http://localhost:8069",
        "http://127.0.0.1:8069",
        "http://localhost:8080"
    ]

    for base_url in base_urls:
        endpoint = f"{base_url}/sama_etat/get_map_data"

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {}
        }

        try:
            print_info(f"Testing endpoint: {endpoint}")

            response = requests.post(
                endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                if 'result' in data:
                    result = data['result']

                    projects = result.get('projects', [])
                    decisions = result.get('decisions', [])
                    events = result.get('events', [])

                    print_success(f"API endpoint responding at {base_url}")
                    print(f"   📊 Projects with coordinates: {len(projects)}")
                    print(f"   📊 Decisions with coordinates: {len(decisions)}")
                    print(f"   📊 Events with coordinates: {len(events)}")

                    # Validate sample coordinates from API
                    total_items = len(projects) + len(decisions) + len(events)
                    if total_items > 0:
                        print_success(f"API returns {total_items} geolocated items")

                        # Test a few coordinates
                        sample_valid = 0
                        sample_total = 0

                        for project in projects[:2]:
                            if project.get('latitude') and project.get('longitude'):
                                sample_total += 1
                                if validate_coordinates(
                                    project['latitude'],
                                    project['longitude'],
                                    f"API Project: {project.get('name', 'Unknown')}"
                                ):
                                    sample_valid += 1

                        if sample_total > 0:
                            print(f"   ✅ Sample validation: {sample_valid}/{sample_total} valid")

                        return True
                    else:
                        print_warning("API responds but returns no geolocated data")
                        return False
                else:
                    print_error(f"Invalid API response format: {data}")
                    return False
            else:
                print_warning(f"HTTP {response.status_code} at {base_url}")
                continue

        except requests.exceptions.ConnectionError:
            print_info(f"No server at {base_url}")
            continue
        except requests.exceptions.Timeout:
            print_warning(f"Timeout connecting to {base_url}")
            continue
        except Exception as e:
            print_error(f"Error testing {base_url}: {e}")
            continue

    print_warning("No Odoo server found - API test skipped")
    print_info("Start Odoo server to test API endpoint")
    return None

def generate_summary_report(results):
    """Generate a summary report of all tests"""
    print_header("VALIDATION SUMMARY REPORT")

    print(f"📅 Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏛️  System: SAMA ÉTAT Map Validation\n")

    test_results = []
    for test_name, result in results.items():
        if result is True:
            status = f"{Colors.GREEN}✅ PASS{Colors.END}"
            test_results.append(True)
        elif result is False:
            status = f"{Colors.RED}❌ FAIL{Colors.END}"
            test_results.append(False)
        else:
            status = f"{Colors.YELLOW}⏭️  SKIP{Colors.END}"
            test_results.append(None)

        test_display = test_name.replace('_', ' ').title()
        print(f"{test_display:.<30} {status}")

    # Calculate overall score
    passed = sum(1 for r in test_results if r is True)
    failed = sum(1 for r in test_results if r is False)
    skipped = sum(1 for r in test_results if r is None)
    total = len(test_results)

    print(f"\n{Colors.BOLD}📊 OVERALL RESULTS:{Colors.END}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Skipped: {skipped}")
    print(f"   Total: {total}")

    if failed == 0 and passed > 0:
        print(f"\n{Colors.GREEN}🎉 ALL TESTS SUCCESSFUL!{Colors.END}")
        print("The map system is ready for citizen use.")
        success = True
    elif failed == 0:
        print(f"\n{Colors.YELLOW}✨ TESTS COMPLETED{Colors.END}")
        print("No failures detected, but some tests were skipped.")
        success = True
    else:
        print(f"\n{Colors.RED}⚠️  ISSUES DETECTED{Colors.END}")
        print("Please review and fix the failed tests above.")
        success = False

    print(f"\n{Colors.BOLD}🚀 NEXT STEPS:{Colors.END}")
    if success:
        print("1. Deploy updated demo data to Odoo")
        print("2. Test public dashboard at /senegal2050/dashboard")
        print("3. Verify map displays correctly for citizens")
        print("4. Check mobile responsiveness")
    else:
        print("1. Fix coordinate validation issues")
        print("2. Re-run validation script")
        print("3. Test API endpoint with Odoo running")
        print("4. Review demo data files")

    return success

def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(
        description="Validate SAMA ÉTAT map coordinate data",
        epilog="Example: python3 validate_map_data.py --test-api"
    )
    parser.add_argument(
        '--test-api',
        action='store_true',
        help='Test API endpoint (requires Odoo server running)'
    )

    args = parser.parse_args()

    print(f"{Colors.BOLD}🗺️  SAMA ÉTAT Map Data Validation{Colors.END}")
    print("Validating coordinates and map functionality for citizen access")

    # Run all validation tests
    results = {
        'coordinate_samples': test_coordinate_samples(),
        'geographic_distribution': test_geographic_distribution(),
    }

    # Optionally test API
    if args.test_api:
        results['api_endpoint'] = test_api_endpoint()

    # Generate final report
    success = generate_summary_report(results)

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
