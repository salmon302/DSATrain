"""
Simple script to add solutions to existing problems
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.collectors.enhanced_data_expander import EnhancedDataExpander

async def main():
    expander = EnhancedDataExpander()
    await expander.expand_dataset()

if __name__ == "__main__":
    asyncio.run(main())
