from dynamicwidget import handlers


def widget_handler(rx):
    def decorator(view):
        handlers.default.register(rx, view)
        return view

    return decorator
