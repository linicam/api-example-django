from time import time

from drchrono.helpers import helper


def get_upload_file_name(instance, filename):
    helper.print_info('get upload file name')
    return '%s_%s' % (str(time()).replace('.', '_'), filename)
