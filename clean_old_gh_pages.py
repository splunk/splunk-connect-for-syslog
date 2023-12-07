import json
import pathlib
import dataclasses
import os


ROOT_DOC_DIR = pathlib.Path(__file__).parent.resolve()


@dataclasses.dataclass
class GithubVersion:
    title: str
    version: str
    aliases: list[str]

    @property
    def is_pr(self):
        return len(self.version) == 4 and self.version.isdigit()
    
    @property
    def disk_path(self):
        return ROOT_DOC_DIR / self.version
    

def load_github_versions() -> list[GithubVersion]:
    with open('versions.json') as f:
        return [GithubVersion(**version) for version in json.load(f)]
    

def overrive_github_versions(versions: list[GithubVersion]) -> None:
    with open('versions.json', 'w') as f:
        json.dump([dataclasses.asdict(version) for version in versions], f, indent=2)


if __name__ == "__main__":
    gh_versions = load_github_versions()

    new_gh_versions = []
    for gh_version in gh_versions:
        if gh_version.is_pr:
            try:
                os.system(f"git rm -rf {gh_version.version}")
            except Exception:
                print(f"Can't remove {gh_version.version}")
        else:
            new_gh_versions.append(gh_version)

    overrive_github_versions(new_gh_versions)
    os.system(f"git add versions.json")