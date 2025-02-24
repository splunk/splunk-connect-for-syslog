from pathlib import Path

import jinja2


def template_generator(template_path: Path, **kwargs) -> str:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path.parent),
        autoescape=False,
    )
    template = env.get_template(template_path.name)
    return template.render(**kwargs)
