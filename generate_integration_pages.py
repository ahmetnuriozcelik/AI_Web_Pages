#!/usr/bin/env python3
"""
WordPress Integration Page Generator
Reads integration data from CSV and creates customized WordPress pages as drafts
Uses Claude LLM to generate benefit descriptions
"""

import csv
import requests
import json
from typing import Dict, List
import os
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

# WordPress credentials from environment variables
WORDPRESS_URL = os.getenv('WORDPRESS_SITE_URL')  # e.g., 'https://yourdomain.com'
WORDPRESS_USERNAME = os.getenv('WORDPRESS_USERNAME')
WORDPRESS_APP_PASSWORD = os.getenv('WORDPRESS_APP_PASSWORD')

# Claude API key
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')


def generate_benefit_description(partner_name: str, benefit_title: str) -> str:
    """Generate benefit description using Claude LLM"""
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""Write a concise, professional benefit description for a Bucketlist + {partner_name} integration.

The benefit title is: "{benefit_title}"

Write 1-2 sentences (maximum 25 words) that explains how this specific benefit helps companies. Focus on practical value for HR teams and employee experience.

Examples of good descriptions:
- "Populate employee data seamlessly in Bucketlist and keep it up to date"
- "Eliminate manual data transfer and significantly reduce the time needed to maintain recognition programs"
- "Utilize employee data for recognition programs, approvals, user roles and permissions, and more"

Return ONLY the description text, nothing else."""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=150,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text.strip()


def generate_faq_answers(partner_name: str) -> Dict[str, str]:
    """Generate FAQ answers using Claude LLM"""
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""Generate answers for these 5 FAQ questions about the Bucketlist + {partner_name} integration.

Questions:
1. Does the Bucketlist {partner_name} integration fully replace {partner_name}'s native recognition?
2. Will employees need to log in to another system?
3. Can we customize Bucketlist Rewards to fit our culture and teams?
4. What kind of reporting and analytics do we get?
5. What kind of rewards are available inside Bucketlist?

Guidelines:
- Keep answers concise (2-3 sentences max)
- Focus on practical benefits and ease of use
- For Q1, explain how Bucketlist upgrades/enhances the partner's capabilities
- For Q2, emphasize seamless integration
- For Q3-5, use general Bucketlist capabilities (not partner-specific)

Return ONLY 5 answers separated by "|||" with no additional text.
Example format: Answer 1|||Answer 2|||Answer 3|||Answer 4|||Answer 5"""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    answers_text = message.content[0].text.strip()
    answers = answers_text.split('|||')
    
    return {
        'FAQ_1_answer': answers[0].strip() if len(answers) > 0 else '',
        'FAQ_2_answer': answers[1].strip() if len(answers) > 1 else '',
        'FAQ_3_answer': answers[2].strip() if len(answers) > 2 else '',
        'FAQ_4_answer': answers[3].strip() if len(answers) > 3 else '',
        'FAQ_5_answer': answers[4].strip() if len(answers) > 4 else '',
    }


def read_csv_integrations(csv_file: str) -> List[Dict[str, str]]:
    """Read integration data from CSV file"""
    integrations = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            integrations.append(row)
    return integrations


def enrich_integration_with_descriptions(integration: Dict[str, str]) -> Dict[str, str]:
    """Generate benefit descriptions and FAQ answers using Claude for the integration"""
    
    partner_name = integration.get('Partner', '')
    
    print(f"  Generating benefit descriptions for {partner_name}...")
    
    # Generate descriptions for each benefit
    for i in range(1, 4):
        title_key = f'Benefit_{i}_title'
        desc_key = f'Benefit_{i}_description'
        
        benefit_title = integration.get(title_key, '')
        if benefit_title:
            description = generate_benefit_description(partner_name, benefit_title)
            integration[desc_key] = description
            print(f"    ✓ Benefit {i}: {benefit_title}")
        else:
            integration[desc_key] = ''
    
    # Generate FAQ answers
    print(f"  Generating FAQ answers...")
    faq_answers = generate_faq_answers(partner_name)
    integration.update(faq_answers)
    print(f"    ✓ Generated {len(faq_answers)} FAQ answers")
    
    return integration


def replace_template_variables(template: str, data: Dict[str, str]) -> str:
    """Replace template variables with actual data"""
    content = template
    
    # Replace all variables
    content = content.replace('{{Partner}}', data.get('Partner', ''))
    content = content.replace('{{Partner_subtitle}}', data.get('Partner_subtitle', ''))
    content = content.replace('{{Benefit_1_title}}', data.get('Benefit_1_title', ''))
    content = content.replace('{{Benefit_1_description}}', data.get('Benefit_1_description', ''))
    content = content.replace('{{Benefit_2_title}}', data.get('Benefit_2_title', ''))
    content = content.replace('{{Benefit_2_description}}', data.get('Benefit_2_description', ''))
    content = content.replace('{{Benefit_3_title}}', data.get('Benefit_3_title', ''))
    content = content.replace('{{Benefit_3_description}}', data.get('Benefit_3_description', ''))
    
    # Replace FAQ answers
    for i in range(1, 6):
        faq_key = f'FAQ_{i}_answer'
        content = content.replace('{{' + faq_key + '}}', data.get(faq_key, ''))
    
    return content


def read_template(template_file: str) -> str:
    """Read the HTML template file"""
    with open(template_file, 'r', encoding='utf-8') as f:
        return f.read()


def create_wordpress_draft(title: str, content: str) -> Dict:
    """Create a draft page in WordPress using REST API"""
    
    if not all([WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD]):
        raise ValueError("WordPress credentials not configured. Check .env file.")
    
    api_url = f"{WORDPRESS_URL}/wp-json/wp/v2/pages"
    
    auth = (WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD)
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        'title': title,
        'content': content,
        'status': 'draft'  # Save as draft
    }
    
    response = requests.post(api_url, auth=auth, headers=headers, json=data)
    
    if response.status_code == 201:
        return {'success': True, 'data': response.json()}
    else:
        return {'success': False, 'error': response.text, 'status_code': response.status_code}


def generate_pages_from_csv(csv_file: str, template_file: str, preview_only: bool = False):
    """Main function to generate WordPress pages from CSV"""
    
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables. Please add it to your .env file.")
    
    print("Reading template...")
    template = read_template(template_file)
    
    print("Reading integrations from CSV...")
    integrations = read_csv_integrations(csv_file)
    
    print(f"Found {len(integrations)} integrations to process.\n")
    
    results = []
    
    for i, integration in enumerate(integrations, 1):
        partner_name = integration.get('Partner', 'Unknown')
        print(f"\n[{i}/{len(integrations)}] Processing: {partner_name}")
        
        # Generate benefit descriptions using Claude
        integration = enrich_integration_with_descriptions(integration)
        
        # Generate page title
        page_title = f"Bucketlist | {partner_name} Integration"
        
        # Replace template variables
        page_content = replace_template_variables(template, integration)
        
        # Preview mode - just show the generated content
        if preview_only:
            print(f"\n  Generated content for {partner_name}:")
            print(f"  Title: {page_title}")
            for i in range(1, 4):
                print(f"  Benefit {i}: {integration.get(f'Benefit_{i}_title', '')}")
                print(f"    → {integration.get(f'Benefit_{i}_description', '')}")
            result = {'success': True, 'data': {'id': 'preview', 'link': 'N/A (preview mode)'}}
        else:
            # Create WordPress draft
            print(f"  Creating WordPress draft...")
            result = create_wordpress_draft(page_title, page_content)
        
        if result['success']:
            page_id = result['data'].get('id')
            page_url = result['data'].get('link')
            print(f"  ✓ Success! Page ID: {page_id}")
            print(f"  URL: {page_url}")
        else:
            print(f"  ✗ Failed: {result.get('error')}")
        
        results.append({
            'partner': partner_name,
            'success': result['success'],
            'result': result
        })
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print("\n" + "="*50)
    print(f"Summary: {successful}/{len(results)} pages created successfully")
    print("="*50)
    
    return results


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python generate_integration_pages.py <csv_file> <template_file> [--preview]")
        print("Example: python generate_integration_pages.py integrations.csv template.html")
        print("         python generate_integration_pages.py integrations.csv template.html --preview")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    template_file = sys.argv[2]
    preview_only = '--preview' in sys.argv
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)
    
    if not os.path.exists(template_file):
        print(f"Error: Template file not found: {template_file}")
        sys.exit(1)
    
    if preview_only:
        print("\n*** PREVIEW MODE - No WordPress pages will be created ***\n")
    
    generate_pages_from_csv(csv_file, template_file, preview_only)
