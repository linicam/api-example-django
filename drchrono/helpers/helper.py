import re


def print_error(title, *args):
    print '======= ERROR!', title, '======='
    for arg in args:
        print arg


def print_info(title, *args):
    print '-------', title, '-------'
    for arg in args:
        print arg


def print_object(o, fields=None, title=None):
    if not title:
        title = type(o)
    print '>>>>>>>', title, '<<<<<<<'
    if hasattr(o, '__dict__'):
        fields = fields or vars(o)
        for field in fields:
            print field, getattr(o, field, "")
    else:
        print o


def print_objects(obj, fields=None, title=None):
    print '+++++++', title, '+++++++'
    for o in obj:
        print_object(o, fields, title)


def get_error_msg(code, msg):
    return "status code: {0}\nerror message: {1}".format(code, msg)


def check_cell_phtone(s):
    reg = re.compile(r'^[(]?[\d]{3}[-) ]?[\d]{3}[- ]?[\d]{4}$')
    return reg.match(s) is not None or len(s) == 0
