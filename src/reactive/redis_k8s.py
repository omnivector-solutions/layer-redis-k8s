from charms.reactive import (
        endpoint_from_flag, set_flag, when, when_not,
)
from charmhelpers.core.hookenv import (
    log,
    metadata,
    network_get,
    status_set,
    relation_id,
)


from charms import layer


@when_not('layer.docker-resource.redis_image.fetched')
def fetch_image():
    layer.docker_resource.fetch('redis_image')


@when('layer.docker-resource.redis_image.available')
@when_not('redis.configured')
def config_redis():
    status_set('maintenance', 'Configuring redis container')

    spec = make_pod_spec()
    log('set pod spec:\n{}'.format(spec))
    layer.caas_base.pod_spec_set(spec)

    set_flag('redis.configured')


def make_pod_spec():
    with open('reactive/spec_template.yaml') as spec_file:
        pod_spec_template = spec_file.read()

    md = metadata()

    image_info = layer.docker_resource.get_info('redis_image')

    data = {
        'name': md.get('name'),
        'docker_image_path': image_info.registry_path,
        'docker_image_username': image_info.username,
        'docker_image_password': image_info.password,
    }
    return pod_spec_template % data


@when('redis.configured')
def redis_active():
    status_set('active', '')


@when('endpoint.redis-k8s.joined')
def configure_relation_data():
    endpoint = endpoint_from_flag('endpoint.redis-k8s.joined')

    info = network_get('redis', relation_id())
    log('network info {0}'.format(info))
    host = info['ingress-addresses'][0]
    if host == "":
        log("no service address yet")
        return
    else:
        endpoint.configure(host=host, port="6379")
