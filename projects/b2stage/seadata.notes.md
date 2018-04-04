
## notes

**PRIORITIES** ::MVP::

* credentials
* list the zip files
- HTTP API logging into elastisearch
    - agree on the username field
- Restricted data prototype
- unwanted characters in filenames (ONLY CHECK)
- push 1 thousand files in production from RAR
- more than one zip file in one unrestricted order

---

3.6.5-alpine3.7

---

logging for maris:
    - receive request
    - end request
        - api maris call
        - otherwise ending request + status

---

```json
{
  "BATCH_DIR_PATH": "/usr/share/batch",
  "DB_PASSWORD": ***,
  "DB_USERNAME": "blabla",
  "JSON_INPUT": "...",
  "LOGS_ENABLE": "1",
  "LOGS_EXCHANGE": "eudat_qc",
  "LOGS_HOST": "sdc-b2host-test.dkrz.de",
  "LOGS_PASSWORD": ***,
  "LOGS_PORT": "5672",
  "LOGS_QUEUE": "maris_elk_test",
  "LOGS_USER": "blabla",
  "LOGS_VHOST": "elkstack_tests",
}
```