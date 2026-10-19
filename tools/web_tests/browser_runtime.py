"""Explicit disposable Chromium profile and guarded launch for CI."""
from contract import require_browser


def options(name):
    require_browser(name)
    return {'headless': True}


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
