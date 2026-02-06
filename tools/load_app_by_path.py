import importlib.util, traceback, os
src_app_path = os.path.abspath(r'C:\web-dev\github-repos\Evident\backend\src\app.py')
print('path:', src_app_path, 'exists?', os.path.exists(src_app_path))
try:
    spec = importlib.util.spec_from_file_location('app', src_app_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print('loaded module, has app?', hasattr(mod, 'app'))
    if hasattr(mod, 'app'):
        print('app:', mod.app)
except Exception:
    traceback.print_exc()
