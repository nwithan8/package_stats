from datetime import datetime, timedelta

import objectrest


def _date_to_str(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")


def _stats_api_call(package_str: str, start_date: datetime, end_date: datetime) -> dict:
    start = _date_to_str(start_date)
    end = _date_to_str(end_date)
    return objectrest.get_json(f"https://api.npmjs.org/downloads/range/{start}:{end}/{package_str}")


def _info_api_call(package_str: str) -> dict:
    return objectrest.get_json(f"https://registry.npmjs.org/{package_str}")


class NodePackageDownloadStat:
    def __init__(self, date: str, downloads: int):
        self.date = date
        self.downloads = downloads


class NodePackageVersion:
    def __init__(self, version_name: str, release_date: str, data: dict):
        self.version_name = version_name
        self.release_date = release_date
        self.downloads = data
        self._package_name = data["name"]


def _process_download_stats(data: dict) -> list[NodePackageDownloadStat]:
    stats = []
    for item in data:
        stats.append(NodePackageDownloadStat(date=item['day'], downloads=item['downloads']))
    return stats


def _sum_downloads(stats: list[NodePackageDownloadStat]) -> int:
    return sum([stat.downloads for stat in stats])


class NodePackage:
    def __init__(self, author_name: str, package_name: str):
        self.author_name = author_name
        self.package_name = package_name

    @property
    def package_str(self) -> str:
        return f"@{self.author_name}/{self.package_name}"

    @property
    def versions(self) -> list[NodePackageVersion]:
        data = _info_api_call(self.package_str)
        versions = []
        date_data = data['time']
        for name, version_info in data["versions"].items():
            date = date_data[name]
            versions.append(NodePackageVersion(version_name=name, release_date=date, data=version_info))
        return versions

    @property
    def latest_version(self) -> NodePackageVersion:
        versions = self.versions
        return versions[-1] if versions else None

    def downloads_between(self, start_date: datetime, end_date: datetime) -> list[NodePackageDownloadStat]:
        data = _stats_api_call(self.package_str, start_date, end_date)
        return _process_download_stats(data['downloads'])

    def downloads_since(self, date: datetime) -> list[NodePackageDownloadStat]:
        return self.downloads_between(date, datetime.now())

    def downloads_on(self, date: datetime) -> NodePackageDownloadStat:
        stats = self.downloads_between(date, date)
        return stats[0] if stats else None

    @property
    def downloads_today(self) -> int:
        stats = self.downloads_on(datetime.now())
        return _sum_downloads([stats]) if stats else 0

    @property
    def downloads_yesterday(self) -> int:
        stats = self.downloads_on(datetime.now() - timedelta(days=1))
        return _sum_downloads([stats]) if stats else 0

    @property
    def downloads_last_week(self) -> int:
        stats = self.downloads_since(datetime.now() - timedelta(days=7))
        return _sum_downloads(stats)

    @property
    def downloads_last_month(self) -> int:
        stats = self.downloads_since(datetime.now() - timedelta(days=30))
        return _sum_downloads(stats)

    @property
    def downloads_last_year(self) -> int:
        stats = self.downloads_since(datetime.now() - timedelta(days=365))
        return _sum_downloads(stats)
