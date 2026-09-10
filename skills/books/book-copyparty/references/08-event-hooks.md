# Event Hooks (copyparty)

Trigger a program (or ZeroMQ message) on upload / move-rename / delete, before
or after the event. See `--help-hooks` for all flags. Examples in `bin/hooks/`.

## ZeroMQ hooks (`--xau`)

- `--xau zmq:pub:tcp://*:5556` → PUB to all connected SUB clients
- `--xau t3,zmq:push:tcp://*:5557` → PUSH to one PULL client (t3 = 3s timeout)
- `--xau t3,j,zmq:req:tcp://localhost:5555` → REQ to REP, `j` = extended info as
  JSON
- Config form (additive — all take effect):

  ```yaml
  [global]
    xau: zmq:pub:tcp://*:5556
    xau: t3,zmq:push:tcp://*:5557
    xau: t3,j,zmq:req:tcp://localhost:5555
  ```

- Receive with `bin/zmq-recv.py`.

## Upload events (older, more powerful — `bin/mtag/`)

Volflag-driven, non-blocking, multithreaded, gives FFmpeg/mtp tags, fires only
on new unique files (not dupes). Occupies parsing threads → fork expensive work
or set `kn` (kill-on-timeout) to let copyparty fork it; `--mtag-mt 1` to queue.

```yaml
[/inc]
  /mnt/inc
  accs:
    w: *
  flags:
    e2d, e2t          # index uploads + tags
    mte: +x1          # append tag x1 to index list
    mtp: x1=ad,kn,/usr/bin/notify-send   # provide tag x1 for any type (ad), no kill, run notify-send
```

Runs `notify-send <path>` on upload. Equivalent event-hook form:
`-e2d --xau notify-send,hello,--`.

## Handlers

Redefine 404/403 behavior with plugins (`bin/handlers/`). Client-side UI/UX
plugins in `contrib/plugins/`.

## IP auth

`--ipu 192.168.123.0/24=spartacus` auto-logs that CIDR in as user `spartacus`.
