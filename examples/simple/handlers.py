from mqcommand.dispatcher import Dispatcher


disp = Dispatcher(prefix='v1')


@disp.handles('create.resource')
def create_resource_v1(ctx, message):
    cmd = message['command']
    assert cmd == 'v1.create.resource'
    print(f'handlers.create_resource_v1: {message}')


@disp.handles('delete.resource')
def delete_resource_v1(ctx, message):
    cmd = message['command']
    assert cmd == 'v1.delete.resource'
    print(f'handlers.delete_resource_v1: {message}')
