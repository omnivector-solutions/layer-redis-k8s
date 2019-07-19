from charms.reactive import when, when_not
from charms.reactive.flags import set_flag
from charmhelpers.core.hookenv import (
    log,
    metadata,
    status_set,
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
