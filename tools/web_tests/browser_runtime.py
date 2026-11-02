"""Explicit disposable Chromium profile and guarded launch for CI."""
from contract import require_browser
import os
import platform


def options(name):
    require_browser(name)
    result = {'headless': True}
    if platform.system() == 'Linux' and os.environ.get('PICROSS_WEB_SOFTWARE') == '1':
        # The book's real 3D path needs a rendered frame inside the unchanged
        # 0.3..0.7 reveal interval. Use the runner's Mesa OpenGL implementation;
        # implicit SwiftShader skipped that interval at ~360 ms/frame.
        # https://chromium.googlesource.com/angle/angle/+/main/doc/DebuggingTips.md
        result['args'] = ['--use-gl=angle', '--use-angle=gl']
    return result


def launch(pw, name, profile, **kwargs):
    require_browser(name)
    return pw.chromium.launch_persistent_context(profile, **options(name), **kwargs)


def graphics(page):
    return page.evaluate('''() => {
      const gl = document.querySelector('canvas').getContext('webgl2');
      if (!gl) throw new Error('No actual WebGL2 context');
      const debug = gl.getExtension('WEBGL_debug_renderer_info');
      return {version:gl.getParameter(gl.VERSION), renderer:gl.getParameter(gl.RENDERER),
        implementation:debug ? gl.getParameter(debug.UNMASKED_RENDERER_WEBGL) : 'not exposed'};
    }''')
