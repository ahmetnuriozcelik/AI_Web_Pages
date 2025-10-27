#!/usr/bin/env python3
"""
Test WordPress Connection
"""
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

def test_wordpress_connection():
    """Test WordPress REST API connection"""
    
    print("\n=== Testing WordPress Connection ===\n")
    
    # Get credentials from .env
    site_url = os.getenv('WORDPRESS_SITE_URL')
    username = os.getenv('WORDPRESS_USERNAME')
    app_password = os.getenv('WORDPRESS_APP_PASSWORD')
    template_page_id = os.getenv('WORDPRESS_TEMPLATE_PAGE_ID')
    
    # Validate environment variables
    if not all([site_url, username, app_password]):
        print("✗ Missing required environment variables")
        print(f"  WORDPRESS_SITE_URL: {'✓' if site_url else '✗'}")
        print(f"  WORDPRESS_USERNAME: {'✓' if username else '✗'}")
        print(f"  WORDPRESS_APP_PASSWORD: {'✓' if app_password else '✗'}")
        return False
    
    print(f"Site URL: {site_url}")
    print(f"Username: {username}")
    print(f"Template Page ID: {template_page_id}\n")
    
    # Test 1: Check if site is reachable
    print("[Test 1/3] Checking site accessibility...")
    try:
        response = requests.get(site_url, timeout=10)
        print(f"✓ Site is reachable (Status: {response.status_code})\n")
    except Exception as e:
        print(f"✗ Cannot reach site: {e}\n")
        return False
    
    # Test 2: Authenticate with REST API
    print("[Test 2/3] Testing authentication...")
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/users/me"
    auth = HTTPBasicAuth(username, app_password)
    
    try:
        response = requests.get(api_url, auth=auth, timeout=10)
        response.raise_for_status()
        user_data = response.json()
        print(f"✓ Authentication successful")
        print(f"  Logged in as: {user_data.get('name', 'Unknown')}")
        print(f"  User ID: {user_data.get('id', 'Unknown')}\n")
    except requests.exceptions.HTTPError as e:
        print(f"✗ Authentication failed: {e}")
        if e.response.status_code == 401:
            print("  Check your username and app password")
        print(f"  Response: {e.response.text}\n")
        return False
    except Exception as e:
        print(f"✗ Error during authentication: {e}\n")
        return False
    
    # Test 3: Check template page access
    if template_page_id:
        print("[Test 3/3] Checking template page access...")
        page_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages/{template_page_id}"
        
        try:
            response = requests.get(page_url, auth=auth, timeout=10)
            response.raise_for_status()
            page_data = response.json()
            print(f"✓ Template page accessible")
            print(f"  Page Title: {page_data.get('title', {}).get('rendered', 'Unknown')}")
            print(f"  Page ID: {page_data.get('id', 'Unknown')}\n")
        except requests.exceptions.HTTPError as e:
            print(f"✗ Cannot access template page: {e}")
            if e.response.status_code == 404:
                print("  Template page not found - check WORDPRESS_TEMPLATE_PAGE_ID")
            print(f"  Response: {e.response.text}\n")
            return False
        except Exception as e:
            print(f"✗ Error accessing template page: {e}\n")
            return False
    else:
        print("[Test 3/3] Skipping template page check (no ID provided)\n")
    
    print("=== All Tests Passed ✓ ===\n")
    return True

if __name__ == '__main__':
    success = test_wordpress_connection()
    exit(0 if success else 1)
