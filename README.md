# docknv - Docker with environments

> One entry-point, multiple deployments

Using `docknv` you can manage any kind of Docker projects to:

- Handle multiple service, network and volume groups (called *schemas*)
- Handle multiple environments depending on context and configuration
- Handle multiple namespaces to deploy multiple Compose stacks concurrently
- Easily manage your local images for your project
- Use flexible custom commands dedicated to your project

## Installation

Quick install:

```bash
git clone https://bitbucket.org/sharingcloud/docknv.git
pip install --upgrade -e ./docknv   # or sudo

# Extra step on Windows
pip install -r requirements-win.txt
```

## Documentation

You can build the documentation in the `docs/` folder.

## Tests

To execute tests, install `tox`:

```bash
pip install tox
```

Then, execute `tox`.
