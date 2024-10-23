import os
import requests
import sys
import csv

def fetch_groups(board_id, api_key):
    """
    Fetches groups from a specified Monday.com board.

    Args:
        board_id (str): The ID of the board.
        api_key (str): Your Monday.com API key.

    Returns:
        list: A list of groups with their IDs and titles.
    """
    query = """
    query ($boardId: [ID!]!) {
      boards(ids: $boardId) {
        groups {
          id
          title
        }
      }
    }
    """

    variables = {
        "boardId": [str(board_id)]  
    }

    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query, "variables": variables},
        headers=headers
    )

    if response.status_code != 200:
        print(f"Query failed with status code {response.status_code}")
        print("Response:", response.text)
        sys.exit(1)

    data = response.json()

    if 'errors' in data:
        print("GraphQL Errors:")
        for error in data['errors']:
            print(error['message'])
        sys.exit(1)

    boards = data.get('data', {}).get('boards', [])
    if not boards:
        print(f"No boards found with ID {board_id}.")
        sys.exit(1)

    board = boards[0]
    groups = board.get('groups', [])

    if not groups:
        print(f"No groups found in board {board_id}.")
        sys.exit(1)

    return groups

def fetch_items(board_id, group_id, api_key, limit=10):
    """
    Fetches items from a specific group within a Monday.com board.

    Args:
        board_id (str): The ID of the board.
        group_id (str): The ID of the group.
        api_key (str): Your Monday.com API key.
        limit (int): Number of items to fetch.

    Returns:
        list: A list of items with their details.
    """
    query = """
    query ($boardId: [ID!]!, $groupId: [String!]!, $limit: Int!) {
      boards(ids: $boardId) {
        groups(ids: $groupId) {
          id
          title
          items_page(limit: $limit) {
            items {
              id
              name
              column_values {
                id
                text
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "boardId": [str(board_id)],    # Ensure group_id and board id is a string within a list
        "groupId": [str(group_id)],  
        "limit": limit
    }

    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query, "variables": variables},
        headers=headers
    )

    if response.status_code != 200:
        print(f"Query failed with status code {response.status_code}")
        print("Response:", response.text)
        sys.exit(1)

    data = response.json()

    if 'errors' in data:
        print("GraphQL Errors:")
        for error in data['errors']:
            print(error['message'])
        sys.exit(1)

    boards = data.get('data', {}).get('boards', [])
    if not boards:
        print(f"No boards found with ID {board_id}.")
        sys.exit(1)

    board = boards[0]
    groups = board.get('groups', [])
    if not groups:
        print(f"No groups found with ID '{group_id}' in board {board_id}.")
        sys.exit(1)

    group = groups[0]
    items_page = group.get('items_page', {})
    items = items_page.get('items', [])

    if not items:
        print(f"No items found in group '{group_id}'.")
        return []

    return items

def export_items_to_csv(items, filename='scheduled_items.csv'):
    """
    Exports fetched items to a CSV file.

    Args:
        items (list): List of items to export.
        filename (str): The name of the CSV file.
    """
    if not items:
        print("No items to export.")
        return

    headers = ['Item ID', 'Item Name']
    column_ids = []
    for column in items[0]['column_values']:
        headers.append(column['id'])
        column_ids.append(column['id'])

    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for item in items:
            row = {
                'Item ID': item['id'],
                'Item Name': item['name']
            }
            for column in item['column_values']:
                row[column['id']] = column.get('text', '')
            writer.writerow(row)

    print(f"Exported {len(items)} items to {filename}.")