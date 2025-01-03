class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

    def __setitem__(self, key, value):
        pass
