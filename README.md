# WordPress AI Landing Page Generator

An AI-powered tool that generates multiple WordPress landing pages using Claude API for content generation.

## Overview

This Python script automates the creation of WordPress landing pages by:
1. Reading integration data from a CSV file
2. Using Claude AI to generate compelling, customized content for each integration
3. Fetching a WordPress template page via REST API
4. Replacing placeholders with AI-generated content
5. Creating draft pages in WordPress

## Prerequisites

- Python 3.7 or higher
- WordPress site with REST API enabled
- WordPress Application Password (not your regular password)
- Anthropic API key

## Installation

### 1. Clone or download this project

```bash
cd /Users/ahmetnuriozcelik/Documents/AI_Web_Pages
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Create WordPress Application Password

1. Log in to your WordPress admin dashboard
2. Go to **Users** → **Profile**
3. Scroll down to **Application Passwords**
4. Enter a name (e.g., "AI Page Generator")
5. Click **Add New Application Password**
6. Copy the generated password (it will look like: `xxxx xxxx xxxx xxxx xxxx xxxx`)

### 2. Find your Template Page ID

1. Go to **Pages** in WordPress admin
2. Hover over your template page
3. Look at the URL in your browser's status bar
4. The ID is the number after `post=` (e.g., `post=123` means ID is `123`)

### 3. Set up environment variables

Copy the example file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
WORDPRESS_SITE_URL=https://yoursite.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
WORDPRESS_TEMPLATE_PAGE_ID=123
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
CSV_FILE_PATH=./integrations.csv
```

**Important:** 
- Use your Application Password, NOT your regular WordPress password
- Remove spaces from the Application Password or keep them as shown
- Use the full site URL including `https://`

## Template Page Setup

Create a WordPress page with the following placeholders:

```html
<!-- Hero Section -->
<h1>{{HEADLINE}}</h1>
<h2>{{SUBHEADLINE}}</h2>
<img src="{{HERO_IMAGE}}" alt="Hero Image">

<!-- Features Section -->
<div class="features">
  <div class="feature">
    <h3>{{FEATURE_1_TITLE}}</h3>
    <p>{{FEATURE_1_DESC}}</p>
  </div>
  <div class="feature">
    <h3>{{FEATURE_2_TITLE}}</h3>
    <p>{{FEATURE_2_DESC}}</p>
  </div>
</div>

<!-- CTA Section -->
<button>Connect Bucketlist with {{INTEGRATION_NAME}}</button>
```

## CSV File Format

Your `integrations.csv` should have these columns:

```csv
integration_name,category,slug
Slack,Communication,bucketlist-slack-integration
BambooHR,HRIS,bucketlist-bamboohr-integration
```

- **integration_name**: Name of the integration (e.g., "Slack")
- **category**: Category/type (e.g., "Communication", "HRIS")
- **slug**: URL-friendly slug for the page

## Usage

### Run the script

```bash
python generate_pages.py
```

### Expected Output

```
=== WordPress AI Landing Page Generator ===

[1/4] Fetching template page (ID: 123)...
✓ Template page 123 fetched successfully

[2/4] Reading integrations from ./integrations.csv...
✓ Loaded 2 integrations from CSV

[3/4] Generating content and creating pages...

Processing 1/2: Slack
  → Calling Claude API for Slack...
  ✓ Content generated for Slack
✓ Page created: https://yoursite.com/bucketlist-slack-integration/

Processing 2/2: BambooHR
  → Calling Claude API for BambooHR...
  ✓ Content generated for BambooHR
✓ Page created: https://yoursite.com/bucketlist-bamboohr-integration/

[4/4] Summary

Successfully created 2 out of 2 pages:

  • Slack: https://yoursite.com/bucketlist-slack-integration/
  • BambooHR: https://yoursite.com/bucketlist-bamboohr-integration/

✓ Done!
```

## Project Structure

```
AI_Web_Pages/
├── generate_pages.py     # Main script
├── requirements.txt      # Python dependencies
├── integrations.csv      # Integration data
├── .env                  # Your credentials (not in git)
├── .env.example          # Template for credentials
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Troubleshooting

### Authentication Errors

- Ensure you're using an **Application Password**, not your regular password
- Check that your username is correct
- Verify the WordPress REST API is enabled on your site

### Template Page Not Found

- Double-check the page ID in your `.env` file
- Ensure the page exists and isn't in the trash

### Claude API Errors

- Verify your Anthropic API key is correct
- Check you have sufficient API credits
- Ensure you have access to Claude 3.5 Sonnet

### CSV Reading Errors

- Check that `integrations.csv` exists in the same directory
- Ensure the CSV has the correct column headers
- Verify the file encoding is UTF-8

## Customization

### Modify the Content Prompt

Edit the `generate_content` method in `generate_pages.py` to customize what Claude generates.

### Add More Placeholders

1. Add placeholders to your WordPress template (e.g., `{{NEW_FIELD}}`)
2. Update the Claude prompt to generate that field
3. Add the replacement in the `replace_placeholders` function

### Change Page Status

By default, pages are created as drafts. To publish immediately:

```python
page = wp_client.create_page(
    title=page_title,
    content=page_content,
    slug=integration['slug'],
    status='publish'  # Change from 'draft' to 'publish'
)
```

## License

MIT

## Support

For issues or questions, please refer to:
- [WordPress REST API Documentation](https://developer.wordpress.org/rest-api/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
