# Gebundene Runtime-Lizenztexte

UnverÃ¤nderte Originaltexte der tatsÃ¤chlich verwendeten CPython-3.13.14-x64-
Komponenten, ergÃ¤nzend zu Python-, Pillow- und PyInstaller-Lizenzen aus deren
Distributionen. Die Quelle wird beim Bau nicht neu heruntergeladen.

| Datei | Gebundene PrimÃ¤rquelle |
| --- | --- |
| [Tcl-8.6.15.txt](Tcl-8.6.15.txt) | [Tcl core-8-6-15](https://github.com/tcltk/tcl/blob/core-8-6-15/license.terms) |
| [OpenSSL-3.0.21.txt](OpenSSL-3.0.21.txt) | [OpenSSL 3.0.21](https://github.com/openssl/openssl/blob/openssl-3.0.21/LICENSE.txt) |
| [Expat-2.8.1.txt](Expat-2.8.1.txt) | [Expat R_2_8_1](https://github.com/libexpat/libexpat/blob/R_2_8_1/expat/COPYING) |
| [zlib-1.3.1.txt](zlib-1.3.1.txt) | [zlib v1.3.1](https://github.com/madler/zlib/blob/v1.3.1/LICENSE) |
| [bzip2-1.0.8.txt](bzip2-1.0.8.txt) | [CPython-Quelldependenz bzip2](https://github.com/python/cpython-source-deps/blob/bzip2-1.0.8/LICENSE) |
| [xz-5.2.5.txt](xz-5.2.5.txt) | [CPython-Quelldependenz xz](https://github.com/python/cpython-source-deps/blob/xz-5.2.5/COPYING) |
| [mpdecimal-4.0.0.txt](mpdecimal-4.0.0.txt) | [CPython-Quelldependenz mpdecimal](https://github.com/python/cpython-source-deps/blob/mpdecimal-4.0.0/COPYRIGHT.txt) |

Die [Windows-Dependenzbindung von CPython 3.13.14](https://github.com/python/cpython/blob/v3.13.14/PCbuild/get_externals.bat)
fÃ¼hrt bzip2 1.0.8, xz/liblzma 5.2.5 und libffi 3.4.4; Python.txt enthÃ¤lt bereits
den libffi-Text und die Hinweise zu Microsoft Distributable Code.
Der Build liest Tcl/OpenSSL/Expat/zlib/mpdecimal tatsÃ¤chlich aus der Laufzeit
und verweigert unpassende Versionen. In xz ist allein die public-domain-
liblzma eingebunden, keine GPL-Kommandozeilenwerkzeuge oder Buildskripte.
Tk erhÃ¤lt seinen Originaltext zusÃ¤tzlich aus der konkreten Pythoninstallation.
