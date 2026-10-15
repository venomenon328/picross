"""Explicit disposable browser profile for the GPU-less Linux CI runner."""
import os


def options(name):
    result = {'headless': True}
    if os.environ.get('PICROSS_WEB_SOFTWARE') == '1' and name == 'firefox':
        # Mozilla blocks some software drivers by default. This is confined to
        # the temporary reference profile, never a player/host requirement.
        result['firefox_user_prefs'] = {'webgl.force-enabled': True}
    return result


def graphics(page):
    return page.evaluate('''() => {
      const gl = document.querySelector('canvas').getContext('webgl2');
      if (!gl) throw new Error('No actual WebGL2 context');
      const debug = gl.getExtension('WEBGL_debug_renderer_info');
      return {version:gl.getParameter(gl.VERSION), renderer:gl.getParameter(gl.RENDERER),
        implementation:debug ? gl.getParameter(debug.UNMASKED_RENDERER_WEBGL) : 'not exposed'};
    }''')
