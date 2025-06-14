#!/usr/bin/env python3
"""
Template Manager Module

Loads and renders templates for documentation generation.
"""

import os
import re
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class TemplateManager:
    """Manager for loading and rendering templates."""

    def __init__(self, templates_dir: Optional[str] = None):
        """Initialize with optional templates directory."""
        if templates_dir:
            self.templates_dir = templates_dir
        else:
            # Default to templates directory in the same folder as this script
            self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context."""
        template_path = os.path.join(self.templates_dir, f"{template_name}.html")

        try:
            with open(template_path, "r") as f:
                template_content = f.read()

            # Simple variable substitution
            for key, value in context.items():
                # Handle simple string replacements
                template_content = template_content.replace("{{ " + key + " }}", str(value))

                # Handle filters
                pattern = r"\{\{\s*" + re.escape(key) + r"\s*\|\s*([a-zA-Z_]+)\s*\}\}"
                matches = re.findall(pattern, template_content)

                for filter_name in matches:
                    filtered_value = self._apply_filter(value, filter_name)
                    template_content = template_content.replace(
                        f"{{ {key} | {filter_name} }}",
                        filtered_value
                    )

            return template_content
        except FileNotFoundError:
            raise ValueError(f"Template '{template_name}' not found in {self.templates_dir}")

    def _apply_filter(self, value: Any, filter_name: str) -> str:
        """Apply a filter to the value."""
        if filter_name == "replace" and isinstance(value, str):
            # Replace spaces with plus signs (for URLs)
            return value.replace(" ", "+")
        elif filter_name == "date" and isinstance(value, datetime):
            # Format date
            return value.strftime("%Y-%m-%d")
        elif filter_name == "upper" and isinstance(value, str):
            # Convert to uppercase
            return value.upper()
        elif filter_name == "lower" and isinstance(value, str):
            # Convert to lowercase
            return value.lower()

        # Default: return as string
        return str(value)

    def list_templates(self) -> Dict[str, str]:
        """List available templates with descriptions."""
        templates = {}

        # Get all .html files in the templates directory
        for file_path in Path(self.templates_dir).glob("*.html"):
            template_name = file_path.stem

            # Extract the first line as a description
            try:
                with open(file_path, "r") as f:
                    first_line = f.readline().strip()
                    # If the first line is an HTML comment, use it as description
                    if first_line.startswith("<!--") and first_line.endswith("-->"):
                        description = first_line[4:-3].strip()
                    else:
                        description = f"Template: {template_name}"
            except Exception:
                description = f"Template: {template_name}"

            templates[template_name] = description

        return templates
