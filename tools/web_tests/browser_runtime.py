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
        # Use the installed full Chromium's documented new headless path and
        # allow the Xvfb/Mesa driver instead of the shell's forced SwiftShader.
        # https://playwright.dev/python/docs/browsers#chromium-new-headless-mode
        # https://chromium.googlesource.com/chromium/src/+/main/docs/gpu/using-gpu-hardware-in-headless-chrome.md
        result.update(channel='chromium', args=['--enable-gpu', '--use-gl=angle', '--use-angle=gl'])
    return result


def launch(pw, name, profile, **kwargs):
    require_browser(name)
    return pw.chromium.launch_persistent_context(profile, **options(name), **kwargs)


def graphics_diagnostics(context):
    """Read actual driver/feature decisions even if creating WebGL2 fails."""
    session = context.browser.new_browser_cdp_session()
    try:
        gpu = session.send('SystemInfo.getInfo')['gpu']
        return {key:gpu.get(key) for key in ('devices','auxAttributes','featureStatus')}
    finally:
        session.detach()


def graphics(page):
    return page.evaluate('''() => {
      const gl = document.querySelector('canvas').getContext('webgl2');
      if (!gl) throw new Error('No actual WebGL2 context');
      const debug = gl.getExtension('WEBGL_debug_renderer_info');
      return {version:gl.getParameter(gl.VERSION), renderer:gl.getParameter(gl.RENDERER),
        implementation:debug ? gl.getParameter(debug.UNMASKED_RENDERER_WEBGL) : 'not exposed'};
    }''')
