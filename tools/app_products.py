"""Two fixed program identities. Never configured by checkout or update requests."""
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Product:
    key: str
    title: str
    executable: str
    install_directory: str
    state_directory: str
    anchor: str

    @property
    def package(self): return 'tools/' + ('production_workspace' if self.key == 'pw' else 'puzzle_editor')
    @property
    def source(self): return Path(__file__).resolve().parents[1] / self.package
    @property
    def icon_resource(self): return 'assets/launcher.ico' if self.key == 'pw' else 'assets/editor.ico'
    @property
    def registry(self): return 'Software\\' + self.state_directory
    @property
    def marker(self): return 'Global\\' + self.state_directory + '.Running.'
    @property
    def environment(self): return self.key + '-app-release'
    @property
    def prefix(self): return self.key + '-v'
    @property
    def provenance(self): return 'picross-' + self.key + '-release-v1'
    @property
    def signed(self): return 'picross-' + self.key + '-release-v2'
    @property
    def signature(self): return 'picross-' + self.key + '-signature-v1'
    @property
    def trust(self): return 'picross-' + self.key + '-trust-v1'
    @property
    def line(self): return tuple(map(int, self.anchor.split('.')[:2]))

PW = Product('pw', 'Picross-Produktionsassistent', 'Picross-Start', 'Picross-Produktionsassistent', 'PicrossProductionWorkspace', '0.1.0')
PE = Product('pe', 'Picross-Bestandseditor', 'Picross-Bestandseditor', 'PicrossPuzzleEditor', 'PicrossPuzzleEditor', '0.2.0')
