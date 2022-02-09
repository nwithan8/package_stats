import objectrest


class RubyGemDownloadStat:
    def __init__(self, date: str, downloads: int):
        self.date = date
        self.downloads = downloads


class RubyGemRankingStat:
    def __init__(self, date: str, rank: int):
        self.date = date
        self.rank = rank


def _api_call(gem_name: str, endpoint: str):
    return objectrest.get_json(f"https://bestgems.org/api/v1/gems/{gem_name}/{endpoint}.json")


def _process_download_stats(data: dict) -> list[RubyGemDownloadStat]:
    stats = []
    for item in data:
        stats.append(RubyGemDownloadStat(date=item['date'], downloads=item['total_downloads']))
    return stats


def _process_ranking_stats(data: dict) -> list[RubyGemRankingStat]:
    stats = []
    for item in data:
        stats.append(RubyGemRankingStat(date=item['date'], rank=item['total_ranking']))
    return stats


class RubyGem:
    def __init__(self, gem_name: str):
        self.gem_name = gem_name

    @property
    def daily_downloads(self):
        data = _api_call(gem_name=self.gem_name, endpoint="daily_downloads")
        return _process_download_stats(data)

    @property
    def total_downloads(self):
        data = _api_call(gem_name=self.gem_name, endpoint="total_downloads")
        return _process_download_stats(data)

    @property
    def daily_ranking(self):
        data = _api_call(gem_name=self.gem_name, endpoint="daily_ranking")
        return _process_ranking_stats(data)

    @property
    def total_ranking(self):
        data = _api_call(gem_name=self.gem_name, endpoint="total_ranking")
        return _process_ranking_stats(data)
