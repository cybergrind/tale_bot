
def xfile(afile, globalz=None, localz=None):
    with open(afile, "r") as fh:
        exec(fh.read(), globalz, localz)

try:
    xfile('settings_local.py', globals(), locals())
except Exception as mess:
    print(mess)

