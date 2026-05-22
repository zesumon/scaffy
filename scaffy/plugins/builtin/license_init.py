"""Plugin that generates a LICENSE file based on the chosen license type."""

from __future__ import annotations

import datetime
from pathlib import Path

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register

LICENSE_TEMPLATES: dict[str, str] = {
    "mit": """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
    "apache2": """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright {year} {author}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
""",
    "gpl3": """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) {year} {author}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
""",
}


class LicenseInitPlugin(BasePlugin):
    name = "license_init"

    def run(self, context: dict) -> None:
        output_dir = Path(context.get("output_dir", "."))
        variables = context.get("variables", {})
        license_type = variables.get("license", "mit").lower()
        author = variables.get("author", "Unknown Author")
        year = str(datetime.date.today().year)

        template = LICENSE_TEMPLATES.get(license_type)
        if template is None:
            raise PluginError(
                f"[license_init] Unknown license type '{license_type}'. "
                f"Available: {', '.join(LICENSE_TEMPLATES)}"
            )

        license_text = template.format(year=year, author=author)
        license_path = output_dir / "LICENSE"
        license_path.write_text(license_text, encoding="utf-8")
        print(f"[license_init] Created {license_path} ({license_type.upper()})")


register(LicenseInitPlugin)
