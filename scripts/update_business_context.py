#!/usr/bin/env python3
"""
Script to update the business context JSON file.
This allows updating the business context without restarting the application.
"""
import json
import sys
from pathlib import Path

def update_business_context(new_context_file: str):
    """Update the business context from a JSON file."""
    # Define the path to the business context file
    context_file = Path(__file__).parent.parent / "data" / "business.json"
    
    # Ensure the directory exists
    context_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load the new context from the provided file
        with open(new_context_file, 'r', encoding='utf-8') as f:
            new_context = json.load(f)
        
        # Write the new context to the business context file
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(new_context, f, indent=2)
        
        # Verify that the file was written correctly by reading it back
        with open(context_file, 'r', encoding='utf-8') as f:
            written_context = json.load(f)
        
        print("SUCCESS: Business context updated successfully")
        print(f"Updated file: {context_file}")
        print(f"Business name: {written_context.get('business_name', 'N/A')}")
        print(f"Description: {written_context.get('description', 'N/A')}")
        return True
    except FileNotFoundError:
        print(f"ERROR: File not found: {new_context_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {new_context_file}: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Failed to update business context: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_business_context.py <path_to_context_json>")
        print("Example: python update_business_context.py ./data/business.json")
        sys.exit(1)
    
    context_file_path = sys.argv[1]
    success = update_business_context(context_file_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
