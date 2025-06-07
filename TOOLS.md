# Available MCP Tools

This document provides a comprehensive reference of all available Capsule CRM tools accessible through the MCP server.

## 👥 Contacts & People

### `list_contacts`
Returns a paginated list of contacts from your Capsule CRM.
- **Parameters:** `page`, `per_page`, `archived`, `since`

### `search_contacts` 
Fuzzy search for contacts by name, email, or organisation.
- **Parameters:** `keyword` (required), `page`, `per_page`

### `list_recent_contacts`
Returns contacts sorted by most recently contacted/updated.
- **Parameters:** `page`, `per_page`

### `get_contact`
Get detailed information about a specific contact.
- **Parameters:** `contact_id` (required)

## 💼 Sales & Opportunities

### `list_opportunities`
Returns a paginated list of all opportunities.
- **Parameters:** `page`, `per_page`, `since`

### `list_open_opportunities`
Returns open sales opportunities (excludes won/lost) ordered by expected close date.
- **Parameters:** `page`, `per_page`

### `get_opportunity`
Get detailed information about a specific opportunity.
- **Parameters:** `opportunity_id` (required)

## 🎫 Support Cases

### `list_cases`
Returns a paginated list of support cases.
- **Parameters:** `page`, `per_page`, `since`

### `search_cases`
Search support cases by keyword.
- **Parameters:** `keyword` (required), `page`, `per_page`

### `get_case`
Get detailed information about a specific support case.
- **Parameters:** `case_id` (required)

## ✅ Tasks

### `list_tasks`
Returns a paginated list of tasks.
- **Parameters:** `page`, `per_page`, `since`

### `get_task`
Get detailed information about a specific task.
- **Parameters:** `task_id` (required)

## 📝 Timeline & Entries

### `list_entries`
Returns timeline entries (notes, emails, calls, etc.).
- **Parameters:** `page`, `per_page`, `since`

### `get_entry`
Get detailed information about a specific timeline entry.
- **Parameters:** `entry_id` (required)

## 📋 Projects

### `list_projects`
Returns a paginated list of projects.
- **Parameters:** `page`, `per_page`, `since`

### `get_project`
Get detailed information about a specific project.
- **Parameters:** `project_id` (required)

## 🏷️ Organization & Configuration

### `list_tags`
Returns a paginated list of tags.
- **Parameters:** `page`, `per_page`

### `get_tag`
Get detailed information about a specific tag.
- **Parameters:** `tag_id` (required)

### `list_users`
Returns a paginated list of users.
- **Parameters:** `page`, `per_page`

### `get_user`
Get detailed information about a specific user.
- **Parameters:** `user_id` (required)

### `list_pipelines`
Returns a list of sales pipelines.

### `list_stages`
Returns a list of pipeline stages.

### `list_milestones`
Returns a list of opportunity milestones.

### `list_custom_fields`
Returns a list of custom field definitions.

## 🛍️ Products & Catalog

### `list_products`
Returns a paginated list of products.
- **Parameters:** `page`, `per_page`

### `list_categories`
Returns a paginated list of product categories.
- **Parameters:** `page`, `per_page`

## 💱 System Information

### `list_currencies`
Returns a list of supported currencies.

## Common Parameters

Most tools support these optional parameters:
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 50, max: 100)
- `since`: Filter by modification date (ISO8601 format, e.g. '2024-01-01T00:00:00Z')