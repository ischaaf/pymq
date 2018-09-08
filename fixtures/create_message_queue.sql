/* add message queue */
CREATE SCHEMA mq;

CREATE TABLE mq.message (
  id              BIGSERIAL PRIMARY KEY,
  created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  message_id      TEXT NOT NULL,
  command         TEXT NOT NULL,
  payload         JSON DEFAULT 'null'::JSON NOT NULL,
  metadata        JSON DEFAULT '{}'::JSON NOT NULL,
  process_on      TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);


/* Optional table for easy deadlettering */
CREATE TABLE mq.deadletter (
  id              BIGINT,
  created_at      TIMESTAMP WITH TIME ZONE,
  updated_at      TIMESTAMP WITH TIME ZONE,
  message_id      TEXT,
  command         TEXT,
  payload         JSON,
  metadata        JSON,
  process_on      TIMESTAMP WITH TIME ZONE,
  error           TEXT
);

/* notify on queue insert */

CREATE OR REPLACE FUNCTION notify_on_new_message() RETURNS TRIGGER AS
$$
DECLARE
BEGIN

  IF TG_OP <> 'INSERT' THEN
    RAISE EXCEPTION 'unsupported TG_OP';
  END IF;

  PERFORM pg_notify(
    'mq_new_message'::text,
    NEW.message_id
  );
  RETURN NEW;
END;
$$
LANGUAGE 'plpgsql'
SECURITY DEFINER
COST 10;

DROP TRIGGER IF EXISTS notify_on_new_message ON mq.message;
CREATE TRIGGER notify_on_new_message
 AFTER INSERT
    ON mq.message
   FOR EACH ROW
       EXECUTE PROCEDURE notify_on_new_message();
