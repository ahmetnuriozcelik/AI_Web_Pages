#!/usr/bin/env python3
"""
WordPress AI Landing Page Generator
Generates WordPress pages using Claude API for content generation
"""

import os
import csv
import json
import sys
from dotenv import load_dotenv
from anthropic import Anthropic
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()


class WordPressClient:
    """Handles WordPress REST API operations"""
    
    def __init__(self, site_url, username, app_password):
        self.site_url = site_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, app_password)
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
    
    def get_template_page(self, page_id):
        """Fetch template page content"""
        try:
            response = requests.get(
                f"{self.api_base}/pages/{page_id}",
                auth=self.auth
            )
            response.raise_for_status()
            print(f"✓ Template page {page_id} fetched successfully")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching template page: {e}")
            raise
    
    def create_page(self, title, content, slug, status='draft'):
        """Create a new WordPress page"""
        try:
            data = {
                'title': title,
                'content': content,
                'slug': slug,
                'status': status
            }
            
            response = requests.post(
                f"{self.api_base}/pages",
                auth=self.auth,
                json=data
            )
            response.raise_for_status()
            page = response.json()
            print(f"✓ Page created: {page['link']}")
            return page
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating page: {e}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            raise


class ClaudeClient:
    """Handles Claude API content generation"""
    
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)
    
    def generate_content(self, integration_name, category):
        """Generate landing page content using Claude"""
        prompt = f"""You are a marketing copywriter creating a landing page for a Bucketlist integration with {integration_name}.

Bucketlist is an employee recognition and rewards platform. The integration with {integration_name} (a {category} tool) allows seamless connectivity between the two platforms.

Generate compelling, professional landing page content in JSON format with these exact fields:
- HEADLINE: A catchy, benefit-driven headline (max 10 words)
- SUBHEADLINE: A supporting subheadline that explains the value (max 20 words)
- FEATURE_1_TITLE: First key feature title (max 5 words)
- FEATURE_1_DESC: Description of first feature (max 25 words)
- FEATURE_2_TITLE: Second key feature title (max 5 words)
- FEATURE_2_DESC: Description of second feature (max 25 words)

Return ONLY valid JSON with these exact keys. No additional text or markdown."""

        try:
            print(f"  → Calling Claude API for {integration_name}...")
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = message.content[0].text
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if not json_match:
                raise ValueError("Could not extract JSON from Claude response")
            
            generated_content = json.loads(json_match.group(0))
            print(f"  ✓ Content generated for {integration_name}")
            
            return generated_content
        except Exception as e:
            print(f"  ✗ Error generating content: {e}")
            raise


def read_integrations_csv(file_path):
    """Read integrations from CSV file"""
    try:
        integrations = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            integrations = list(reader)
        
        print(f"✓ Loaded {len(integrations)} integrations from CSV")
        return integrations
    except Exception as e:
        print(f"✗ Error reading CSV file: {e}")
        raise


def replace_placeholders(template_content, integration, generated_content):
    """Replace placeholders in template with generated content"""
    
    # Replace all placeholders
    content = template_content
    content = content.replace('{{HEADLINE}}', generated_content.get('HEADLINE', ''))
    content = content.replace('{{SUBHEADLINE}}', generated_content.get('SUBHEADLINE', ''))
    content = content.replace('{{FEATURE_1_TITLE}}', generated_content.get('FEATURE_1_TITLE', ''))
    content = content.replace('{{FEATURE_1_DESC}}', generated_content.get('FEATURE_1_DESC', ''))
    content = content.replace('{{FEATURE_2_TITLE}}', generated_content.get('FEATURE_2_TITLE', ''))
    content = content.replace('{{FEATURE_2_DESC}}', generated_content.get('FEATURE_2_DESC', ''))
    content = content.replace('{{INTEGRATION_NAME}}', integration['integration_name'])
    content = content.replace('{{HERO_IMAGE}}', 'https://via.placeholder.com/800x400')
    
    return content


def main():
    """Main execution function"""
    
    print("\n=== WordPress AI Landing Page Generator ===\n")
    
    # Validate environment variables
    required_vars = [
        'WORDPRESS_SITE_URL',
        'WORDPRESS_USERNAME',
        'WORDPRESS_APP_PASSWORD',
        'WORDPRESS_TEMPLATE_PAGE_ID',
        'ANTHROPIC_API_KEY',
        'CSV_FILE_PATH'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"✗ Missing required environment variables: {', '.join(missing_vars)}")
        print("  Please create a .env file based on .env.example")
        sys.exit(1)
    
    # Initialize clients
    wp_client = WordPressClient(
        os.getenv('WORDPRESS_SITE_URL'),
        os.getenv('WORDPRESS_USERNAME'),
        os.getenv('WORDPRESS_APP_PASSWORD')
    )
    
    claude_client = ClaudeClient(os.getenv('ANTHROPIC_API_KEY'))
    
    # Get template page
    template_page_id = os.getenv('WORDPRESS_TEMPLATE_PAGE_ID')
    print(f"\n[1/4] Fetching template page (ID: {template_page_id})...")
    template_page = wp_client.get_template_page(template_page_id)
    template_content = template_page['content']['rendered']
    
    # Read integrations
    csv_file = os.getenv('CSV_FILE_PATH')
    print(f"\n[2/4] Reading integrations from {csv_file}...")
    integrations = read_integrations_csv(csv_file)
    
    # Process each integration
    print(f"\n[3/4] Generating content and creating pages...\n")
    created_pages = []
    
    for i, integration in enumerate(integrations, 1):
        print(f"Processing {i}/{len(integrations)}: {integration['integration_name']}")
        
        try:
            # Generate content with Claude
            generated_content = claude_client.generate_content(
                integration['integration_name'],
                integration['category']
            )
            
            # Replace placeholders
            page_content = replace_placeholders(
                template_content,
                integration,
                generated_content
            )
            
            # Create page title
            page_title = f"Bucketlist + {integration['integration_name']} Integration"
            
            # Create WordPress page
            page = wp_client.create_page(
                title=page_title,
                content=page_content,
                slug=integration['slug']
            )
            
            created_pages.append({
                'name': integration['integration_name'],
                'url': page['link']
            })
            
            print()
        
        except Exception as e:
            print(f"✗ Failed to process {integration['integration_name']}: {e}\n")
            continue
    
    # Summary
    print(f"[4/4] Summary\n")
    print(f"Successfully created {len(created_pages)} out of {len(integrations)} pages:\n")
    for page in created_pages:
        print(f"  • {page['name']}: {page['url']}")
    
    print("\n✓ Done!\n")


if __name__ == '__main__':
    main()
