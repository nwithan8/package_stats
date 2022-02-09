from datetime import datetime

import objectrest


def _date_to_str(date: datetime) -> str:
    return date.strftime('%Y-%m-%d')


def _pepy_info_api_call(package_name: str) -> dict:
    return objectrest.get_json(f'https://api.pepy.tech/api/v2/projects/{package_name}')


def _pypi_stats_info_api_call(package_name: str, endpoint: str, params: dict = None) -> dict:
    return objectrest.get_json(f'https://pypistats.org/api/packages/{package_name}/{endpoint}', params=params)


def _recent_stats(package_name: str, params: dict = None) -> dict:
    return _pypi_stats_info_api_call(package_name=package_name, endpoint='recent', params=params).get('data')


def _overall_stats(package_name: str, params: dict = None) -> dict:
    return _pypi_stats_info_api_call(package_name=package_name, endpoint='overall', params=params).get('data')


def _python_major_stats(package_name: str, params: dict = None) -> dict:
    return _pypi_stats_info_api_call(package_name=package_name, endpoint='python_major', params=params).get('data')


def _python_minor_stats(package_name: str, params: dict = None) -> dict:
    return _pypi_stats_info_api_call(package_name=package_name, endpoint='python_minor', params=params).get('data')


def _system_stats(package_name: str, params: dict = None) -> dict:
    return _pypi_stats_info_api_call(package_name=package_name, endpoint='system', params=params).get('data')


class PythonPackageDownloadStat:
    def __init__(self, date: str, downloads: int):
        self.date = date
        self.downloads = downloads


class PythonPackageVersion:
    def __init__(self, version_name: str, downloads: int, package_name: str):
        self.version_name = version_name
        self.recent_downloads = downloads
        self._package_name = package_name

    @property
    def daily_downloads(self) -> list[PythonPackageDownloadStat]:
        data = _pepy_info_api_call(package_name=self._package_name).get('downloads')
        stats = []
        for date, downloads in data.items():
            total = downloads.get(self.version_name, 0)
            stats.append(PythonPackageDownloadStat(date=date, downloads=total))
        return stats


class PythonPackage:
    def __init__(self, package_name: str):
        self.package_name = package_name

    @property
    def downloads_lifetime(self) -> int:
        return _pepy_info_api_call(package_name=self.package_name).get('total_downloads', 0)

    @property
    def versions(self) -> list[PythonPackageVersion]:
        data = _pepy_info_api_call(package_name=self.package_name).get('versions')
        versions = []
        for version_name in data.keys():
            downloads = self.recent_total_downloads_for_version(version_name=version_name)
            versions.append(
                PythonPackageVersion(version_name=version_name, downloads=downloads, package_name=self.package_name))
        return versions

    def downloads_on(self, date: datetime) -> int:
        date_str = _date_to_str(date=date)
        data = _overall_stats(package_name=self.package_name, params={'mirrors': False})
        for _, info in data.items():
            if info.get('date') == date_str:
                return info.get('downloads')
        return 0

    @property
    def downloads_yesterday(self) -> int:
        return _recent_stats(package_name=self.package_name).get('last_day', 0)

    @property
    def downloads_last_week(self) -> int:
        return _recent_stats(package_name=self.package_name).get('last_week', 0)

    @property
    def downloads_last_month(self) -> int:
        return _recent_stats(package_name=self.package_name).get('last_month', 0)

    @property
    def daily_downloads_totals(self) -> list[PythonPackageDownloadStat]:
        data = _pepy_info_api_call(package_name=self.package_name).get('downloads')
        stats = []
        for date, downloads in data.items():
            total = sum(downloads.values())
            stats.append(PythonPackageDownloadStat(date=date, downloads=total))
        return stats

    def daily_downloads_for_version(self, version_name: str) -> list[PythonPackageDownloadStat]:
        data = _pepy_info_api_call(package_name=self.package_name).get('downloads')
        stats = []
        for date, downloads in data.items():
            total = downloads.get(version_name, 0)
            stats.append(PythonPackageDownloadStat(date=date, downloads=total))
        return stats

    def recent_total_downloads_for_version(self, version_name: str) -> int:
        data = _pepy_info_api_call(package_name=self.package_name).get('downloads')
        total = 0
        for date, downloads in data.items():
            total += downloads.get(version_name, 0)
        return total

    def recent_total_downloads_by_operating_system(self, operating_system: str) -> int:
        data = _system_stats(package_name=self.package_name, params={'os': operating_system})
        total = 0
        for _, info in data.items():
            total += info.get('downloads', 0)
        return total

    def recent_total_downloads_by_python_version(self, python_version: str) -> int:
        data = _python_minor_stats(package_name=self.package_name, params={'version': python_version})
        total = 0
        for _, info in data.items():
            total += info.get('downloads', 0)
        return total
