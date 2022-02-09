import objectrest


def _info_api_call(package_str: str):
    return objectrest.get_json(
        f'https://packagist.org/packages/{package_str}.json').get('package')


def _stats_api_call(package_str: str, stats_type: str = "daily"):
    return objectrest.get_json(
        f'https://packagist.org/packages/{package_str}/stats/all.json?average={stats_type}')


def _version_stats_api_call(package_str: str, version: str, stats_type: str = "daily"):
    return objectrest.get_json(
        f'https://packagist.org/packages/{package_str}/stats/{version}.json?average={stats_type}')


class PHPPackageDownloadStat:
    def __init__(self, date: str, downloads: int):
        self.date = date
        self.downloads = downloads


def _process_stats(data: dict, value_key: str = None) -> list[PHPPackageDownloadStat]:
    stats = []
    labels = data.get('labels')
    values = data.get('values')
    if value_key:
        values = values.get(value_key)
    for i in range(0, len(labels)):
        stats.append(PHPPackageDownloadStat(date=labels[i], downloads=values[i]))
    return stats


class PHPPackageVersion:
    def __init__(self, version_name: str, data: dict):
        self.version_name = version_name
        self.data = data
        self._package_name = data.get('name')

    @property
    def daily_downloads(self) -> list[PHPPackageDownloadStat]:
        data = _version_stats_api_call(package_str=self._package_name, version=self.version_name, stats_type="daily")
        return _process_stats(data=data, value_key=self.version_name)

    @property
    def average_daily_downloads_weekly(self) -> list[PHPPackageDownloadStat]:
        data = _version_stats_api_call(package_str=self._package_name, version=self.version_name, stats_type="weekly")
        return _process_stats(data=data, value_key=self.version_name)

    @property
    def average_daily_downloads_monthly(self) -> list[PHPPackageDownloadStat]:
        data = _version_stats_api_call(package_str=self._package_name, version=self.version_name, stats_type="monthly")
        return _process_stats(data=data, value_key=self.version_name)


class PHPPackage:
    def __init__(self, package_author: str, package_name: str):
        self.package_author = package_author
        self.package_name = package_name

    @property
    def _package_str(self) -> str:
        return f"{self.package_author}/{self.package_name}"

    def _daily_stats(self, interval: str = "daily"):
        data = _stats_api_call(package_str=self._package_str, stats_type=interval)
        return _process_stats(data=data, value_key=self._package_str)

    def _daily_stats_by_version(self, version: str, interval: str = "daily"):
        data = _version_stats_api_call(version=version, package_str=self._package_str, stats_type=interval)
        return _process_stats(data=data, value_key=version)

    @property
    def versions(self) -> list[PHPPackageVersion]:
        data = _info_api_call(package_str=self._package_str).get('versions')
        versions = []
        for name, version_data in data.items():
            versions.append(PHPPackageVersion(version_name=name, data=version_data))
        return versions

    @property
    def latest_version(self) -> PHPPackageVersion:
        return self.versions[0]

    # General stats
    @property
    def daily_downloads(self) -> list[PHPPackageDownloadStat]:
        return self._daily_stats(interval="daily")

    @property
    def average_daily_downloads_weekly(self) -> list[PHPPackageDownloadStat]:
        return self._daily_stats(interval="weekly")

    @property
    def average_daily_downloads_monthly(self) -> list[PHPPackageDownloadStat]:
        return self._daily_stats(interval="monthly")

    @property
    def average_daily_downloads_lifetime(self) -> int:
        return _info_api_call(package_str=self._package_str).get('downloads').get(
            'daily')

    @property
    def average_monthly_downloads_lifetime(self) -> int:
        return _info_api_call(package_str=self._package_str).get('downloads').get(
            'monthly')

    @property
    def total_downloads_lifetime(self) -> int:
        return _info_api_call(package_str=self._package_str).get('downloads').get(
            'total')

    # Specific version stats
    def daily_downloads_by_version(self, version: str) -> list[PHPPackageDownloadStat]:
        return self._daily_stats_by_version(version=version, interval="daily")

    def average_daily_downloads_weekly_by_version(self, version: str) -> list[PHPPackageDownloadStat]:
        return self._daily_stats_by_version(version=version, interval="weekly")

    def average_daily_downloads_monthly_by_version(self, version: str) -> list[PHPPackageDownloadStat]:
        return self._daily_stats_by_version(version=version, interval="monthly")
