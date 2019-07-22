from charms.reactive import when, when_not
from charms.reactive import set_flag, clear_flag
from charms.reactive import Endpoint


class RedisProvides(Endpoint):

    @when('endpoint.{endpoint_name}.joined')
    def joined(self):
        set_flag(self.expand_name('available'))

    @when_not('endpoint.{endpoint_name}.joined')
    def broken(self):
        clear_flag(self.expand_name('available'))

    def configure(self, host, port, password=None):
        for relation in self.relations:
            ctxt = {'host': host, 'port': port}
            if password:
                ctxt['password'] = password
            relation.to_publish.update(ctxt)
