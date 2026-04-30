# Pyxel Web build

Run from the repository root:

```bash
tools/build_web.sh
```

Outputs:

- `web/index.html`
- `web/pyxel-rogue.pyxapp`

Check that the tracked web build is current:

```bash
tools/check_web_build.sh
```

Publish the generated build to the `gh-pages` branch:

```bash
tools/deploy_pages.sh
```
