def print_error(title, msg):
    print '======= ERROR!', title, '======='
    if type(msg) == 'list':
        for m in msg:
            print m
    else:
        print msg


def print_info(title, msg=None):
    print '-------', title, '-------'
    if type(msg) == 'list':
        for m in msg:
            print m
    elif msg:
        print msg


def print_object(o, fields=None, title=None):
    print '>>>>>>>', title, '<<<<<<<'
    if hasattr(o, '__dict__'):
        fields = fields or vars(o)
        # if fields:
        print o, [(field, getattr(o, field, "")) for field in fields]
    else:
        print o


def print_objects(obj, fields=None, title=None):
    print '+++++++', title, '+++++++'
    for o in obj:
        print_object(o, fields, title)
        # else:
        #     print o, [(k, vars(o)[k]) for k in vars(o)]


def get_error_msg(code, msg):
    return "status code: {0}\nerror message: {1}".format(code, msg)
