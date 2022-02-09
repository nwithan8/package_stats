import objectrest


def _info_api_call(package_name: str) -> dict:
    return objectrest.get_json(f"https://azuresearch-usnc.nuget.org/query?q={package_name}&prerelease=false")


def _stats_api_call(package_name: str, params: str = "") -> dict:
    return objectrest.get_json(
        f'https://www.nuget.org/stats/reports/packages/{package_name}{params}')


def _version_api_call(package_name: str) -> dict:
    params = "?groupBy=Version"
    return _stats_api_call(package_name, params)


def _client_api_call(package_name: str) -> dict:
    params = "?groupBy=ClientVersion"
    return _stats_api_call(package_name, params)


def _version_client_api_call(package_name: str) -> dict:
    params = "?groupBy=ClientVersion&groupBy=Version"
    return _stats_api_call(package_name, params)


class NugetPackageClient:
    def __init__(self, package_name: str, client_version: str, total_downloads: int):
        self._package_name = package_name
        self.client_version = client_version
        self.total_downloads = total_downloads


class NugetPackageVersion:
    def __init__(self, package_name: str, version: str, total_downloads: int, client_data: dict = None):
        self._package_name = package_name
        self.version = version
        self.total_downloads = total_downloads
        self.clients = []
        if client_data:
            for client in client_data:
                self.clients.append(NugetPackageClient(package_name, client["ClientVersion"], client["Downloads"]))


class NugetPackage:
    def __init__(self, package_name: str):
        self.package_name = package_name

    @property
    def versions(self) -> list[NugetPackageVersion]:
        data = _info_api_call(self.package_name).get('data')[0]
        version_data = data.get('versions', {})
        versions = []
        for version in version_data.items():
            versions.append(NugetPackageVersion(package_name=self.package_name, version=version.get('version'),
                                                total_downloads=version.get('downloads')))
        return versions

    @property
    def latest_version(self) -> NugetPackageVersion:
        versions = self.versions
        return versions[-1]

    @property
    def detailed_versions(self) -> list[NugetPackageVersion]:
        version_data = _version_api_call(self.package_name).get('Table')
        client_version_data = _version_client_api_call(self.package_name).get('Table')
        versions = []
        for entry in version_data:
            name = entry[0].get('Data')
            download_count = entry[1].get('Data')
            try:
                download_count = int(download_count)
            except ValueError:
                download_count = 0

            client_data = {}
            version_starts_at = 0
            for i in range(0, len(client_version_data)):
                if client_version_data[i][0] is None:
                    pass
                elif client_version_data[i][0].get('Data') == name:
                    # store the first entry for this version
                    client_data[client_version_data[i][1].get('Data')] = int(client_version_data[i][2].get('Data'))
                    version_starts_at = i
                    break
            # store all subsequent entries for this version until we find a new version
            for client_entry in client_version_data[version_starts_at + 1:]:
                if client_entry[0] is None:
                    client_data[client_entry[1].get('Data')] = int(client_entry[2].get('Data'))
                else:
                    break

            versions.append(
                NugetPackageVersion(package_name=self.package_name, version=name, total_downloads=download_count,
                                    client_data=client_data))
        return versions

    @property
    def clients(self) -> list[NugetPackageClient]:
        data = _client_api_call(self.package_name).get('Table')
        clients = []
        for entry in data:
            name = entry[0].get('Data')
            download_count = entry[1].get('Data')
            try:
                download_count = int(download_count)
            except ValueError:
                download_count = 0
            clients.append(
                NugetPackageClient(package_name=self.package_name, client_version=name, total_downloads=download_count))
        return clients

    # "recent" is the last 6 weeks

    @property
    def recent_total_downloads(self) -> int:
        data = _version_api_call(self.package_name).get('Table')
        total = 0
        for entry in data:
            total += int(entry[1].get('Data'))
        return total

    def recent_total_downloads_by_version(self, version: str) -> int:
        versions = self.versions
        for v in versions:
            if v.version == version:
                return v.total_downloads
        return 0

    def recent_total_downloads_by_client(self, client: str) -> int:
        clients = self.clients
        for c in clients:
            if c.client_version == client:
                return c.total_downloads
        return 0
