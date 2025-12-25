import asyncio
import sys

from src.main_carrd import main

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Программа остановлена пользователем")
        sys.exit(0)
