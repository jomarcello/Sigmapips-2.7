#!/usr/bin/env python3

def add_trades_method(file_path):
    print(f"Adding _get_signal_related_trades method to {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Find the position to insert the method
    insert_position = -1
    for i, line in enumerate(lines):
        if "# Initialize logging early in the application startup" in line:
            insert_position = i
            break
    
    if insert_position == -1:
        print("Could not find insertion point")
        return
    
    # Create the properly indented method
    method_lines = [
        "    async def _get_signal_related_trades(self, signal_id):\n",
        "        \"\"\"Retrieve related trades from the database\"\"\"\n",
        "        try:\n",
        "            # Fetch the related trades data from the database\n",
        "            trades_data = await self.db.get_related_trades(signal_id)\n",
        "            \n",
        "            if trades_data:\n",
        "                return trades_data\n",
        "            else:\n",
        "                logger.warning(f\"No related trades data found for signal ID {signal_id}\")\n",
        "                return None\n",
        "        except Exception as e:\n",
        "            logger.error(f\"Error retrieving related trades: {str(e)}\")\n",
        "            logger.exception(e)\n",
        "            return None\n",
        "\n",
    ]
    
    # Insert the method at the appropriate position
    lines[insert_position:insert_position] = method_lines
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)
    
    print(f"Added _get_signal_related_trades method to {file_path}")

if __name__ == "__main__":
    add_trades_method("trading_bot/main.py") 