#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiDjangoProject.settings')

    # 强制使用ASGI
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        print("检测到runserver命令，检查ASGI配置...")
        import django
        django.setup()
        from django.conf import settings
        if hasattr(settings, 'ASGI_APPLICATION'):
            print(f"ASGI应用: {settings.ASGI_APPLICATION}")
        else:
            print("警告: 未找到ASGI_APPLICATION设置")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
