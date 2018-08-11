from examples.postgres import database


INSERT_STATEMENT = (
    "INSERT INTO mq.message(message_id, command, payload) "
    "VALUES (:message_id, :command, :payload)"
)

messages = [
    {'message_id': 'mid_1', 'command': 'test.command', 'payload': {'foo': 1}},
    {'message_id': 'mid_2', 'command': 'test.command', 'payload': {'foo': 2}},
    {'message_id': 'mid_3', 'command': 'test.command', 'payload': {'foo': 3}},
    {'message_id': 'mid_4', 'command': 'test.command', 'payload': {'foo': 4}},
]


with database.start_transaction() as session:
    session.execute(INSERT_STATEMENT, messages)
