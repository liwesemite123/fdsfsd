import json
import logging
from pathlib import Path


class AccountStats:

    def __init__(self, stats_dir: str = "account_stats"):
        self.stats_dir = Path(stats_dir)
        self.stats_dir.mkdir(exist_ok=True)

    def _get_stats_file(self, account_name: str) -> Path:
        return self.stats_dir / f"{account_name}.json"

    def load_stats(self, account_name: str) -> dict:
        stats_file = self._get_stats_file(account_name)

        if stats_file.exists():
            try:
                with open(stats_file, encoding="utf-8") as f:
                    stats = json.load(f)
                    logging.info(f"📊 Загружена статистика для {account_name}: {stats['sent_count']}/{stats['total_target']} отписок")
                    return stats
            except Exception as e:
                logging.exception(f"❌ Ошибка загрузки статистики {account_name}: {e}")

        return {
            "account_name": account_name,
            "sent_count": 0,
            "total_target": 200,
            "is_completed": False
        }

    def save_stats(self, account_name: str, sent_count: int, total_target: int = 200, is_completed: bool = False) -> None:
        stats_file = self._get_stats_file(account_name)

        stats = {
            "account_name": account_name,
            "sent_count": sent_count,
            "total_target": total_target,
            "is_completed": is_completed
        }

        try:
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            logging.debug(f"💾 Статистика сохранена для {account_name}: {sent_count}/{total_target}")
        except Exception as e:
            logging.exception(f"❌ Ошибка сохранения статистики {account_name}: {e}")

    def is_completed(self, account_name: str) -> bool:
        stats = self.load_stats(account_name)
        return stats.get("is_completed", False)

    def get_sent_count(self, account_name: str) -> int:
        stats = self.load_stats(account_name)
        return stats.get("sent_count", 0)

    def reset_stats(self, account_name: str) -> None:
        self.save_stats(account_name, 0, 200, False)
        logging.info(f"🔄 Статистика сброшена для {account_name}")

    def delete_stats(self, account_name: str) -> None:
        stats_file = self._get_stats_file(account_name)
        if stats_file.exists():
            stats_file.unlink()
            logging.info(f"🗑️ Статистика удалена для {account_name}")
